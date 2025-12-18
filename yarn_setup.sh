#!/usr/bin/env bash
set -euo pipefail

# =========================================================
# Hadoop 3.3.6 + Spark 3.3.2 on YARN (RHEL 9) bootstrap
# - Idempotent download + install to /opt
# - Configures HDFS/YARN + Spark-on-YARN
# - Creates Python venv at /root/pyvenv (for PySpark)
# =========================================================

HADOOP_VER="3.3.6"
SPARK_VER="3.3.2"

# Apache URLs (stable for these exact versions)
HADOOP_TGZ_URL="https://downloads.apache.org/hadoop/common/hadoop-${HADOOP_VER}/hadoop-${HADOOP_VER}.tar.gz"
HADOOP_SHA_URL="${HADOOP_TGZ_URL}.sha512"

SPARK_TGZ_NAME="spark-${SPARK_VER}-bin-hadoop3.tgz"
SPARK_TGZ_URL="https://archive.apache.org/dist/spark/spark-${SPARK_VER}/${SPARK_TGZ_NAME}"
SPARK_SHA_URL="${SPARK_TGZ_URL}.sha512"

# Defaults (override via flags)
ROLE="worker"                 # master|worker
CLUSTER_NAME="hadoop-spark"
NN_HOST="master"              # NameNode host
RM_HOST="master"              # ResourceManager host
WORKERS="worker1 worker2"     # space-separated
DATA_DIR="/data"              # HDFS local storage base
REPL_FACTOR="2"               # dfs.replication
JAVA_HOME_OVERRIDE=""         # optional
OPEN_FW_PORTS="true"          # open firewalld ports (still need AWS SG)

usage() {
  cat <<EOF
Usage:
  bash $0 --role master --nn-host master --rm-host master --workers "worker1 worker2" [--data-dir /data] [--repl 2]
  bash $0 --role worker --nn-host master --rm-host master --workers "worker1 worker2"

Flags:
  --role         master|worker
  --nn-host      NameNode hostname (fs.defaultFS uses this)
  --rm-host      ResourceManager hostname
  --workers      "worker1 worker2 worker3"
  --data-dir     local base dir for HDFS (default: /data)
  --repl         dfs.replication (default: 2)
  --no-fw        don't modify firewalld
  --java-home    set JAVA_HOME explicitly
EOF
}

# -------------------------
# Parse args
# -------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --role) ROLE="$2"; shift 2;;
    --nn-host) NN_HOST="$2"; shift 2;;
    --rm-host) RM_HOST="$2"; shift 2;;
    --workers) WORKERS="$2"; shift 2;;
    --data-dir) DATA_DIR="$2"; shift 2;;
    --repl) REPL_FACTOR="$2"; shift 2;;
    --no-fw) OPEN_FW_PORTS="false"; shift 1;;
    --java-home) JAVA_HOME_OVERRIDE="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

if [[ "$ROLE" != "master" && "$ROLE" != "worker" ]]; then
  echo "ERROR: --role must be master or worker"
  exit 1
fi

# -------------------------
# Helpers
# -------------------------
log() { echo -e "\n[+] $*"; }

detect_java_home() {
  if [[ -n "$JAVA_HOME_OVERRIDE" ]]; then
    echo "$JAVA_HOME_OVERRIDE"
    return
  fi
  local java_bin
  java_bin="$(readlink -f "$(command -v java)")"
  # .../bin/java -> JAVA_HOME = ... (strip /bin/java)
  echo "${java_bin%/bin/java}"
}

download_and_verify_sha512() {
  local url="$1"
  local sha_url="$2"
  local out="$3"

  if [[ -f "$out" ]]; then
    log "Already downloaded: $out"
    return
  fi

  log "Downloading: $url"
  curl -fL --retry 5 --retry-delay 2 -o "$out" "$url"

  log "Downloading SHA512: $sha_url"
  local sha_file="${out}.sha512"
  curl -fL --retry 5 --retry-delay 2 -o "$sha_file" "$sha_url"

  # sha file format: "<hash>  <filename>"
  local expected
  expected="$(awk '{print $1}' "$sha_file" | head -n1)"
  local actual
  actual="$(sha512sum "$out" | awk '{print $1}')"

  if [[ "$expected" != "$actual" ]]; then
    echo "ERROR: SHA512 mismatch for $out"
    echo "Expected: $expected"
    echo "Actual:   $actual"
    exit 1
  fi

  log "SHA512 OK: $out"
}

