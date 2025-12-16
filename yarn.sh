#!/usr/bin/env bash
set -euo pipefail

##############################################
# CONFIG
##############################################

ROLE="${1:-master}"   # "master" or "worker"

HADOOP_VERSION="3.3.6"
SPARK_VERSION="3.3.2"

INSTALL_DIR="/opt"
HADOOP_HOME="${INSTALL_DIR}/hadoop"
SPARK_HOME="${INSTALL_DIR}/spark"

HADOOP_TGZ="https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"
SPARK_TGZ="https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz"

# HDFS dirs
NN_DIR="/data/nn"
DN_DIR="/data/dn"

# cluster hostnames
MASTER_HOST="master"
WORKER_HOSTS=("worker1" "worker2")

##############################################
# Helpers
##############################################

log() { echo "[`date +%H:%M:%S`] $*"; }

install_packages_rhel9() {
  log "Installing base packages (RHEL 9)..."
  if command -v dnf &>/dev/null; then
    dnf install -y java-11-openjdk java-11-openjdk-devel wget openssh-clients rsync tar
  elif command -v yum &>/dev/null; then
    yum install -y java-11-openjdk java-11-openjdk-devel wget openssh-clients rsync tar
  else
    log "ERROR: No dnf/yum found. Install Java + wget + ssh manually."
    exit 1
  fi
}

detect_java_home() {
  if ! command -v java &>/dev/null; then
    log "ERROR: java not found even after install. Check Java installation."
    exit 1
  fi

  local java_bin
  java_bin="$(readlink -f "$(which java)")"
  local java_home
  java_home="$(dirname "$(dirname "$java_bin")")"
  echo "$java_home"
}

setup_env_file() {
  local java_home="$1"
  log "Configuring /etc/profile.d/bigdata.sh with JAVA_HOME=${java_home} ..."
  cat >/etc/profile.d/bigdata.sh <<EOF
export JAVA_HOME=${java_home}
export HADOOP_HOME=${HADOOP_HOME}
export SPARK_HOME=${SPARK_HOME}
export HADOOP_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$SPARK_HOME/bin:\$SPARK_HOME/sbin
EOF

  # shellcheck source=/dev/null
  source /etc/profile.d/bigdata.sh || true
}

install_hadoop() {
  if [ -d "${HADOOP_HOME}" ]; then
    log "Hadoop already installed at ${HADOOP_HOME}, skipping download."
    return
  fi

  log "Downloading and installing Hadoop ${HADOOP_VERSION}..."
  mkdir -p "${INSTALL_DIR}"
  cd "${INSTALL_DIR}"

  wget -q "${HADOOP_TGZ}" -O "hadoop-${HADOOP_VERSION}.tar.gz"
  tar -xzf "hadoop-${HADOOP_VERSION}.tar.gz"
  mv "hadoop-${HADOOP_VERSION}" "${HADOOP_HOME}"
}

install_spark() {
  if [ -d "${SPARK_HOME}" ]; then
    log "Spark already installed at ${SPARK_HOME}, skipping download."
    return
  fi

  log "Downloading and installing Spark ${SPARK_VERSION}..."
  mkdir -p "${INSTALL_DIR}"
  cd "${INSTALL_DIR}"

  wget -q "${SPARK_TGZ}" -O "spark-${SPARK_VERSION}-bin-hadoop3.tgz"
  tar -xzf "spark-${SPARK_VERSION}-bin-hadoop3.tgz"
  mv "spark-${SPARK_VERSION}-bin-hadoop3" "${SPARK_HOME}"
}

configure_hadoop() {
  log "Configuring Hadoop core-site.xml, hdfs-site.xml, yarn-site.xml, mapred-site.xml..."

  mkdir -p "${HADOOP_HOME}/etc/hadoop"

  # core-site.xml
  cat >"${HADOOP_HOME}/etc/hadoop/core-site.xml" <<EOF
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://${MASTER_HOST}:9000</value>
  </property>
</configuration>
EOF

  # hdfs-site.xml
  mkdir -p "${NN_DIR}" "${DN_DIR}"

  cat >"${HADOOP_HOME}/etc/hadoop/hdfs-site.xml" <<EOF
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>2</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:${NN_DIR}</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:${DN_DIR}</value>
  </property>
</configuration>
EOF

  # yarn-site.xml
  cat >"${HADOOP_HOME}/etc/hadoop/yarn-site.xml" <<EOF
<configuration>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>${MASTER_HOST}</value>
  </property>

  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
</configuration>
EOF

  # mapred-site.xml
  if [ -f "${HADOOP_HOME}/etc/hadoop/mapred-site.xml.template" ]; then
    cp "${HADOOP_HOME}/etc/hadoop/mapred-site.xml.template" \
       "${HADOOP_HOME}/etc/hadoop/mapred-site.xml"
  fi

  cat >"${HADOOP_HOME}/etc/hadoop/mapred-site.xml" <<EOF
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
</configuration>
EOF

  # workers file (only on master)
  if [ "${ROLE}" = "master" ]; then
    log "Writing workers file ..."
    {
      for w in "${WORKER_HOSTS[@]}"; do
        echo "$w"
      done
    } > "${HADOOP_HOME}/etc/hadoop/workers"
  fi
}

configure_spark() {
  log "Configuring Spark for YARN..."

  cd "${SPARK_HOME}/conf"

  [ -f spark-env.sh ] || cp spark-env.sh.template spark-env.sh
  [ -f spark-defaults.conf ] || cp spark-defaults.conf.template spark-defaults.conf

  # Detect Java home again for Spark env (just to be safe)
  local java_home
  java_home="$(detect_java_home)"

  # spark-env.sh
  cat > spark-env.sh <<EOF
export JAVA_HOME=${java_home}
export HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop
export YARN_CONF_DIR=${HADOOP_HOME}/etc/hadoop
EOF

  # spark-defaults.conf
  cat > spark-defaults.conf <<EOF
spark.master                     yarn
spark.submit.deployMode          client

spark.executor.instances         2
spark.executor.memory            2g
spark.executor.cores             2
spark.driver.memory              1g
spark.app.name                   SparkOnYarnDefaultApp
EOF
}

##############################################
# MAIN
##############################################

log "Starting setup for ROLE = ${ROLE} on RHEL 9..."

install_packages_rhel9

JAVA_HOME_DETECTED="$(detect_java_home)"
log "Detected JAVA_HOME = ${JAVA_HOME_DETECTED}"

setup_env_file "${JAVA_HOME_DETECTED}"
install_hadoop
install_spark
configure_hadoop
configure_spark

log "Setup completed on this node (${ROLE})."

cat <<EOF

Next manual steps:

1) Run this script on ALL nodes:

   On master:
     ./setup_spark_yarn_rhel9.sh master

   On workers:
     ./setup_spark_yarn_rhel9.sh worker

2) (Optional but recommended) Configure passwordless SSH from master to workers
   if you want 'start-dfs.sh' and 'start-yarn.sh' to auto-SSH:
     ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -N ""
     ssh-copy-id root@worker1
     ssh-copy-id root@worker2

3) On MASTER ONLY (first time):
     hdfs namenode -format

4) On MASTER (to start HDFS + YARN):
     start-dfs.sh
     start-yarn.sh

5) Check daemons with:
     jps

6) Test Spark on YARN from MASTER:
     spark-shell --master yarn --deploy-mode client
     scala> sc.parallelize(1 to 1000).sum()

EOF
