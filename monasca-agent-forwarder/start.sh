#!/bin/ash
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

set -x

AGENT_CONF="/etc/monasca/agent"

template () {
  if [ "$CONFIG_TEMPLATE" = "true" ]; then
    python /template.py "$1" "$2"
  else
    cp "$1" "$2"
  fi
}

if [ "$HOSTNAME_FROM_KUBERNETES" = "true" ]; then
  AGENT_HOSTNAME=$(python /kubernetes_get_host.py)
  if [ $? != 0 ]; then
    echo "Error getting hostname from Kubernetes"
    return 1
  fi
  export AGENT_HOSTNAME
fi

template $AGENT_CONF/agent.yaml.j2 $AGENT_CONF/agent.yaml

/usr/local/bin/monasca-forwarder
