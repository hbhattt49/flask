#!/bin/bash
# ========================================================================
# Spark + Hadoop YARN Bootstrap Script (RHEL 9)
#
# - Run on MASTER  → installs + formats + starts cluster
# - Run on WORKER  → installs + joins existing cluster
#
# Hadoop 3.3.6 | Spark 3.3.2 | Python 3.10 | Java 11
# ROOT USER ONLY
#
# Usage:
#   ./bootstrap_spark_yarn_rhel9.sh <MASTER_IP>
#
# ========================================================================

set -euo pipefail
trap 'echo -e "\033[0;31m[ERROR]\033[0m Failed at line $LINENO"; exit 1' ERR

# ------------------------------------------------------------------------
# Root check
# ------------------------------------------------------------------------
if [[ $EUID -ne 0 ]]; then
  echo "ERROR: Run as root"
  exit 1
fi

# ------------------------------------------------------------------------
# Args
# ------------------------------------------------------------------------
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <MASTER_IP>"
  exit 1
fi

MASTER_IP="$1"
CURRENT_IP="$(hostname -I | awk '{print $1}')"

if [[ "$CURRENT_IP" == "$MASTER_IP" ]]; then
  NODE_ROLE="master"
else
  NODE_ROLE="worker"
fi

# ------------------------------------------------------------------------
# Versions
# ------------------------------------------------------------------------
HADOOP_VERSION="3.3.6"
SPARK_VERSION="3.3.2"
PYTHON_VERSION="3.10.13"

INSTALL_DIR="/opt"
HADOOP_HOME="/opt/hadoop"
SPARK_HOME="/opt/spark"

HDFS_NAMENODE_DIR="/data/hadoop/namenode"
HDFS_DATANODE_DIR="/data/hadoop/datanode"
HDFS_TMP_DIR="/data/hadoop/tmp"

# ------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err()  { echo -e "${RED}[ERROR]${NC} $1"; }

safe_source() {
  set +u
  export BASHRCSOURCED=1
  source "$1"
  set -u
}

# ------------------------------------------------------------------------
# Install base packages
# ------------------------------------------------------------------------
install_prereqs() {
  log "Installing system prerequisites"
  dnf -y makecache
  dnf install -y wget curl rsync net-tools vim \
                 java-11-openjdk java-11-openjdk-devel \
                 gcc gcc-c++ make \
                 openssl-devel zlib-devel bzip2-devel \
                 readline-devel sqlite-devel ncurses-devel \
                 libffi-devel xz-devel
}

# ------------------------------------------------------------------------
# Detect JAVA_HOME
# ------------------------------------------------------------------------
detect_java() {
  export JAVA_HOME="$(dirname $(dirname $(readlink -f $(which javac))))"
  log "JAVA_HOME=$JAVA_HOME"
}

# ------------------------------------------------------------------------
# Install Python
# ------------------------------------------------------------------------
install_python() {
  if command -v python3.10 >/dev/null; then
    log "Python already installed"
    return
  fi

  cd /tmp
  wget -q https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
  tar -xzf Python-${PYTHON_VERSION}.tgz
  cd Python-${PYTHON_VERSION}
  ./configure --enable-optimizations --with-ensurepip=install
  make -j$(nproc)
  make altinstall

  ln -sf /usr/local/bin/python3.10 /usr/bin/python3.10
  ln -sf /usr/local/bin/pip3.10 /usr/bin/pip3.10
}

# ------------------------------------------------------------------------
# Python deps
# ------------------------------------------------------------------------
install_python_deps() {
  python3.10 -m pip install --upgrade pip
  python3.10 -m pip install numpy==1.24.3 pandas==2.0.3 pyspark==3.3.2 py4j==0.10.9.5
}

# ------------------------------------------------------------------------
# Install Hadoop
# ------------------------------------------------------------------------
install_hadoop() {
  [[ -d $HADOOP_HOME ]] && return
  cd /tmp
  wget  https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz
  tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /opt
  mv /opt/hadoop-${HADOOP_VERSION} $HADOOP_HOME
  mkdir -p $HDFS_TMP_DIR $HDFS_DATANODE_DIR $HDFS_NAMENODE_DIR
}

# ------------------------------------------------------------------------
# Install Spark
# ------------------------------------------------------------------------
install_spark() {
  [[ -d $SPARK_HOME ]] && return
  cd /tmp
  wget https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz
  tar -xzf spark-${SPARK_VERSION}-bin-hadoop3.tgz -C /opt
  mv /opt/spark-${SPARK_VERSION}-bin-hadoop3 $SPARK_HOME
}

# ------------------------------------------------------------------------
# Environment
# ------------------------------------------------------------------------
configure_env() {
  detect_java
  cat >> /root/.bashrc <<EOF

# Hadoop + Spark
export JAVA_HOME=${JAVA_HOME}
export HADOOP_HOME=${HADOOP_HOME}
export HADOOP_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export YARN_HOME=\$HADOOP_HOME
export SPARK_HOME=${SPARK_HOME}
export PYSPARK_PYTHON=/usr/local/bin/python3.10
export PATH=\$JAVA_HOME/bin:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$SPARK_HOME/bin:\$PATH
EOF
  safe_source /root/.bashrc

}

# ------------------------------------------------------------------------
# Hadoop config
# ------------------------------------------------------------------------
configure_hadoop() {
  cat > $HADOOP_HOME/etc/hadoop/core-site.xml <<EOF
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://${MASTER_IP}:9000</value>
  </property>
  <property>
    <name>hadoop.tmp.dir</name>
    <value>${HDFS_TMP_DIR}</value>
  </property>
</configuration>
EOF

  cat > $HADOOP_HOME/etc/hadoop/hdfs-site.xml <<EOF
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>2</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file://${HDFS_NAMENODE_DIR}</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file://${HDFS_DATANODE_DIR}</value>
  </property>
</configuration>
EOF

  cat > $HADOOP_HOME/etc/hadoop/yarn-site.xml <<EOF
<configuration>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>${MASTER_IP}</value>
  </property>
</configuration>
EOF
}

# ------------------------------------------------------------------------
# Spark config
# ------------------------------------------------------------------------
configure_spark() {
  mkdir -p $SPARK_HOME/conf
  cat > $SPARK_HOME/conf/spark-env.sh <<EOF
export JAVA_HOME=${JAVA_HOME}
export HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop
EOF
  chmod +x $SPARK_HOME/conf/spark-env.sh
}

# ------------------------------------------------------------------------
# MASTER start
# ------------------------------------------------------------------------
start_master() {
  log "Formatting HDFS (first run only)"
  hdfs namenode -format -force || true

  log "Starting HDFS"
  #start-dfs.sh
  hdfs --daemon start namenode
  hdfs --daemon start secondarynamenode
  yarn --daemon start resourcemanager

  log "Starting YARN"
  start-yarn.sh

  hdfs dfs -mkdir -p /spark-logs || true
  hdfs dfs -chmod 777 /spark-logs || true

  log "MASTER cluster started"
}

# ------------------------------------------------------------------------
# WORKER start
# ------------------------------------------------------------------------
start_worker() {
  log "Starting DataNode"
  hdfs --daemon start datanode

  log "Starting NodeManager"
  yarn --daemon start nodemanager

  log "WORKER joined cluster"
}

# ------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------
log "Node role detected: $NODE_ROLE"
install_prereqs
install_python
install_python_deps
install_hadoop
install_spark
configure_env
configure_hadoop
configure_spark

if [[ "$NODE_ROLE" == "master" ]]; then
  start_master
else
  start_worker
fi

log "Bootstrap completed successfully"
jps
