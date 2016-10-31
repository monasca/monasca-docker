#!/bin/bash -x

cat /kafka/config/server.properties.template | sed \
  -e "s|{{ZOOKEEPER_CONNECTION_STRING}}|${ZOOKEEPER_CONNECTION_STRING}|g" \
  -e "s|{{ZOOKEEPER_CHROOT}}|${ZOOKEEPER_CHROOT:-}|g" \
  -e "s|{{KAFKA_BROKER_ID}}|${KAFKA_BROKER_ID:-0}|g" \
  -e "s|{{KAFKA_ADVERTISED_HOST_NAME}}|${KAFKA_ADVERTISED_HOST_NAME:-$IP}|g" \
  -e "s|{{KAFKA_PORT}}|${KAFKA_LISTEN_PORT:-9092}|g" \
  -e "s|{{KAFKA_ADVERTISED_PORT}}|${KAFKA_ADVERTISED_PORT:-9092}|g" \
  -e "s|{{KAFKA_DELETE_TOPIC_ENABLE}}|${KAFKA_DELETE_TOPIC_ENABLE:-false}|g" \
  -e "s|{{ZOOKEEPER_CONNECTION_TIMEOUT_MS}}|${ZOOKEEPER_CONNECTION_TIMEOUT_MS:-10000}|g" \
  -e "s|{{ZOOKEEPER_SESSION_TIMEOUT_MS}}|${ZOOKEEPER_SESSION_TIMEOUT_MS:-10000}|g" \
  -e "s|{{GROUP_MAX_SESSION_TIMEOUT_MS}}|${GROUP_MAX_SESSION_TIMEOUT_MS:-300000}|g" \
   > /kafka/config/server.properties

# Kafka's built-in start scripts set the first three system properties here, but
# we add two more to make remote JMX easier/possible to access in a Docker
# environment:
#
#   1. RMI port - pinning this makes the JVM use a stable one instead of
#      selecting random high ports each time it starts up.
#   2. RMI hostname - normally set automatically by heuristics that may have
#      hard-to-predict results across environments.
#
# These allow saner configuration for firewalls, EC2 security groups, Docker
# hosts running in a VM with Docker Machine, etc. See:
#
# https://issues.apache.org/jira/browse/CASSANDRA-7087
if [ -z $KAFKA_JMX_OPTS ]; then
    KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote=true"
    KAFKA_JMX_OPTS="$KAFKA_JMX_OPTS -Dcom.sun.management.jmxremote.authenticate=false"
    KAFKA_JMX_OPTS="$KAFKA_JMX_OPTS -Dcom.sun.management.jmxremote.ssl=false"
    KAFKA_JMX_OPTS="$KAFKA_JMX_OPTS -Dcom.sun.management.jmxremote.rmi.port=$JMX_PORT"
    KAFKA_JMX_OPTS="$KAFKA_JMX_OPTS -Djava.rmi.server.hostname=${JAVA_RMI_SERVER_HOSTNAME:-$KAFKA_ADVERTISED_HOST_NAME} "
    export KAFKA_JMX_OPTS
fi

function finish {
  cat /kafka/config/server.properties
  cat /kafka/logs/server.log
}
trap finish EXIT

echo "Starting kafka"
/kafka/bin/kafka-server-start.sh /kafka/config/server.properties
