#!/bin/sh
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

MONASCA_API_WAIT_RETRIES=${MONASCA_API_WAIT_RETRIES:-"24"}
MONASCA_API_WAIT_DELAY=${MONASCA_API_WAIT_DELAY:-"5"}

if [ "$KEYSTONE_DEFAULTS_ENABLED" = "true" ]; then
  export OS_AUTH_URL=${OS_AUTH_URL:-"http://keystone:35357/v3/"}
  export OS_USERNAME=${OS_USERNAME:-"mini-mon"}
  export OS_PASSWORD=${OS_PASSWORD:-"password"}
  export OS_USER_DOMAIN_NAME=${OS_USER_DOMAIN_NAME:-"Default"}
  export OS_PROJECT_NAME=${OS_PROJECT_NAME:-"mini-mon"}
  export OS_PROJECT_DOMAIN_NAME=${OS_PROJECT_DOMAIN_NAME:-"Default"}
fi

echo "Loading Definitions...."

python /template.py /config/definitions.yml.j2 /config/definitions.yml
python monasca_alarm_definition.py --verbose --definitions-file /config/definitions.yml
