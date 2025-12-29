#!/bin/bash
# ============================================================
# Hadoop 3.3.6 + Spark 3.3.2 Bootstrap (ROOT ONLY)
# Dynamic workers | RHEL 9 | CapacityScheduler fixed
# ============================================================

set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <MASTER_IP>"
  exit 1
fi
# ---------- CONFIG ----------
MASTER_IP=$1

HADOOP_VERSION="3.3.6"
SPARK_VERSION="3.3.2"

INSTALL_DIR="/opt"
HADOOP_HOME="$INSTALL_DIR/hadoop"
SPARK_HOME="$INSTALL_DIR/spark"

DATA_DIR="/data"
HDFS_NN="$DATA_DIR/hdfs/namenode"
HDFS_DN="$DATA_DIR/hdfs/datanode"
YARN_LOCAL="$DATA_DIR/yarn/local"
YARN_LOGS="$DATA_DIR/yarn/logs"

# ---------- SAFETY ----------
if [[ $EUID -ne 0 ]]; then
  echo "Run as root only"
  exit 1
fi

THIS_IP=$(hostname -I | awk '{print $1}')
ROLE="worker"
[[ "$THIS_IP" == "$MASTER_IP" ]] && ROLE="master"

echo "========================================="
echo "BOOTSTRAP START"
echo "Role: $ROLE"
echo "IP:   $THIS_IP"
echo "========================================="

# ---------- SYSTEM ----------
dnf -y install java-11-openjdk java-11-openjdk-devel wget curl rsync net-tools \
               python3 python3-pip openssh-clients openssh-server
pip install pandas numpy pyspark==3.3.2
systemctl enable --now sshd

JAVA_HOME=$(dirname $(dirname $(readlink -f $(which javac))))

# ---------- DIRECTORIES ----------
mkdir -p \
  "$HDFS_NN" "$HDFS_DN" \
  "$YARN_LOCAL" "$YARN_LOGS" \
  /var/run/hadoop

chmod -R 777 "$DATA_DIR"

# ---------- DOWNLOAD ----------
cd /tmp

if [[ ! -d "$HADOOP_HOME" ]]; then
  wget -q https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
  tar -xzf hadoop-$HADOOP_VERSION.tar.gz
  mv hadoop-$HADOOP_VERSION "$HADOOP_HOME"
fi

if [[ ! -d "$SPARK_HOME" ]]; then
  wget -q https://archive.apache.org/dist/spark/spark-$SPARK_VERSION/spark-$SPARK_VERSION-bin-hadoop3.tgz
  tar -xzf spark-$SPARK_VERSION-bin-hadoop3.tgz
  mv spark-$SPARK_VERSION-bin-hadoop3 "$SPARK_HOME"
fi

# ---------- ENV ----------
cat >/etc/profile.d/bigdata.sh <<EOF
export JAVA_HOME=$JAVA_HOME
export HADOOP_HOME=$HADOOP_HOME
export SPARK_HOME=$SPARK_HOME
export HADOOP_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=\$HADOOP_HOME/etc/hadoop
export PATH=\$JAVA_HOME/bin:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$SPARK_HOME/bin:\$PATH
EOF

source /etc/profile.d/bigdata.sh

# ---------- HADOOP CONF ----------
cat >$HADOOP_HOME/etc/hadoop/core-site.xml <<EOF
<configuration>
 <property>
  <name>fs.defaultFS</name>
  <value>hdfs://$MASTER_IP:9000</value>
 </property>
</configuration>
EOF

cat >$HADOOP_HOME/etc/hadoop/hdfs-site.xml <<EOF
<configuration>
 <property>
  <name>dfs.replication</name>
  <value>1</value>
 </property>
 <property>
  <name>dfs.namenode.name.dir</name>
  <value>file://$HDFS_NN</value>
 </property>
 <property>
  <name>dfs.datanode.data.dir</name>
  <value>file://$HDFS_DN</value>
 </property>
</configuration>
EOF

cat >$HADOOP_HOME/etc/hadoop/mapred-site.xml <<EOF
<configuration>
 <property>
  <name>mapreduce.framework.name</name>
  <value>yarn</value>
 </property>
</configuration>
EOF

cat >$HADOOP_HOME/etc/hadoop/yarn-site.xml <<EOF
<configuration>

 <property>
  <name>yarn.resourcemanager.hostname</name>
  <value>$MASTER_IP</value>
 </property>

 <property>
  <name>yarn.nodemanager.aux-services</name>
  <value>mapreduce_shuffle</value>
 </property>

 <property>
  <name>yarn.nodemanager.local-dirs</name>
  <value>$YARN_LOCAL</value>
 </property>

 <property>
  <name>yarn.nodemanager.log-dirs</name>
  <value>$YARN_LOGS</value>
 </property>

 <property>
  <name>yarn.nodemanager.vmem-check-enabled</name>
  <value>false</value>
 </property>

 <property>
  <name>yarn.scheduler.capacity.maximum-am-resource-percent</name>
  <value>0.5</value>
 </property>

</configuration>
EOF

# ---------- SPARK CONF ----------
mkdir -p $SPARK_HOME/conf

cat >$SPARK_HOME/conf/spark-env.sh <<EOF
export JAVA_HOME=$JAVA_HOME
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export YARN_CONF_DIR=$HADOOP_HOME/etc/hadoop
EOF
chmod +x $SPARK_HOME/conf/spark-env.sh

cat >$SPARK_HOME/conf/spark-defaults.conf <<EOF
spark.master yarn
spark.submit.deployMode client
spark.executor.memory 2g
spark.executor.cores 2
spark.driver.memory 1g
spark.yarn.am.memory 512m
spark.yarn.am.cores 1
EOF

# ---------- MASTER ----------
if [[ "$ROLE" == "master" ]]; then
  echo "Formatting HDFS (first time only)..."
  hdfs namenode -format -force || true

  start-dfs.sh
  start-yarn.sh

  hdfs dfs -mkdir -p /spark-logs
  hdfs dfs -chmod 777 /spark-logs
fi

# ---------- WORKER ----------
if [[ "$ROLE" == "worker" ]]; then
  yarn --daemon start nodemanager
  hdfs --daemon start datanode
fi

# ---------- DONE ----------
echo "========================================"
echo "BOOTSTRAP COMPLETE"
echo "Role: $ROLE"
echo "Master: $MASTER_IP"
echo "========================================"
