#!/bin/sh

export GUNICORN_WORKERS=${GUNICORN_WORKERS:-1}
export GUNICORN_WORKER_CLASS=${GUNICORN_WORKER_CLASS:-"gevent"}
export GUNICORN_WORKER_CONNECTIONS=${GUNICORN_WORKER_CONNECTIONS:-2000}
export GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-10}
export GUNICORN_BACKLOG=${GUNICORN_BACKLOG:-1000}

KAFKA_WAIT_RETRIES=${KAFKA_WAIT_RETRIES:-"24"}
KAFKA_WAIT_DELAY=${KAFKA_WAIT_DELAY:-"5"}

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
    /etc/monasca/log-api.conf.j2 \
    /etc/monasca/log-api.conf

  python template.py \
    /etc/monasca/log-api-paste.ini.j2 \
    /etc/monasca/log-api-paste.ini

  python template.py \
    /etc/monasca/log-api-logging.conf.j2 \
    /etc/monasca/log-api-logging.conf

  python template.py \
    /etc/monasca/log-api-gunicorn.conf.j2 \
    /etc/monasca/log-api-gunicorn.conf
else
  cp /etc/monasca/log-api.conf.j2 /etc/monasca/log-api.conf
  cp /etc/monasca/log-api-paste.ini.j2 /etc/monasca/log-api-paste.ini
  cp /etc/monasca/log-api-logging.conf.j2 /etc/monasca/log-api-logging.conf
  cp /etc/monasca/log-api-gunicorn.conf.j2 /etc/monasca/log-api-gunicorn.conf
fi

export PYTHONIOENCODING=utf-8
gunicorn \
    --config /etc/monasca/log-api-gunicorn.conf \
    --paste /etc/monasca/log-api-paste.ini
