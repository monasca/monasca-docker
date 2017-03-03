#!/bin/ash

set -x

CONFIG_TEMPLATES="/templates"
CONFIG_DEST="/kafka/config"

KAFKA_LISTEN_PORT=${KAFKA_LISTEN_PORT:-"9092"}
ZOOKEEPER_CONNECTION_STRING=${ZOOKEEPER_CONNECTION_STRING:-"zookeeper:2181"}
export KAFKA_LISTEN_PORT ZOOKEEPER_CONNECTION_STRING

ZOOKEEPER_WAIT=${ZOOKEEPER_WAIT:-"true"}
ZOOKEEPER_WAIT_TIMEOUT=${ZOOKEEPER_WAIT_TIMEOUT:-"3"}
ZOOKEEPER_WAIT_DELAY=${ZOOKEEPER_WAIT_DELAY:-"10"}
ZOOKEEPER_WAIT_RETRIES=${ZOOKEEPER_WAIT_RETRIES:-"20"}

first_zk=$(echo $ZOOKEEPER_CONNECTION_STRING | cut -d, -f1)
zk_host=$(echo $first_zk | cut -d\: -f1)
zk_port=$(echo $first_zk | cut -d\: -f2)

# wait for zookeeper to become available
if [ "$ZOOKEEPER_WAIT" = "true" ]; then
  success="false"
  for i in $(seq $ZOOKEEPER_WAIT_RETRIES); do
    ok=$(echo ruok | nc $zk_host $zk_port -w $ZOOKEEPER_WAIT_TIMEOUT)
    if [ $? -eq 0 -a "$ok" = "imok" ]; then
      success="true"
      break
    else
      echo "Connect attempt $i of $ZOOKEEPER_WAIT_RETRIES failed, retrying..."
      sleep $ZOOKEEPER_WAIT_DELAY
    fi
  done

  if [ "$success" != "true" ]; then
    echo "Could not connect to $first_zk after $i attempts, exiting..."
    sleep 1
    exit 1
  fi
fi

if [ "$KAFKA_HOSTNAME_FROM_IP" = "true" ]; then
  # see also: http://stackoverflow.com/a/21336679
  ip=$(ip route get 8.8.8.8 | awk 'NR==1 {print $NF}')
  echo "Using autodetected IP as advertised hostname: $ip"
  export KAFKA_ADVERTISED_HOST_NAME=$ip
fi

# copy all normal .properties files
for f in $CONFIG_TEMPLATES/*.properties; do
  if [ -e "$f" ]; then
    cp "$f" "$CONFIG_DEST/$(basename "$f")"
  fi
done

# apply all *.properties.j2 templates
for f in $CONFIG_TEMPLATES/*.properties.j2; do
  if [ -e "$f" ]; then
    python /template.py "$f" "$CONFIG_DEST/$(basename "$f" .j2)"
  fi
done

if [ "$KAFKA_JMX" = "true" ]; then
  KAFKA_JMX_PORT=${KAFKA_JMX_PORT:-"7203"}

  # see also: https://github.com/ches/docker-kafka/blob/master/Dockerfile
  # we don't export any kafka options by default so JVMs spawned on this
  # container don't always hit port conflicts
  # this should make it possible to e.g. run scripts in /kafka/bin/ on the
  # runnign server without the JVM crashing due to the RMI port being used
  export JMX_PORT=$KAFKA_JMX_PORT

  if [ -z "$KAFKA_JMX_OPTS" ]; then
    KAFKA_JMX_OPTS="-Dcom.sun.management.jmxremote=true"
    KAFKA_JMX_OPTS="$KAFKA_JMX_OPTS -Dcom.sun.management.jmxremote.authenticate=false"
    KAFKA_JMX_OPTS="$KAFKA_JMX_OPTS -Dcom.sun.management.jmxremote.ssl=false"
    KAFKA_JMX_OPTS="$KAFKA_JMX_OPTS -Dcom.sun.management.jmxremote.rmi.port=$KAFKA_JMX_PORT"
    KAFKA_JMX_OPTS="$KAFKA_JMX_OPTS -Djava.rmi.server.hostname=$KAFKA_ADVERTISED_HOST_NAME "
    export KAFKA_JMX_OPTS
  fi
fi

echo "Creating topics..."
python /create_topics.py &

echo "Starting kafka..."
exec /kafka/bin/kafka-server-start.sh "$CONFIG_DEST/server.properties"
