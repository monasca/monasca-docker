#!/bin/sh

# Default values for executing it manually on the host
KEYSTONE_AUTH_URI=${KEYSTONE_AUTH_URI:-http://localhost:5000}
KEYSTONE_ADMIN_USER=${KEYSTONE_ADMIN_USER:-admin}
KEYSTONE_ADMIN_PASSWORD=${KEYSTONE_ADMIN_PASSWORD:-secretadmin}
KEYSTONE_ADMIN_TENANT=${KEYSTONE_ADMIN_TENANT:-admin}
KEYSTONE_ADMIN_DOMAIN=${KEYSTONE_ADMIN_DOMAIN:-default}
MONASCA_CONTAINER_API_PORT=${MONASCA_CONTAINER_API_PORT:-8070}

KEYSTONE_TOKEN=$(curl --include --silent --show-error --output - --header "Content-Type:application/json" \
    --data '{ "auth": {
        "identity": {
          "methods": ["password"],
          "password": {
            "user": {
              "name": "'"${KEYSTONE_ADMIN_USER}"'",
              "domain": { "id": "'"${KEYSTONE_ADMIN_DOMAIN}"'" },
              "password": "'"${KEYSTONE_ADMIN_PASSWORD}"'"
            }
          }
        },
        "scope": {
          "project": {
            "name": "'"${KEYSTONE_ADMIN_TENANT}"'",
            "domain": { "id": "'"${KEYSTONE_ADMIN_DOMAIN}"'" }
          }
        }
      }
    }' \
    "${KEYSTONE_AUTH_URI}/v3/auth/tokens" 2>&1 | \
        awk -F ':' '
            BEGIN {token=""; output=""}
            $1 == "X-Subject-Token" {token=$2}
            {output=output $0 "\n"}
            END {
                if(token!="") {print token}
                else {print output > "/dev/stderr"; exit 1}
            }'
    ) && \
curl --include --silent --show-error --output - --header "X-Auth-Token:${KEYSTONE_TOKEN}" \
    http://localhost:"${MONASCA_CONTAINER_API_PORT}" 2>&1 | \
    awk '
        BEGIN {status_code="0"; body=""; output=""}
        $1 ~ /^HTTP\// {status_line=$0; status_code=$2}
        $1 ~ /^\{/ {body=$0}
        {output=output $0 "\n"}
        END {
            if(status_code=="200") {
                print status_line;
                print body;
            } else {
                print output;
                exit 2;
            }
        }'

exit $?
