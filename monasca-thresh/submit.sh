#!/bin/sh

TOPOLOGY_NAME="thresh-cluster"

MYSQL_WAIT_RETRIES=${MYSQL_WAIT_RETRIES:-"24"}
MYSQL_WAIT_DELAY=${MYSQL_WAIT_DELAY:-"5"}

KAFKA_WAIT_RETRIES=${KAFKA_WAIT_RETRIES:-"24"}
KAFKA_WAIT_DELAY=${KAFKA_WAIT_DELAY:-"5"}

echo "Waiting for MySQL to become available..."
success="false"
for i in $(seq "$MYSQL_WAIT_RETRIES"); do
  mysqladmin status \
      --host="$MYSQL_DB_HOST" \
      --port="$MYSQL_DB_PORT" \
      --user="$MYSQL_DB_USERNAME" \
      --password="$MYSQL_DB_PASSWORD" \
      --connect_timeout=10
  if [ $? -eq 0 ]; then
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
    python /kafka_wait_for_topics.py
    if [ $? -eq 0 ]; then
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

if ${NO_STORM_CLUSTER} = "true"; then
  echo "Using Thresh Config file /storm/conf/thresh-config.yml. Contents:"
  cat /storm/conf/thresh-config.yml | grep -vi password
  JAVAOPTS="-Xmx$(python /heap.py "$WORKER_MAX_HEAP_MB")"
  echo "Submitting storm topology as local cluster using JAVAOPTS of $JAVAOPTS"
  java "$JAVAOPTS" -classpath "/monasca-thresh.jar:/storm/lib/*" monasca.thresh.ThresholdingEngine /storm/conf/thresh-config.yml thresh-cluster local
  exit $?
fi

echo "Waiting for storm to become available..."
success="false"
for i in $(seq "$STORM_WAIT_RETRIES"); do
  timeout -t "$STORM_WAIT_TIMEOUT" storm list
  if [ $? -eq 0 ]; then
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
  cat /storm/conf/thresh-config.yml | grep -vi password
  echo "Submitting storm topology..."
  storm jar /monasca-thresh.jar \
    monasca.thresh.ThresholdingEngine \
    /storm/conf/thresh-config.yml \
    "$TOPOLOGY_NAME"
fi
