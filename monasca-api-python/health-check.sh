#!/bin/sh

# Default values for executing it manually on the host
KEYSTONE_AUTH_URI=${1:-http://localhost:5000}
KEYSTONE_ADMIN_USER=${2:-admin}
KEYSTONE_ADMIN_PASSWORD=${3:-secretadmin}
API_PORT=${4:-8070}

KEYSTONE_TOKEN=$(curl --include --silent --output - --header "Content-Type: application/json" \
    --data '{"auth":{"identity":{"methods":["password"],"password":{"user":{"name":"'"${KEYSTONE_ADMIN_USER}"'","domain":{"id":"default"},"password":"'"${KEYSTONE_ADMIN_PASSWORD}"'"}}}}}' \
    "${KEYSTONE_AUTH_URI}/v3/auth/tokens" | awk -F ':' '$1=="X-Subject-Token" {print $2}')

curl --silent --output - --header "X-Auth-Token:${KEYSTONE_TOKEN}" -o - http://localhost:${API_PORT}
