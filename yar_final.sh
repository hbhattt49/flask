#!/bin/bash
# ========================================================================
# Spark YARN Cluster Bootstrap Script (RHEL 9) - Root User Only
# Hadoop 3.3.6 + Spark 3.3.2 + Python 3.10
# For 3-node cluster setup
# ========================================================================
#
# Usage: ./bootstrap_spark_cluster_rhel9.sh <MASTER_IP> <WORKER1_IP> <WORKER2_IP>
# Example: ./bootstrap_spark_cluster_rhel9.sh 172.31.45.253 172.31.19.244 172.31.27.84
#
# ========================================================================

set -euo pipefail

trap 'echo -e "\033[0;31m[ERROR]\033[0m Script failed at line $LINENO"; exit 1' ERR

# ========================================================================
# Check if running as root
# ========================================================================
if [ "${EUID}" -ne 0 ]; then
  echo "ERROR: This script must be run as root"
  echo "Please run: sudo su -"
  echo "Then execute: ./bootstrap_spark_cluster_rhel9.sh <MASTER_IP> <WORKER1_IP> <WORKER2_IP>"
  exit 1
fi

# ========================================================================
# Parse Arguments
# ========================================================================
if [ "$#" -ne 3 ]; then
  echo "ERROR: Invalid number of arguments"
  echo "Usage: $0 <MASTER_IP> <WORKER1_IP> <WORKER2_IP>"
  exit 1
fi

MASTER_IP="$1"
WORKER1_IP="$2"
WORKER2_IP="$3"

# ========================================================================
# Configuration Variables
# ========================================================================
HADOOP_VERSION="3.3.6"
SPARK_VERSION="3.3.2"
PYTHON_VERSION="3.10.13"

INSTALL_DIR="/opt"
HADOOP_HOME="${INSTALL_DIR}/hadoop"
SPARK_HOME="${INSTALL_DIR}/spark"

# HDFS directories
HDFS_NAMENODE_DIR="/data/hadoop/namenode"
HDFS_DATANODE_DIR="/data/hadoop/datanode"
HDFS_TMP_DIR="/data/hadoop/tmp"

# Current IP
CURRENT_IP="$(hostname -I | awk '{print $1}')"

# Determine node type based on IP
if [ "$CURRENT_IP" == "$MASTER_IP" ]; then
  NODE_TYPE="master"
  HOSTNAME_NODE="master"
elif [ "$CURRENT_IP" == "$WORKER1_IP" ]; then
  NODE_TYPE="worker"
  HOSTNAME_NODE="worker1"
elif [ "$CURRENT_IP" == "$WORKER2_IP" ]; then
  NODE_TYPE="worker"
  HOSTNAME_NODE="worker2"
else
  echo "ERROR: Current IP ($CURRENT_IP) does not match any provided IPs"
  echo "Master: $MASTER_IP, Worker1: $WORKER1_IP, Worker2: $WORKER2_IP"
  exit 1
fi

# ========================================================================
# Color output functions
# ========================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_section() {
  echo -e "\n${BLUE}========================================${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}========================================${NC}"
}

safe_source() {
  local f="$1"
  # Temporarily disable nounset while sourcing
  set +u
  # Some RHEL bashrc expects this variable
  export BASHRCSOURCED=1
  # shellcheck disable=SC1090
  source "$f"
  set -u
}

# ========================================================================
# Display Configuration
# ========================================================================
display_config() {
  log_section "Cluster Configuration"
  echo "Master IP:   $MASTER_IP"
  echo "Worker1 IP:  $WORKER1_IP"
  echo "Worker2 IP:  $WORKER2_IP"
  echo ""
  echo "Current IP:  $CURRENT_IP"
  echo "Node Type:   $NODE_TYPE"
  echo "Hostname:    $HOSTNAME_NODE"
  echo ""
  echo "Hadoop:      $HADOOP_VERSION"
  echo "Spark:       $SPARK_VERSION"
  echo "Python:      $PYTHON_VERSION"
  echo "Java:        OpenJDK 11"
  log_section ""

  read -r -p "Continue with installation? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    echo "Installation cancelled."
    exit 0
  fi
}

