#!/bin/sh
# shellcheck disable=SC2086
# (C) Copyright 2017 FUJITSU LIMITED

MONASCA_LOG_API_WAIT_RETRIES=${MONASCA_LOG_API_WAIT_RETRIES:-"24"}
MONASCA_LOG_API_WAIT_DELAY=${MONASCA_LOG_API_WAIT_DELAY:-"5"}
KEYSTONE_WAIT_RETRIES=${KEYSTONE_WAIT_RETRIES:-"24"}
KEYSTONE_WAIT_DELAY=${KEYSTONE_WAIT_DELAY:-"5"}

wait_for_log_api() {
  if [ "$1" = "true" ]; then
    echo "Waiting for Monasca Log API to become available..."

    for i in $(seq "$MONASCA_LOG_API_WAIT_RETRIES"); do
      curl --silent --show-error --output - \
        "${MONASCA_LOG_API_URL}"/healthcheck 2>&1 && return

      echo "Monasca Log API not yet ready (attempt $i of $MONASCA_LOG_API_WAIT_RETRIES)"
      sleep "$MONASCA_LOG_API_WAIT_DELAY"
    done
    echo "Monasca Log API failed to become ready, exiting..."
    sleep 1
    exit 1
  fi
}

wait_for_keystone() {
  if [ "$1" = "true" ]; then
    echo "Waiting for Keystone to become available..."

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
        }' "$OS_AUTH_URL"/auth/tokens 2>&1 && return

      echo "Keystone not yet ready (attempt $i of $KEYSTONE_WAIT_RETRIES)"
      sleep "$KEYSTONE_WAIT_DELAY"
    done

    echo "Keystone failed to become ready, exiting..."
    sleep 1
    exit 1
  fi
}

wait_for_log_api "$MONASCA_WAIT_FOR_LOG_API"
wait_for_keystone "$MONASCA_WAIT_FOR_KEYSTONE"

/p2 -t /monasca-log-agent.conf.j2 > /monasca-log-agent.conf

echo
echo "Starting Monasca log agent"
logstash -f /monasca-log-agent.conf
