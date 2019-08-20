#!/bin/sh

TOPOLOGY_NAME="thresh-cluster"

MYSQL_WAIT_RETRIES=${MYSQL_WAIT_RETRIES:-"24"}
MYSQL_WAIT_DELAY=${MYSQL_WAIT_DELAY:-"5"}

KAFKA_WAIT_RETRIES=${KAFKA_WAIT_RETRIES:-"24"}
KAFKA_WAIT_DELAY=${KAFKA_WAIT_DELAY:-"5"}

THRESH_STACK_SIZE=${THRESH_STACK_SIZE:-"1024k"}

echo "Waiting for MySQL to become available..."
success="false"
for i in $(seq "$MYSQL_WAIT_RETRIES"); do
  if mysqladmin status \
      --host="$MYSQL_DB_HOST" \
      --port="$MYSQL_DB_PORT" \
      --user="$MYSQL_DB_USERNAME" \
      --password="$MYSQL_DB_PASSWORD" \
      --connect_timeout=10; then
    echo "MySQL is available, continuing..."
    success="true"
    break
  else
    echo "Connection attempt $i of $MYSQL_WAIT_RETRIES failed"
    sleep "$MYSQL_WAIT_DELAY"
  fi
done

if [ "$success" != "true" ]; then
    echo "Unable to reach MySQL database! Exiting..."
    sleep 1
    exit 1
fi

if [ -n "$KAFKA_WAIT_FOR_TOPICS" ]; then
  echo "Waiting for Kafka topics to become available..."
  success="false"

  for i in $(seq "$KAFKA_WAIT_RETRIES"); do
    if python /kafka_wait_for_topics.py; then
      success="true"
      break
    else
      echo "Kafka not yet ready (attempt $i of $KAFKA_WAIT_RETRIES)"
      sleep "$KAFKA_WAIT_DELAY"
    fi
  done

  if [ "$success" != "true" ]; then
    echo "Kafka failed to become ready, exiting..."
    sleep 1
    exit 1
  fi
fi

# generate thresh-config.yml
python template.py /templates/thresh-config.yml.j2 /storm/conf/thresh-config.yml

if [ "${NO_STORM_CLUSTER}" = "true" ]; then
  echo "Using Thresh Config file /storm/conf/thresh-config.yml. Contents:"
  grep -vi password /storm/conf/thresh-config.yml
  # shellcheck disable=SC2086
  JAVAOPTS="-XX:MaxRAM=$(python /memory.py $WORKER_MAX_MB) -XX:+UseSerialGC -Xss$THRESH_STACK_SIZE"

  if [ "$LOCAL_JMX" = "true" ]; then
    JAVAOPTS="$JAVAOPTS -Dcom.sun.management.jmxremote=true"

    port="${LOCAL_JMX_PORT:-9090}"
    JAVAOPTS="$JAVAOPTS -Dcom.sun.management.jmxremote.port=$port"
    JAVAOPTS="$JAVAOPTS -Dcom.sun.management.jmxremote.rmi.port=$port"
    JAVAOPTS="$JAVAOPTS -Dcom.sun.management.jmxremote.ssl=false"
    JAVAOPTS="$JAVAOPTS -Dcom.sun.management.jmxremote.authenticate=false"
    JAVAOPTS="$JAVAOPTS -Dcom.sun.management.jmxremote.local.only=false"
  fi

  if [ -n "$LOG_CONFIG_FILE" ]; then
    JAVAOPTS="$JAVAOPTS -Dlog4j.configurationFile=$LOG_CONFIG_FILE"
  fi

  echo "Submitting storm topology as local cluster using JAVAOPTS of $JAVAOPTS"
  # shellcheck disable=SC2086
  java $JAVAOPTS -classpath "/monasca-thresh.jar:/storm/lib/*" monasca.thresh.ThresholdingEngine /storm/conf/thresh-config.yml thresh-cluster local
  exit $?
fi

echo "Waiting for storm to become available..."
success="false"
for i in $(seq "$STORM_WAIT_RETRIES"); do
  if timeout -t "$STORM_WAIT_TIMEOUT" storm list; then
    echo "Storm is available, continuing..."
    success="true"
    break
  else
    echo "Connection attempt $i of $STORM_WAIT_RETRIES failed"
    sleep "$STORM_WAIT_DELAY"
  fi
done

if [ "$success" != "true" ]; then
  echo "Unable to connect to Storm! Exiting..."
  sleep 1
  exit 1
fi

topologies=$(storm list | awk '/-----/,0{if (!/-----/)print $1}')
found="false"
for topology in $topologies; do
  if [ "$topology" = "$TOPOLOGY_NAME" ]; then
    found="true"
    echo "Found existing storm topology with name: $topology"
    break
  fi
done

if [ "$found" = "true" ]; then
  echo "Storm topology already exists, will not submit again"
  # TODO handle upgrades
else
  echo "Using Thresh Config file /storm/conf/thresh-config.yml. Contents:"
  grep -vi password /storm/conf/thresh-config.yml
  echo "Submitting storm topology..."
  storm jar /monasca-thresh.jar \
    monasca.thresh.ThresholdingEngine \
    /storm/conf/thresh-config.yml \
    "$TOPOLOGY_NAME"
fi
