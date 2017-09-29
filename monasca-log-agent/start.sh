#!/bin/sh
# (C) Copyright 2017 FUJITSU LIMITED

MONASCA_LOG_API_WAIT_RETRIES=${MONASCA_LOG_API_WAIT_RETRIES:-"24"}
MONASCA_LOG_API_WAIT_DELAY=${MONASCA_LOG_API_WAIT_DELAY:-"5"}

if [ "$MONASCA_WAIT_FOR_LOG_API" = "true" ]; then
  echo "Waiting for Monasca Log API to become available..."
  success="false"

  for i in $(seq "$MONASCA_LOG_API_WAIT_RETRIES"); do
    curl --silent --show-error --output - \
      http://log-api:"${MONASCA_CONTAINER_LOG_API_PORT}"/healthcheck 2>&1
    if [ $? -eq 0 ]; then
      echo
      success="true"
      break
    else
      echo "Monasca Log API not yet ready (attempt $i of $MONASCA_LOG_API_WAIT_RETRIES)"
      sleep "$MONASCA_LOG_API_WAIT_DELAY"
    fi
  done

  if [ "$success" != "true" ]; then
    echo "Monasca Log API failed to become ready, exiting..."
    sleep 1
    exit 1
  fi
fi

KEYSTONE_WAIT_RETRIES=${KEYSTONE_WAIT_RETRIES:-"24"}
KEYSTONE_WAIT_DELAY=${KEYSTONE_WAIT_DELAY:-"5"}

if [ "$MONASCA_WAIT_FOR_KEYSTONE" = "true" ]; then
  echo "Waiting for Keystone to become available..."
  success="false"

  for i in $(seq "$KEYSTONE_WAIT_RETRIES"); do
    curl --fail --silent --show-error --output - \
      -H "Content-Type: application/json" \
      -d '
      { "auth": {
          "identity": {
            "methods": ["password"],
            "password": {
              "user": {
                "name": "'$OS_USERNAME'",
                "domain": { "id": "'$OS_USER_DOMAIN_NAME'" },
                "password": "'$OS_PASSWORD'"
              }
            }
          }
        }
      }' $OS_AUTH_URL/auth/tokens 2>&1
    if [ $? -eq 0 ]; then
      echo
      success="true"
      break
    else
      echo "Keystone not yet ready (attempt $i of $KEYSTONE_WAIT_RETRIES)"
      sleep "$KEYSTONE_WAIT_DELAY"
    fi
  done

  if [ "$success" != "true" ]; then
    echo "Keystone failed to become ready, exiting..."
    sleep 1
    exit 1
  fi
fi

/p2 -t /monasca-log-agent.conf.p2 > /monasca-log-agent.conf

echo "Starting Monasca log agent"
logstash -f /monasca-log-agent.conf
