#!/bin/sh
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

MONASCA_API_WAIT_RETRIES=${MONASCA_API_WAIT_RETRIES:-"24"}
MONASCA_API_WAIT_DELAY=${MONASCA_API_WAIT_DELAY:-"5"}

if [ -n "$MONASCA_WAIT_FOR_API" ]; then
  echo "Waiting for Monasca API to become available..."
  success="false"

  for i in $(seq $MONASCA_API_WAIT_RETRIES); do
    monasca alarm-definition-list --limit 1
    if [ $? -eq 0 ]; then
      success="true"
      break
    else
      echo "Monasca API not yet ready (attempt $i of $MONASCA_API_WAIT_RETRIES)"
      sleep "$MONASCA_API_WAIT_DELAY"
    fi
  done
fi

if [ "$success" != "true" ]; then
  echo "Monasca API failed to become ready, exiting..."
  sleep 1
  exit 1
fi

echo "Loading Definitions...."
python monasca_alarm_definition.py --verbose --definitions-file /config/definitions.yml 