ensure_packages() {
  log "Installing OS packages"
  dnf -y install \
    java-11-openjdk java-11-openjdk-devel \
    python3 python3-pip \
    curl wget tar gzip rsync which \
    openssh-clients openssh-server \
    firewalld || true

  systemctl enable --now sshd || true
}

install_hadoop() {
  local base="/opt"
  local tgz="/tmp/hadoop-${HADOOP_VER}.tar.gz"
  local dir="${base}/hadoop-${HADOOP_VER}"
  local link="${base}/hadoop"

  if [[ -d "$dir" ]]; then
    log "Hadoop already installed at $dir"
  else
    download_and_verify_sha512 "$HADOOP_TGZ_URL" "$HADOOP_SHA_URL" "$tgz"
    log "Extracting Hadoop to $base"
    tar -xzf "$tgz" -C "$base"
  fi

  ln -sfn "$dir" "$link"
}

install_spark() {
  local base="/opt"
  local tgz="/tmp/${SPARK_TGZ_NAME}"
  local dir="${base}/spark-${SPARK_VER}-bin-hadoop3"
  local link="${base}/spark"

  if [[ -d "$dir" ]]; then
    log "Spark already installed at $dir"
  else
    download_and_verify_sha512 "$SPARK_TGZ_URL" "$SPARK_SHA_URL" "$tgz"
    log "Extracting Spark to $base"
    tar -xzf "$tgz" -C "$base"
  fi

  ln -sfn "$dir" "$link"
}

setup_python_venv() {
  log "Setting up Python venv at /root/pyvenv"
  if [[ ! -d /root/pyvenv ]]; then
    python3 -m venv /root/pyvenv
  fi
  /root/pyvenv/bin/pip install -U pip wheel setuptools
  # Packages your sample needs
  /root/pyvenv/bin/pip install -U numpy pandas
}

write_env_profile() {
  local java_home
  java_home="$(detect_java_home)"

  log "Writing /etc/profile.d/hadoop_spark.sh"
  cat >/etc/profile.d/hadoop_spark.sh <<EOF
export JAVA_HOME="${java_home}"
export HADOOP_HOME="/opt/hadoop"
export HADOOP_CONF_DIR="\$HADOOP_HOME/etc/hadoop"
export YARN_CONF_DIR="\$HADOOP_CONF_DIR"
export SPARK_HOME="/opt/spark"
export PATH="\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$SPARK_HOME/bin:\$SPARK_HOME/sbin"
EOF
}

make_dirs() {
  log "Creating HDFS local dirs under ${DATA_DIR}"
  mkdir -p "${DATA_DIR}/hdfs/namenode" "${DATA_DIR}/hdfs/datanode"
  mkdir -p /var/log/hadoop /var/log/spark
  chmod -R 755 "${DATA_DIR}" /var/log/hadoop /var/log/spark
}

write_hadoop_configs() {
  log "Writing Hadoop configs"
  local conf="/opt/hadoop/etc/hadoop"

  # workers file used by some scripts; still useful
  printf "%s\n" ${WORKERS} > "${conf}/workers"

  cat > "${conf}/core-site.xml" <<EOF
<?xml version="1.0"?>
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://${NN_HOST}:8020</value>
  </property>
  <property>
    <name>hadoop.tmp.dir</name>
    <value>${DATA_DIR}/hadoop-tmp</value>
  </property>
</configuration>
EOF

  cat > "${conf}/hdfs-site.xml" <<EOF
<?xml version="1.0"?>
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>${REPL_FACTOR}</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file://${DATA_DIR}/hdfs/namenode</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file://${DATA_DIR}/hdfs/datanode</value>
  </property>
  <property>
    <name>dfs.permissions.enabled</name>
    <value>false</value>
  </property>
</configuration>
EOF

  cat > "${conf}/yarn-site.xml" <<EOF
<?xml version="1.0"?>
<configuration>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>${RM_HOST}</value>
  </property>

  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>

  <!-- Basic resource settings (tune per instance type) -->
  <property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>8192</value>
  </property>
  <property>
    <name>yarn.nodemanager.resource.cpu-vcores</name>
    <value>4</value>
  </property>

  <property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value>
  </property>
</configuration>
EOF

  cat > "${conf}/mapred-site.xml" <<EOF
<?xml version="1.0"?>
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
</configuration>
EOF

  # hadoop-env.sh: ensure JAVA_HOME is set
  local java_home
  java_home="$(detect_java_home)"
  if ! grep -q '^export JAVA_HOME=' "${conf}/hadoop-env.sh"; then
    echo "export JAVA_HOME=${java_home}" >> "${conf}/hadoop-env.sh"
  fi
}

