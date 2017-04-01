#!/bin/sh

echo "Waiting for storm to become available..."
success="false"
for i in $(seq $STORM_WAIT_RETRIES); do
  timeout -t $STORM_WAIT_TIMEOUT storm list
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

echo "Submitting storm topology..."

storm jar /monasca-thresh.jar \
  monasca.thresh.ThresholdingEngine \
  /storm/conf/thresh-config.yml \
  thresh-cluster
