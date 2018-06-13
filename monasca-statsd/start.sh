#!/bin/ash
# shellcheck shell=dash
# (C) Copyright 2018 FUJITSU LIMITED

set -x

template () {
  if [ "$CONFIG_TEMPLATE" = "true" ]; then
    python /template.py "$1" "$2"
  else
    cp "$1" "$2"
  fi
}

AGENT_CONF="/etc/monasca/agent"

template /agent.yaml.j2 $AGENT_CONF/agent.yaml
rm /agent.yaml.j2 $AGENT_CONF/agent.yaml.j2
cat $AGENT_CONF/agent.yaml
monasca-statsd