write_spark_configs() {
  log "Writing Spark configs"
  local conf="/opt/spark/conf"
  mkdir -p "$conf"

  # spark-env
  cat > "${conf}/spark-env.sh" <<EOF
#!/usr/bin/env bash
export JAVA_HOME="$(detect_java_home)"
export HADOOP_CONF_DIR="/opt/hadoop/etc/hadoop"
export YARN_CONF_DIR="/opt/hadoop/etc/hadoop"
EOF
  chmod +x "${conf}/spark-env.sh"

  # spark-defaults
  cat > "${conf}/spark-defaults.conf" <<EOF
spark.master                      yarn
spark.submit.deployMode           cluster
spark.eventLog.enabled            true
spark.eventLog.dir                hdfs:///spark-history
spark.history.fs.logDirectory     hdfs:///spark-history
spark.sql.execution.arrow.pyspark.enabled false
EOF

  # Optional: keep spark logs local too
  cat > "${conf}/log4j2.properties" <<'EOF'
rootLogger.level = INFO
rootLogger.appenderRef.stdout.ref = console
appender.console.type = Console
appender.console.name = console
appender.console.layout.type = PatternLayout
appender.console.layout.pattern = %d{ISO8601} %p %c{1.} [%t] %m%n
EOF
}

open_firewalld_ports() {
  [[ "$OPEN_FW_PORTS" == "true" ]] || return 0

  log "Configuring firewalld (you still must open AWS Security Group ports)"
  systemctl enable --now firewalld || true

  # Common ports (adjust as needed)
  # HDFS: 8020, 9870 (NN UI), 9864 (DN UI)
  # YARN: 8030-8033 (RM), 8088 (RM UI), 8042 (NM UI)
  # Spark: 18080 (history server)
  firewall-cmd --permanent --add-port=22/tcp || true

  if [[ "$ROLE" == "master" ]]; then
    for p in 8020 9870 8030 8031 8032 8033 8088 18080; do
      firewall-cmd --permanent --add-port=${p}/tcp || true
    done
  fi

  # Worker ports
  for p in 9864 8042; do
    firewall-cmd --permanent --add-port=${p}/tcp || true
  done

  firewall-cmd --reload || true
}

write_systemd_units() {
  log "Creating systemd units for Hadoop/YARN (local daemons; no ssh fan-out)"
  mkdir -p /etc/hadoop

  cat > /etc/hadoop/hadoop-env <<EOF
JAVA_HOME=$(detect_java_home)
HADOOP_HOME=/opt/hadoop
HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
YARN_CONF_DIR=/opt/hadoop/etc/hadoop
EOF

  # NameNode (master only)
  cat > /etc/systemd/system/hdfs-namenode.service <<'EOF'
[Unit]
Description=HDFS NameNode
After=network.target

[Service]
Type=forking
EnvironmentFile=/etc/hadoop/hadoop-env
ExecStart=/opt/hadoop/sbin/hadoop-daemon.sh start namenode
ExecStop=/opt/hadoop/sbin/hadoop-daemon.sh stop namenode
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

  # DataNode (all nodes)
  cat > /etc/systemd/system/hdfs-datanode.service <<'EOF'
[Unit]
Description=HDFS DataNode
After=network.target

[Service]
Type=forking
EnvironmentFile=/etc/hadoop/hadoop-env
ExecStart=/opt/hadoop/sbin/hadoop-daemon.sh start datanode
ExecStop=/opt/hadoop/sbin/hadoop-daemon.sh stop datanode
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

  # ResourceManager (master only)
  cat > /etc/systemd/system/yarn-resourcemanager.service <<'EOF'
[Unit]
Description=YARN ResourceManager
After=network.target

[Service]
Type=forking
EnvironmentFile=/etc/hadoop/hadoop-env
ExecStart=/opt/hadoop/sbin/yarn-daemon.sh start resourcemanager
ExecStop=/opt/hadoop/sbin/yarn-daemon.sh stop resourcemanager
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

  # NodeManager (all nodes)
  cat > /etc/systemd/system/yarn-nodemanager.service <<'EOF'
[Unit]
Description=YARN NodeManager
After=network.target

[Service]
Type=forking
EnvironmentFile=/etc/hadoop/hadoop-env
ExecStart=/opt/hadoop/sbin/yarn-daemon.sh start nodemanager
ExecStop=/opt/hadoop/sbin/yarn-daemon.sh stop nodemanager
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

  # Spark History Server (master only; optional but useful)
  cat > /etc/systemd/system/spark-historyserver.service <<'EOF'
[Unit]
Description=Spark History Server
After=network.target

[Service]
Type=forking
Environment="SPARK_HOME=/opt/spark"
Environment="JAVA_HOME=/usr"
ExecStart=/opt/spark/sbin/start-history-server.sh
ExecStop=/opt/spark/sbin/stop-history-server.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
}

