#!/bin/sh

set -x

KEYSTONE_IDENTITY_URI=${KEYSTONE_IDENTITY_URI:-"http://keystone:35357"}

KEYSTONE_INIT_WAIT_RETRIES=${KEYSTONE_INIT_WAIT_RETRIES:-"24"}
KEYSTONE_INIT_WAIT_DELAY=${KEYSTONE_INIT_WAIT_DELAY:-"5"}

wait_keystone() {
  echo "Waiting for Keystone to become available..."
  success="false"
  for i in $(seq $KEYSTONE_INIT_WAIT_RETRIES); do
    curl "$KEYSTONE_IDENTITY_URI" --max-time=10
    if [ $? -eq 0 ]; then
      echo "Keystone is available, continuing..."
      success="true"
      break
    else
      echo "Connection attempt $i of $KEYSTONE_INIT_WAIT_RETRIES failed"
      sleep "$KEYSTONE_INIT_WAIT_DELAY"
    fi
  done

  if [ "$success" != "true" ]; then
      echo "Unable to reach Keystone! Exiting..."
      sleep 1
      exit 1
  fi
}

wait_keystone

LD_PRELOAD=/stack-fix.so python keystone_init.py