# ========================================================================
# 1. Configure Hostname and Hosts File
# ========================================================================
configure_network() {
  log_section "Configuring Network and Hostname"

  log_info "Setting hostname to: $HOSTNAME_NODE"
  hostnamectl set-hostname "$HOSTNAME_NODE"

  log_info "Configuring /etc/hosts file..."
  cp /etc/hosts "/etc/hosts.backup.$(date +%Y%m%d_%H%M%S)"

  sed -i '/# Spark-Hadoop Cluster/,/# End Spark-Hadoop Cluster/d' /etc/hosts

  cat >> /etc/hosts <<EOF

# Spark-Hadoop Cluster
$MASTER_IP    master
$WORKER1_IP   worker1
$WORKER2_IP   worker2
# End Spark-Hadoop Cluster
EOF

  log_info "Network configuration completed"
  log_info "Testing connectivity..."

  ping -c 1 master >/dev/null 2>&1 && log_info "✓ Can reach master" || log_warn "✗ Cannot reach master"
  ping -c 1 worker1 >/dev/null 2>&1 && log_info "✓ Can reach worker1" || log_warn "✗ Cannot reach worker1"
  ping -c 1 worker2 >/dev/null 2>&1 && log_info "✓ Can reach worker2" || log_warn "✗ Cannot reach worker2"
}

# ========================================================================
# Helper: detect JAVA_HOME on RHEL
# ========================================================================
detect_java_home() {
  if command -v javac >/dev/null 2>&1; then
    JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v javac)")")")"
    export JAVA_HOME
    log_info "Detected JAVA_HOME=$JAVA_HOME"
  else
    log_warn "javac not found yet; JAVA_HOME will be detected after Java install."
  fi
}

# ========================================================================
# 2. Install System Prerequisites (RHEL 9)
# ========================================================================
install_prerequisites() {
  log_section "Installing System Prerequisites (RHEL 9)"

  # Make sure dnf exists
  if ! command -v dnf >/dev/null 2>&1; then
    log_error "dnf not found. Are you sure this is RHEL 9?"
    exit 1
  fi

  dnf -y makecache

  # Basic tooling
  dnf install -y wget curl rsync net-tools vim

  # SSH
  dnf install -y openssh-server openssh-clients
  systemctl enable --now sshd

  # Java 11
  dnf install -y java-11-openjdk java-11-openjdk-devel
  detect_java_home

  # Build tools (build-essential equivalent)
  dnf groupinstall -y "Development Tools" || dnf install -y gcc gcc-c++ make

  # Python build deps
  dnf install -y \
    openssl-devel zlib-devel bzip2-devel readline-devel sqlite-devel \
    ncurses-devel xz xz-devel tk-devel libffi-devel

  # Optional: htop (best-effort)
  if ! dnf install -y htop; then
    log_warn "htop not available in enabled repos. Trying to enable EPEL (best-effort)..."
    dnf install -y epel-release || true
    dnf install -y htop || log_warn "Still cannot install htop; continuing without it."
  fi

  log_info "System prerequisites installed successfully"
}

# ========================================================================
# 3. Configure SSH (keys + config)
# ========================================================================
configure_ssh() {
  log_section "Configuring SSH"

  # Ensure sshd is enabled
  systemctl enable --now sshd

  mkdir -p /root/.ssh
  chmod 700 /root/.ssh

  if [ ! -f /root/.ssh/id_rsa ]; then
    log_info "Generating SSH key..."
    ssh-keygen -t rsa -N "" -f /root/.ssh/id_rsa
  fi

  cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
  chmod 600 /root/.ssh/authorized_keys

  cat > /root/.ssh/config <<EOF
Host master worker1 worker2
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
EOF
  chmod 600 /root/.ssh/config

  log_info "SSH configuration completed"

  if [ "$NODE_TYPE" == "master" ]; then
    log_warn "IMPORTANT: After all nodes finish installation, run on master:"
    echo "  ssh-copy-id root@worker1"
    echo "  ssh-copy-id root@worker2"
  fi
}

