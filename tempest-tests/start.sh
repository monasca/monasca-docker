#!/bin/sh
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

set -x

MONASCA_API_WAIT_RETRIES=${MONASCA_API_WAIT_RETRIES:-"24"}
MONASCA_API_WAIT_DELAY=${MONASCA_API_WAIT_DELAY:-"5"}

OS_USERNAME=${OS_USERNAME:-"mini-mon"}
OS_PASSWORD=${OS_PASSWORD:-"password"}
OS_TENANT_NAME=${OS_TENANT_NAME:-"mini-mon"}
OS_DOMAIN_NAME=${OS_DOMAIN_NAME:-"Default"}
ALT_USERNAME=${ALT_USERNAME:-"mini-mon"}
ALT_PASSWORD=${ALT_PASSWORD:-"password"}
ALT_TENANT_NAME=${ALT_TENANT_NAME:-"mini-mon"}
AUTH_USE_SSL=${AUTH_USE_SSL:-"False"}
KEYSTONE_SERVER=${KEYSTONE_SERVER:-"keystone"}
KEYSTONE_PORT=${KEYSTONE_PORT:-"35357"}

USE_DYNAMIC_CREDS=${USE_DYNAMIC_CREDS:-"True"}
ADMIN_PROJECT_NAME=${ADMIN_PROJECT_NAME:-"mini-mon"}
ADMIN_USERNAME=${ADMIN_USERNAME:-"mini-mon"}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-"password"}
ADMIN_DOMAIN_NAME=${ADMIN_DOMAIN_NAME:-"Default"}

if [ "$AUTH_USE_SSL" = "False" ]; then
  AUTH_PROTOCOL="http"
else
  AUTH_PROTOCOL="https"
fi

AUTH_URI="${AUTH_PROTOCOL}://${KEYSTONE_SERVER}:${KEYSTONE_PORT}/v2.0/"
AUTH_URI_V3="${AUTH_PROTOCOL}://${KEYSTONE_SERVER}:${KEYSTONE_PORT}/v3/"

if [ "$MONASCA_WAIT_FOR_API" = "true" ]; then
  echo "Waiting for Monasca API to become available..."
  success="false"

  for i in $(seq $MONASCA_API_WAIT_RETRIES); do
    monasca --os-user-domain-name "${OS_DOMAIN_NAME}" --os-project-name mini-mon \
       --os-auth-url "${AUTH_URI_V3}" --os-username "${OS_USERNAME}" \
       --os-password "${OS_PASSWORD}" alarm-list --limit 1
    if [ $? -eq 0 ]; then
      success="true"
      break
    else
      echo "Monasca API not yet ready (attempt $i of $MONASCA_API_WAIT_RETRIES)"
      sleep "$MONASCA_API_WAIT_DELAY"
    fi
  done

  if [ "$success" != "true" ]; then
    echo "Monasca API failed to become ready, exiting..."
    sleep 1
    exit 1
  fi
fi

python template.py \
  /etc/tempest/tempest.conf.j2 \
  /etc/tempest/tempest.conf

cd /monasca-api
export OS_TEST_PATH=./monasca_tempest_tests/tests/api

OSTESTR_REGEX=${OSTESTR_REGEX:-"monasca_tempest_tests"}
testr init && \
ostestr --serial --regex "${OSTESTR_REGEX}"

if [ "$STAY_ALIVE" = "true" ]; then
  sleep 7200
fi