format_namenode_if_needed() {
  if [[ "$ROLE" != "master" ]]; then
    return 0
  fi

  # NameNode format guard
  if [[ -f "${DATA_DIR}/hdfs/namenode/current/VERSION" ]]; then
    log "NameNode already formatted (VERSION exists) - skipping format"
  else
    log "Formatting NameNode (first time only)"
    /opt/hadoop/bin/hdfs namenode -format -nonInteractive "${CLUSTER_NAME}"
  fi
}

start_services() {
  log "Enabling + starting services for role=$ROLE"

  # DataNode + NodeManager everywhere
  systemctl enable --now hdfs-datanode yarn-nodemanager

  if [[ "$ROLE" == "master" ]]; then
    systemctl enable --now hdfs-namenode yarn-resourcemanager
  fi
}

create_hdfs_dirs_for_spark() {
  if [[ "$ROLE" != "master" ]]; then
    return 0
  fi

  log "Creating HDFS dirs for Spark event logs (spark-history)"
  /opt/hadoop/bin/hdfs dfs -mkdir -p /spark-history || true
  /opt/hadoop/bin/hdfs dfs -chmod 1777 /spark-history || true
}

print_next_steps() {
  cat <<EOF

=========================================================
DONE on this node.
Role: ${ROLE}
Hadoop: /opt/hadoop  (hadoop-${HADOOP_VER})
Spark : /opt/spark   (spark-${SPARK_VER}-bin-hadoop3)
Python venv: /root/pyvenv
=========================================================

Web UIs (ensure AWS SG allows these):
- NameNode UI:      http://${NN_HOST}:9870  (master)
- YARN RM UI:       http://${RM_HOST}:8088  (master)
- NodeManager UI:   http://<worker>:8042
- Spark History UI: http://${RM_HOST}:18080 (after jobs run)

PySpark (cluster mode) best practice:
- Package /root/pyvenv and ship to YARN using --archives
Example:

  tar -czf /root/pyvenv.tgz -C /root pyvenv

  /opt/spark/bin/spark-submit \\
    --master yarn \\
    --deploy-mode cluster \\
    --name IrisSample \\
    --num-executors 2 \\
    --executor-cores 1 \\
    --executor-memory 1g \\
    --conf spark.yarn.am.memory=1g \\
    --conf spark.yarn.am.cores=1 \\
    --archives /root/pyvenv.tgz#pyenv \\
    --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=pyenv/pyvenv/bin/python \\
    --conf spark.executorEnv.PYSPARK_PYTHON=pyenv/pyvenv/bin/python \\
    /root/iris_sample.py

Logs:
  yarn logs -applicationId <appId>

=========================================================
EOF
}

# -------------------------
# Main
# -------------------------
ensure_packages
install_hadoop
install_spark
setup_python_venv
write_env_profile
make_dirs
write_hadoop_configs
write_spark_configs
open_firewalld_ports
write_systemd_units
format_namenode_if_needed
start_services

# On master, wait a moment and create HDFS dirs for Spark
if [[ "$ROLE" == "master" ]]; then
  sleep 3
  create_hdfs_dirs_for_spark
  systemctl enable --now spark-historyserver || true
fi

print_next_steps