# ========================================================================
# 4. Install Python 3.10 (build from source)
# ========================================================================
install_python() {
  log_section "Installing Python $PYTHON_VERSION"

  if command -v python3.10 >/dev/null 2>&1; then
    log_info "Python 3.10 already installed"
    python3.10 --version
    return
  fi

  cd /tmp

  if [ ! -f "Python-${PYTHON_VERSION}.tgz" ]; then
    log_info "Downloading Python ${PYTHON_VERSION}..."
    wget "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz"
  fi

  log_info "Extracting and compiling Python..."
  tar -xzf "Python-${PYTHON_VERSION}.tgz"
  cd "Python-${PYTHON_VERSION}"

  ./configure --enable-optimizations --with-ensurepip=install
  make -j"$(nproc)"
  make altinstall

  ln -sf /usr/local/bin/python3.10 /usr/bin/python3.10
  ln -sf /usr/local/bin/pip3.10 /usr/bin/pip3.10

  python3.10 -m pip install --upgrade pip

  cd /tmp
  rm -rf "Python-${PYTHON_VERSION}" "Python-${PYTHON_VERSION}.tgz"

  log_info "Python ${PYTHON_VERSION} installed successfully"
  python3.10 --version
}

# ========================================================================
# 5. Install Python Dependencies
# ========================================================================
install_python_dependencies() {
  log_section "Installing Python Dependencies"

  python3.10 -m pip install \
    numpy==1.24.3 \
    pandas==2.0.3 \
    pyspark==3.3.2 \
    py4j==0.10.9.5

  log_info "Python dependencies installed successfully"
  python3.10 -m pip list | grep -E "numpy|pandas|pyspark|py4j" || true
}

# ========================================================================
# 6. Install Hadoop
# ========================================================================
install_hadoop() {
  log_section "Installing Hadoop $HADOOP_VERSION"

  if [ -d "${HADOOP_HOME}" ]; then
    log_warn "Hadoop already installed at ${HADOOP_HOME}"
    return
  fi

  cd /tmp

  if [ ! -f "hadoop-${HADOOP_VERSION}.tar.gz" ]; then
    log_info "Downloading Hadoop ${HADOOP_VERSION}..."
    wget "https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"
  fi

  log_info "Extracting Hadoop..."
  tar -xzf "hadoop-${HADOOP_VERSION}.tar.gz" -C "${INSTALL_DIR}/"
  mv "${INSTALL_DIR}/hadoop-${HADOOP_VERSION}" "${HADOOP_HOME}"

  mkdir -p "${HDFS_NAMENODE_DIR}" "${HDFS_DATANODE_DIR}" "${HDFS_TMP_DIR}"
  mkdir -p "${HADOOP_HOME}/logs"
  mkdir -p /var/run/hadoop

  cd /tmp
  rm -f "hadoop-${HADOOP_VERSION}.tar.gz"

  log_info "Hadoop installed successfully at ${HADOOP_HOME}"
}

# ========================================================================
# 7. Install Spark
# ========================================================================
install_spark() {
  log_section "Installing Spark $SPARK_VERSION"

  if [ -d "${SPARK_HOME}" ]; then
    log_warn "Spark already installed at ${SPARK_HOME}"
    return
  fi

  cd /tmp

  if [ ! -f "spark-${SPARK_VERSION}-bin-hadoop3.tgz" ]; then
    log_info "Downloading Spark ${SPARK_VERSION}..."
    wget "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz"
  fi

  log_info "Extracting Spark..."
  tar -xzf "spark-${SPARK_VERSION}-bin-hadoop3.tgz" -C "${INSTALL_DIR}/"
  mv "${INSTALL_DIR}/spark-${SPARK_VERSION}-bin-hadoop3" "${SPARK_HOME}"

  mkdir -p "${SPARK_HOME}/logs"

  cd /tmp
  rm -f "spark-${SPARK_VERSION}-bin-hadoop3.tgz"

  log_info "Spark installed successfully at ${SPARK_HOME}"
}

