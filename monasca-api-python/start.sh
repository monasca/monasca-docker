#!/bin/sh

GUNICORN_WORKERS=${GUNICORN_WORKERS:-"9"}
GUNICORN_WORKER_CLASS=${GUNICORN_WORKER_CLASS:-"gevent"}
GUNICORN_WORKER_CONNECTIONS=${GUNICORN_WORKER_CONNECTIONS:-"2000"}
GUNICORN_BACKLOG=${GUNICORN_BACKLOG:-"1000"}

MYSQL_WAIT_RETRIES=${MYSQL_WAIT_RETRIES:-"24"}
MYSQL_WAIT_DELAY=${MYSQL_WAIT_DELAY:-"5"}

KAFKA_WAIT_RETRIES=${KAFKA_WAIT_RETRIES:-"24"}
KAFKA_WAIT_DELAY=${KAFKA_WAIT_DELAY:-"5"}

if [ "$MYSQL_WAIT_RETRIES" != "0" ]; then
  echo "Waiting for MySQL to become available..."
  success="false"
  for i in $(seq "$MYSQL_WAIT_RETRIES"); do
    if mysqladmin status \
        --host="$MYSQL_HOST" \
        --user="$MYSQL_USER" \
        --password="$MYSQL_PASSWORD" \
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

if [ "$CONFIG_TEMPLATE" = "true" ]; then
  python template.py \
    /etc/monasca/api-config.conf.j2 \
    /etc/monasca/api-config.conf

  python template.py \
    /etc/monasca/api-config.ini.j2 \
    /etc/monasca/api-config.ini

  python template.py \
    /etc/monasca/api-logging.conf.j2 \
    /etc/monasca/api-logging.conf
else
  cp /etc/monasca/api-config.conf.j2 /etc/monasca/api-config.conf
  cp /etc/monasca/api-config.ini.j2 /etc/monasca/api-config.ini
  cp /etc/monasca/api-logging.conf.j2 /etc/monasca/api-logging.conf
fi

if [ "$ADD_ACCESS_LOG" = "true" ]; then
  access_arg="--access-logfile -"
else
  access_arg=
fi

# Needed to allow utf8 use in the Monasca API
export PYTHONIOENCODING=utf-8
gunicorn --capture-output \
  -n monasca-api \
  --worker-class="$GUNICORN_WORKER_CLASS" \
  --worker-connections="$GUNICORN_WORKER_CONNECTIONS" \
  --backlog="$GUNICORN_BACKLOG" \
  $access_arg \
  --access-logformat "$ACCESS_LOG_FIELDS" \
  --paste /etc/monasca/api-config.ini \
  -w "$GUNICORN_WORKERS"
