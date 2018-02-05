#!/bin/ash
# shellcheck shell=dash
# (C) Copyright 2017-2018 Hewlett Packard Enterprise Development LP

AGENT_CONF="/etc/monasca/agent"

if [ "$KEYSTONE_DEFAULTS_ENABLED" = "true" ]; then
  export OS_AUTH_URL=${OS_AUTH_URL:-"http://keystone:35357/v3/"}
  export OS_USERNAME=${OS_USERNAME:-"monasca-agent"}
  export OS_PASSWORD=${OS_PASSWORD:-"password"}
  export OS_USER_DOMAIN_NAME=${OS_USER_DOMAIN_NAME:-"Default"}
  export OS_PROJECT_NAME=${OS_PROJECT_NAME:-"mini-mon"}
  export OS_PROJECT_DOMAIN_NAME=${OS_PROJECT_DOMAIN_NAME:-"Default"}
fi

set -x

template () {
  if [ "$CONFIG_TEMPLATE" = "true" ]; then
    python /template.py "$1" "$2"
  else
    cp "$1" "$2"
  fi
}

if [ "$HOSTNAME_FROM_KUBERNETES" = "true" ]; then
  if ! AGENT_HOSTNAME=$(python /kubernetes_get_host.py); then
    echo "Error getting hostname from Kubernetes"
    return 1
  fi
  export AGENT_HOSTNAME
fi

template $AGENT_CONF/agent.yaml.j2 $AGENT_CONF/agent.yaml

monasca-forwarder
