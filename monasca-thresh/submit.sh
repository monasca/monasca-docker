#!/bin/sh

TOPOLOGY_NAME="thresh-cluster"

echo "Waiting for storm to become available..."
success="false"
for i in $(seq $STORM_WAIT_RETRIES); do
  date
  timeout -t $STORM_WAIT_TIMEOUT storm list
  if [ $? -eq 0 ]; then
    echo "Storm is available, continuing..."
    success="true"
    break
  else
    echo $?
    date
    ps -ef
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
