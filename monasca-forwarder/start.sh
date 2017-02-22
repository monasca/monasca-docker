#!/bin/sh
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

KAFKA_WAIT_RETRIES=${KAFKA_WAIT_RETRIES:-"24"}
KAFKA_WAIT_DELAY=${KAFKA_WAIT_DELAY:-"5"}

if [ -n "$KAFKA_WAIT_FOR_TOPICS" ]; then
  echo "Waiting for Kafka topics to become available..."
  success="false"

  for i in $(seq $KAFKA_WAIT_RETRIES); do
    python /kafka_wait_for_topics.py
    if [ $? -eq 0 ]; then
      success="true"
      break
    else
      echo "Kafka not yet ready (attempt $i of $KAFKA_WAIT_RETRIES)"
      sleep "$KAFKA_WAIT_DELAY"
    fi
  done
fi

if [ "$success" != "true" ]; then
  echo "Kafka failed to become ready, exiting..."
  sleep 1
  exit 1
fi

echo "Starting Forwarder..."
if [ "$CONFIG_TEMPLATE" = "true" ]; then
  python /template.py /config/forwarder.conf.j2 /config/forwarder.conf
  python /template.py /config/forwarder_metric_match.yml.j2 /config/forwarder_metric_match.yml
else
  cp /config/forwarder.conf.j2 /config/forwarder.conf
  cp /config/forwarder_metric_match.yml.j2 /config/forwarder_metric_match.yml
fi

monasca-forwarder --config-file /config/forwarder.conf
