#!/bin/sh
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

set -x

export OS_USERNAME=${OS_USERNAME:-"mini-mon"}
export OS_PASSWORD=${OS_PASSWORD:-"password"}
export OS_TENANT_NAME=${OS_TENANT_NAME:-"mini-mon"}
export OS_DOMAIN_NAME=${OS_DOMAIN_NAME:-"Default"}
export OS_AUTH_URL=${OS_AUTH_URL:-"http://keystone:35357/v3"}
export MONASCA_URL=${MONASCA_URL:-"http://monasca-api:8070"}

export WEBHOOK_IP
WEBHOOK_IP=$(ip route get 8.8.8.8 | awk 'NR==1 {print $NF}')

/smoke-test