# ========================================================================
# 8. Configure Environment Variables
# ========================================================================
configure_environment() {
  log_section "Configuring Environment Variables"

  # Ensure JAVA_HOME known now
  detect_java_home
  if [ -z "${JAVA_HOME:-}" ]; then
    log_error "JAVA_HOME could not be detected. Is java-11-openjdk-devel installed?"
    exit 1
  fi

  cp /root/.bashrc "/root/.bashrc.backup.$(date +%Y%m%d_%H%M%S)"
  sed -i '/# Hadoop-Spark Environment/,/# End Hadoop-Spark Environment/d' /root/.bashrc

  cat >> /root/.bashrc <<EOF

# Hadoop-Spark Environment
export JAVA_HOME=${JAVA_HOME}
export HADOOP_HOME=/opt/hadoop
export HADOOP_CONF_DIR=\${HADOOP_HOME}/etc/hadoop
export HADOOP_MAPRED_HOME=\${HADOOP_HOME}
export HADOOP_COMMON_HOME=\${HADOOP_HOME}
export HADOOP_HDFS_HOME=\${HADOOP_HOME}
export YARN_HOME=\${HADOOP_HOME}
export SPARK_HOME=/opt/spark
export PYSPARK_PYTHON=/usr/local/bin/python3.10
export PYSPARK_DRIVER_PYTHON=/usr/local/bin/python3.10
export PATH=\${JAVA_HOME}/bin:\${HADOOP_HOME}/bin:\${HADOOP_HOME}/sbin:\${SPARK_HOME}/bin:\${SPARK_HOME}/sbin:\$PATH
# End Hadoop-Spark Environment
EOF

  # shellcheck disable=SC1090
  #source /root/.bashrc
  safe_source /root/.bashrc

  log_info "Environment variables configured"
}

