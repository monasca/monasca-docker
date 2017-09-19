#!/bin/sh
# (C) Copyright 2017 FUJITSU LIMITED

MONASCA_LOG_API_WAIT_RETRIES=${MONASCA_LOG_API_WAIT_RETRIES:-"24"}
MONASCA_LOG_API_WAIT_DELAY=${MONASCA_LOG_API_WAIT_DELAY:-"5"}

if [ -n "$MONASCA_WAIT_FOR_LOG_API" ]; then
  echo "Waiting for Monasca Log API to become available..."
  success="false"

  for i in $(seq "$MONASCA_LOG_API_WAIT_RETRIES"); do
    curl --silent --show-error --output - \
      http://log-api:"${MONASCA_CONTAINER_LOG_API_PORT}"/healthcheck 2>&1
    if [ $? -eq 0 ]; then
      success="true"
      break
    else
      echo "Monasca Log API not yet ready (attempt $i of $MONASCA_LOG_API_WAIT_RETRIES)"
      sleep "$MONASCA_LOG_API_WAIT_DELAY"
    fi
  done
fi

if [ "$success" != "true" ]; then
  echo "Monasca Log API failed to become ready, exiting..."
  sleep 1
  exit 1
fi

/p2 -t /monasca-log-agent.conf.p2 > /monasca-log-agent.conf

logstash -f /monasca-log-agent.conf
