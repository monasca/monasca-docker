#!/bin/sh
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

MYSQL_WAIT_RETRIES=${MYSQL_WAIT_RETRIES:-"24"}
MYSQL_WAIT_DELAY=${MYSQL_WAIT_DELAY:-"5"}

KAFKA_WAIT_RETRIES=${KAFKA_WAIT_RETRIES:-"24"}
KAFKA_WAIT_DELAY=${KAFKA_WAIT_DELAY:-"5"}

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

echo "Starting notification engine..."
if [ "$CONFIG_TEMPLATE" = "true" ]; then
  python /template.py /config/notification.yaml.j2 /config/notification.yaml
else
  cp /config/notification.yaml.j2 /config/notification.yaml
fi

monasca-notification /config/notification.yaml