# ========================================================================
# 9. Configure Hadoop
# ========================================================================
configure_hadoop() {
  log_section "Configuring Hadoop"

  # shellcheck disable=SC1090
  source /root/.bashrc

  cat > "${HADOOP_HOME}/etc/hadoop/hadoop-env.sh" <<EOF
export JAVA_HOME=${JAVA_HOME}
export HADOOP_HOME=${HADOOP_HOME}
export HADOOP_CONF_DIR=\${HADOOP_HOME}/etc/hadoop
export HADOOP_LOG_DIR=\${HADOOP_HOME}/logs
export HADOOP_PID_DIR=/var/run/hadoop
export HADOOP_OPTS="-Djava.net.preferIPv4Stack=true"
EOF

  cat > "${HADOOP_HOME}/etc/hadoop/core-site.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://172.31.45.253:9000</value>
  </property>
  <property>
    <name>hadoop.tmp.dir</name>
    <value>${HDFS_TMP_DIR}</value>
  </property>
  <property>
    <name>io.file.buffer.size</name>
    <value>131072</value>
  </property>
</configuration>
EOF

  cat > "${HADOOP_HOME}/etc/hadoop/hdfs-site.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
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
  <property>
    <name>dfs.namenode.http-address</name>
    <value>172.31.45.253:9870</value>
  </property>
  <property>
    <name>dfs.namenode.secondary.http-address</name>
    <value>172.31.45.253:9868</value>
  </property>
  <property>
    <name>dfs.blocksize</name>
    <value>134217728</value>
  </property>
</configuration>
EOF

  cat > "${HADOOP_HOME}/etc/hadoop/mapred-site.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
  <property>
    <name>mapreduce.application.classpath</name>
    <value>\$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/*:\$HADOOP_MAPRED_HOME/share/hadoop/mapreduce/lib/*</value>
  </property>
  <property>
    <name>yarn.app.mapreduce.am.env</name>
    <value>HADOOP_MAPRED_HOME=\${HADOOP_HOME}</value>
  </property>
  <property>
    <name>mapreduce.map.env</name>
    <value>HADOOP_MAPRED_HOME=\${HADOOP_HOME}</value>
  </property>
  <property>
    <name>mapreduce.reduce.env</name>
    <value>HADOOP_MAPRED_HOME=\${HADOOP_HOME}</value>
  </property>
</configuration>
EOF

  cat > "${HADOOP_HOME}/etc/hadoop/yarn-site.xml" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>172.31.45.253</value>
  </property>
  <property>
    <name>yarn.resourcemanager.address</name>
    <value>172.31.45.253:8032</value>
  </property>
  <property>
    <name>yarn.resourcemanager.scheduler.address</name>
    <value>172.31.45.253:8030</value>
  </property>
  <property>
    <name>yarn.resourcemanager.resource-tracker.address</name>
    <value>172.31.45.253:8031</value>
  </property>
  <property>
    <name>yarn.resourcemanager.webapp.address</name>
    <value>172.31.45.253:8088</value>
  </property>

  <property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>4096</value>
  </property>
  <property>
    <name>yarn.nodemanager.resource.cpu-vcores</name>
    <value>2</value>
  </property>
  <property>
    <name>yarn.scheduler.maximum-allocation-mb</name>
    <value>4096</value>
  </property>
  <property>
    <name>yarn.scheduler.minimum-allocation-mb</name>
    <value>512</value>
  </property>

  <property>
    <name>yarn.nodemanager.vmem-check-enabled</name>
    <value>false</value>
  </property>
  <property>
    <name>yarn.nodemanager.pmem-check-enabled</name>
    <value>false</value>
  </property>
</configuration>
EOF

  cat > "${HADOOP_HOME}/etc/hadoop/workers" <<EOF
worker1
worker2
EOF

  log_info "Hadoop configuration completed"
}

# ========================================================================
# 10. Configure Spark
# ========================================================================
configure_spark() {
  log_section "Configuring Spark"

  # shellcheck disable=SC1090
  source /root/.bashrc

  mkdir -p "${SPARK_HOME}/conf"

  cat > "${SPARK_HOME}/conf/spark-env.sh" <<EOF
export JAVA_HOME=${JAVA_HOME}
export HADOOP_HOME=${HADOOP_HOME}
export SPARK_HOME=${SPARK_HOME}
export HADOOP_CONF_DIR=${HADOOP_HOME}/etc/hadoop
export YARN_CONF_DIR=${HADOOP_HOME}/etc/hadoop
export PYSPARK_PYTHON=/usr/local/bin/python3.10
export PYSPARK_DRIVER_PYTHON=/usr/local/bin/python3.10
export SPARK_DIST_CLASSPATH=\$(${HADOOP_HOME}/bin/hadoop classpath)
EOF
  chmod +x "${SPARK_HOME}/conf/spark-env.sh"

  cat > "${SPARK_HOME}/conf/spark-defaults.conf" <<EOF
spark.master                     yarn
spark.submit.deployMode          client
spark.eventLog.enabled           true
spark.eventLog.dir               hdfs://master:9000/spark-logs
spark.history.fs.logDirectory    hdfs://master:9000/spark-logs
spark.yarn.historyServer.address master:18080
spark.executor.memory            2g
spark.executor.cores             2
spark.driver.memory              1g
spark.serializer                 org.apache.spark.serializer.KryoSerializer
spark.sql.execution.arrow.pyspark.enabled true
spark.sql.execution.arrow.pyspark.fallback.enabled true
spark.yarn.am.memory             512m
spark.yarn.am.cores              1
EOF

  log_info "Spark configuration completed"
}

# ========================================================================
# 11. Format HDFS (Master Only)
# ========================================================================
format_hdfs() {
  if [ "$NODE_TYPE" != "master" ]; then
    log_info "Skipping HDFS format (not master node)"
    return
  fi

  log_section "Formatting HDFS NameNode"
  # shellcheck disable=SC1090
  source /root/.bashrc

  log_warn "Formatting NameNode (this will delete all HDFS data)..."
  "${HADOOP_HOME}/bin/hdfs" namenode -format -force -clusterID sparkcluster

  log_info "HDFS formatted successfully"
}

# ========================================================================
# 12. Start Hadoop Services (Master Only)
# ========================================================================
start_hadoop() {
  if [ "$NODE_TYPE" != "master" ]; then
    log_info "Skipping Hadoop start (not master node)"
    return
  fi

  log_section "Starting Hadoop Services"
  # shellcheck disable=SC1090
  source /root/.bashrc

  log_info "Starting HDFS..."
  "${HADOOP_HOME}/sbin/start-dfs.sh"
  sleep 5

  log_info "Starting YARN..."
  "${HADOOP_HOME}/sbin/start-yarn.sh"
  sleep 10

  log_info "Creating Spark log directory in HDFS..."
  "${HADOOP_HOME}/bin/hdfs" dfs -mkdir -p /spark-logs
  "${HADOOP_HOME}/bin/hdfs" dfs -chmod 777 /spark-logs

  log_info "Hadoop services started successfully"
}

# ========================================================================
# 13. Start Spark History Server (Master Only)
# ========================================================================
start_spark_history() {
  if [ "$NODE_TYPE" != "master" ]; then
    log_info "Skipping Spark History Server (not master node)"
    return
  fi

  log_section "Starting Spark History Server"
  # shellcheck disable=SC1090
  source /root/.bashrc

  "${SPARK_HOME}/sbin/start-history-server.sh"
  log_info "Spark History Server started successfully"
}

# ========================================================================
# 14. Create Test Script
# ========================================================================
create_test_script() {
  log_section "Creating Test Scripts"

  log_info "Creating test_iris.py..."
  cat > /root/test_iris.py <<'EOF'
import numpy as np
import copyreg

def _reduce_dtype(dt):
    return (np.dtype, (dt.str,))
copyreg.pickle(np.dtype, _reduce_dtype)

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, FloatType, StringType
from pyspark.sql.functions import col

spark = SparkSession.builder.appName("IrisSample").getOrCreate()

schema = StructType([
    StructField("sepal_length", FloatType(), True),
    StructField("sepal_width", FloatType(), True),
    StructField("petal_length", FloatType(), True),
    StructField("petal_width", FloatType(), True),
    StructField("label_str", StringType(), True),
])

data = [
    (5.1, 3.5, 1.4, 0.2, "setosa"),
    (4.9, 3.0, 1.4, 0.2, "setosa"),
    (6.2, 3.4, 5.4, 2.3, "virginica"),
    (5.9, 3.0, 5.1, 1.8, "virginica"),
    (5.5, 2.3, 4.0, 1.3, "versicolor"),
    (6.5, 2.8, 4.6, 1.5, "versicolor"),
]

df = spark.createDataFrame(data, schema=schema)

print("Schema:")
df.printSchema()

print("\nClass distribution:")
df.groupBy("label_str").count().show()

df_filtered = df.filter(col("sepal_length") > 5.0)
pdf = df_filtered.toPandas()
print("\nConverted Pandas DataFrame:")
print(pdf.head())

spark.stop()
EOF
  chmod +x /root/test_iris.py

  log_info "Creating run_test.sh..."
  cat > /root/run_test.sh <<'EOF'
#!/bin/bash
set -e
source /root/.bashrc

echo "Running Iris test on Spark YARN cluster..."
echo "==========================================="

spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --num-executors 2 \
  --executor-memory 2G \
  --executor-cores 2 \
  --driver-memory 1G \
  /root/test_iris.py

echo ""
echo "Test completed!"
EOF
  chmod +x /root/run_test.sh

  log_info "Test scripts created successfully"
}

# ========================================================================
# 15. Create Management Scripts
# ========================================================================
create_management_scripts() {
  log_section "Creating Management Scripts"

  cat > /root/start_cluster.sh <<'EOF'
#!/bin/bash
set -e
source /root/.bashrc
echo "Starting Hadoop and Spark services..."
${HADOOP_HOME}/sbin/start-dfs.sh
${HADOOP_HOME}/sbin/start-yarn.sh
${SPARK_HOME}/sbin/start-history-server.sh
echo "Services started!"
jps
EOF
  chmod +x /root/start_cluster.sh

  cat > /root/stop_cluster.sh <<'EOF'
#!/bin/bash
set -e
source /root/.bashrc
echo "Stopping Hadoop and Spark services..."
${SPARK_HOME}/sbin/stop-history-server.sh
${HADOOP_HOME}/sbin/stop-yarn.sh
${HADOOP_HOME}/sbin/stop-dfs.sh
echo "Services stopped!"
EOF
  chmod +x /root/stop_cluster.sh

  cat > /root/cluster_status.sh <<'EOF'
#!/bin/bash
source /root/.bashrc
echo "========================================"
echo "Cluster Status"
echo "========================================"
echo ""
echo "=== Java Processes ==="
jps
echo ""
echo "=== HDFS Health ==="
hdfs dfsadmin -report 2>/dev/null | head -20
echo ""
echo "=== YARN Nodes ==="
yarn node -list 2>/dev/null
echo ""
echo "=== Running Applications ==="
yarn application -list 2>/dev/null
EOF
  chmod +x /root/cluster_status.sh

  log_info "Management scripts created"
}

# ========================================================================
# 16. Verification
# ========================================================================
verify_installation() {
  log_section "Verifying Installation"
  source /root/.bashrc

  echo ""
  log_info "=== Java Version ==="
  java -version 2>&1 | head -3 || true

  echo ""
  log_info "=== Python Version ==="
  python3.10 --version

  echo ""
  log_info "=== Python Packages ==="
  python3.10 -m pip list | grep -E "numpy|pandas|pyspark|py4j" || true

  echo ""
  log_info "=== Hadoop Version ==="
  hadoop version | head -1 || true

  echo ""
  log_info "=== Spark Version ==="
  spark-submit --version 2>&1 | grep -i "version" | head -1 || true

  if [ "$NODE_TYPE" == "master" ]; then
    echo ""
    log_info "=== Java Processes (Master) ==="
    jps || true

    echo ""
    log_info "=== HDFS Report ==="
    hdfs dfsadmin -report 2>/dev/null | head -30 || true
  else
    echo ""
    log_info "=== Java Processes (Worker) ==="
    jps || true
  fi

  echo ""
  log_info "Verification completed"
}

# ========================================================================
# 17. Display Final Information
# ========================================================================
display_final_info() {
  log_section "Installation Complete!"

  echo ""
  echo "Node Type: $NODE_TYPE"
  echo "Hostname:  $HOSTNAME_NODE"
  echo "IP:        $CURRENT_IP"
  echo ""

  if [ "$NODE_TYPE" == "master" ]; then
    echo "=============================================="
    echo "MASTER NODE - IMPORTANT NEXT STEPS"
    echo "=============================================="
    echo ""
    echo "1. Setup SSH keys to workers:"
    echo "   ssh-copy-id root@worker1"
    echo "   ssh-copy-id root@worker2"
    echo ""
    echo "2. Test SSH connectivity:"
    echo "   ssh root@worker1 'hostname'"
    echo "   ssh root@worker2 'hostname'"
    echo ""
    echo "3. Run the test script:"
    echo "   /root/run_test.sh"
    echo ""
    echo "=============================================="
    echo "WEB INTERFACES"
    echo "=============================================="
    echo "HDFS NameNode:        http://$MASTER_IP:9870"
    echo "YARN ResourceManager: http://$MASTER_IP:8088"
    echo "Spark History Server: http://$MASTER_IP:18080"
    echo ""
    echo "=============================================="
    echo "USEFUL COMMANDS"
    echo "=============================================="
    echo "Start cluster:   /root/start_cluster.sh"
    echo "Stop cluster:    /root/stop_cluster.sh"
    echo "Check status:    /root/cluster_status.sh"
    echo "Run test:        /root/run_test.sh"
    echo ""
  else
    echo "=============================================="
    echo "WORKER NODE - Installation Complete"
    echo "=============================================="
    echo ""
    echo "This worker node is ready to join the cluster."
    echo "Expected processes: DataNode, NodeManager"
    echo "Check: jps"
    echo ""
  fi

  echo "=============================================="
  echo "ENVIRONMENT VARIABLES"
  echo "=============================================="
  echo "To use Hadoop and Spark commands, run:"
  echo "  source /root/.bashrc"
  echo ""
}

# ========================================================================
# Main Execution
# ========================================================================
main() {
  clear
  log_section "Spark YARN Cluster Bootstrap Script (RHEL 9)"
  echo "Date: $(date)"
  echo ""

  display_config
  configure_network
  install_prerequisites
  configure_ssh
  install_python
  install_python_dependencies
  install_hadoop
  install_spark
  configure_environment
  configure_hadoop
  configure_spark
  format_hdfs
  start_hadoop
  start_spark_history
  create_test_script
  create_management_scripts
  verify_installation
  display_final_info

  log_info "Bootstrap completed successfully!"
}

main "$@"
