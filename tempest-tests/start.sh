#!/bin/sh
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

set -x

export MONASCA_API_WAIT_RETRIES=${MONASCA_API_WAIT_RETRIES:-"24"}
export MONASCA_API_WAIT_DELAY=${MONASCA_API_WAIT_DELAY:-"5"}

export OS_USERNAME=${OS_USERNAME:-"mini-mon"}
export OS_PASSWORD=${OS_PASSWORD:-"password"}
export OS_TENANT_NAME=${OS_TENANT_NAME:-"mini-mon"}
export OS_DOMAIN_NAME=${OS_DOMAIN_NAME:-"Default"}
export ALT_USERNAME=${ALT_USERNAME:-"mini-mon"}
export ALT_PASSWORD=${ALT_PASSWORD:-"password"}
export ALT_TENANT_NAME=${ALT_TENANT_NAME:-"mini-mon"}
export AUTH_USE_SSL=${AUTH_USE_SSL:-"False"}
export KEYSTONE_SERVER=${KEYSTONE_SERVER:-"keystone"}
export KEYSTONE_PORT=${KEYSTONE_PORT:-"35357"}

export USE_DYNAMIC_CREDS=${USE_DYNAMIC_CREDS:-"True"}
export ADMIN_PROJECT_NAME=${ADMIN_PROJECT_NAME:-"mini-mon"}
export ADMIN_USERNAME=${ADMIN_USERNAME:-"mini-mon"}
export ADMIN_PASSWORD=${ADMIN_PASSWORD:-"password"}
export ADMIN_DOMAIN_NAME=${ADMIN_DOMAIN_NAME:-"Default"}

if [ "$AUTH_USE_SSL" = "true" ]; then
  export AUTH_PROTOCOL="https"
else
  export AUTH_PROTOCOL="http"
fi

export AUTH_URI="${AUTH_PROTOCOL}://${KEYSTONE_SERVER}:${KEYSTONE_PORT}/v2.0/"
export AUTH_URI_V3="${AUTH_PROTOCOL}://${KEYSTONE_SERVER}:${KEYSTONE_PORT}/v3/"

if [ "$MONASCA_WAIT_FOR_API" = "true" ]; then
  echo "Waiting for Monasca API to become available..."
  success="false"

  for i in $(seq "$MONASCA_API_WAIT_RETRIES"); do
    if monasca --os-user-domain-name "${OS_DOMAIN_NAME}" --os-project-name "${OS_TENANT_NAME}" \
       --os-auth-url "${AUTH_URI_V3}" --os-username "${OS_USERNAME}" \
       --os-password "${OS_PASSWORD}" alarm-list --limit 1; then
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

cd /monasca-api || exit
export OS_TEST_PATH=./monasca_tempest_tests/tests/api

if [ ! -r .testrepository ]; then
  testr init
fi

OSTESTR_REGEX=${OSTESTR_REGEX:-"monasca_tempest_tests"}
ostestr --serial --regex "${OSTESTR_REGEX}"

RESULT=$?

if [ $RESULT != 0 ] && [ "$STAY_ALIVE_ON_FAILURE" = "true" ]; then
  sleep 7200
fi
exit $RESULT
