#!/bin/sh
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

set -x

MONASCA_API_WAIT_RETRIES=${MONASCA_API_WAIT_RETRIES:-"24"}
MONASCA_API_WAIT_DELAY=${MONASCA_API_WAIT_DELAY:-"5"}

if [ "$MONASCA_WAIT_FOR_API" = "true" ]; then
  # TODO Need the correct credentials for this to work
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

  if [ "$success" != "true" ]; then
    echo "Monasca API failed to become ready, exiting..."
    sleep 1
    exit 1
  fi
fi

if [ "$CONFIG_TEMPLATE" = "true" ]; then
  python template.py \
    /etc/tempest/tempest.conf.j2 \
    /etc/tempest/tempest.conf
else
  cp /etc/tempest/tempest.conf.j2 /etc/tempest/tempest.conf
fi

export OS_TEST_PATH=./monasca_tempest_tests/tests/api

cd /monasca-api && \
sed -e "s/'anotherrole'/'monasca-read-only-user'/" -i.sv monasca_tempest_tests/tests/api/base.py && \
testr init && \
testr list-tests monasca_tempest_tests > monasca_tests  && \
testr run --load-list=monasca_tests  && \

FAILED=$?

if [ $FAILED -ne 0]; then
  sleep 3600
fi
exit $FAILED
