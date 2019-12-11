#!/bin/ash
# shellcheck shell=dash
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

set -x

PLUGIN_TEMPLATES="/templates"
USER_PLUGINS="/plugins.d"

AGENT_CONF="/etc/monasca/agent"
AGENT_PLUGINS="$AGENT_CONF/conf.d"

if [ "$KEYSTONE_DEFAULTS_ENABLED" = "true" ]; then
  export OS_AUTH_URL=${OS_AUTH_URL:-"http://keystone:35357/v3/"}
  export OS_USERNAME=${OS_USERNAME:-"monasca-agent"}
  export OS_PASSWORD=${OS_PASSWORD:-"password"}
  export OS_USER_DOMAIN_NAME=${OS_USER_DOMAIN_NAME:-"Default"}
  export OS_PROJECT_NAME=${OS_PROJECT_NAME:-"mini-mon"}
  export OS_PROJECT_DOMAIN_NAME=${OS_PROJECT_DOMAIN_NAME:-"Default"}
fi

mkdir -p "$AGENT_PLUGINS"

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

if [ "$DOCKER" = "true" ]; then
  template $PLUGIN_TEMPLATES/docker.yaml.j2 $AGENT_PLUGINS/docker.yaml
fi

# cadvisor
if [ "$CADVISOR" = "true" ]; then
  template $PLUGIN_TEMPLATES/cadvisor_host.yaml.j2 $AGENT_PLUGINS/cadvisor_host.yaml
fi

# kubernetes
if [ "$KUBERNETES" = "true" ]; then
  template $PLUGIN_TEMPLATES/kubernetes.yaml.j2 $AGENT_PLUGINS/kubernetes.yaml
fi

# kubernetes_api
if [ "$KUBERNETES_API" = "true" ]; then
  template $PLUGIN_TEMPLATES/kubernetes_api.yaml.j2 $AGENT_PLUGINS/kubernetes_api.yaml
fi

# prometheus scraping
if [ "$PROMETHEUS" = "true" ]; then
  template $PLUGIN_TEMPLATES/prometheus.yaml.j2 $AGENT_PLUGINS/prometheus.yaml
fi

# monasca-monitoring
if [ "$MONASCA_MONITORING" = "true" ]; then
  template $PLUGIN_TEMPLATES/zk.yaml.j2 $AGENT_PLUGINS/zk.yaml
  template $PLUGIN_TEMPLATES/kafka_consumer.yaml.j2 $AGENT_PLUGINS/kafka_consumer.yaml
  template $PLUGIN_TEMPLATES/mysql.yaml.j2 $AGENT_PLUGINS/mysql.yaml
fi

# monasca-log-monitoring
if [ "$MONASCA_LOG_MONITORING" = "true" ]; then
  template $PLUGIN_TEMPLATES/elastic.yaml.j2 $AGENT_PLUGINS/elastic.yaml
fi

# common for monasca-monitoring and monasca-log-monitoring
if [ "$MONASCA_MONITORING" = "true" ] || [ "$MONASCA_LOG_MONITORING" = "true" ]; then
  template $PLUGIN_TEMPLATES/http_check.yaml.j2 $AGENT_PLUGINS/http_check.yaml
  template $PLUGIN_TEMPLATES/process.yaml.j2 $AGENT_PLUGINS/process.yaml
fi

# system
template $PLUGIN_TEMPLATES/cpu.yaml.j2 $AGENT_PLUGINS/cpu.yaml
template $PLUGIN_TEMPLATES/disk.yaml.j2 $AGENT_PLUGINS/disk.yaml
template $PLUGIN_TEMPLATES/load.yaml.j2 $AGENT_PLUGINS/load.yaml
template $PLUGIN_TEMPLATES/memory.yaml.j2 $AGENT_PLUGINS/memory.yaml

# apply user templates
for f in "$USER_PLUGINS"/*.yaml.j2; do
  if [ -e "$f" ]; then
    template "$f" "$AGENT_PLUGINS/$(basename "$f" .j2)"
  fi
done

# copy plain user plugins
for f in "$USER_PLUGINS"/*.yaml; do
  if [ -e "$f" ]; then
    cp "$f" "$AGENT_PLUGINS/$(basename "$f")"
  fi
done

template $AGENT_CONF/agent.yaml.j2 $AGENT_CONF/agent.yaml

monasca-collector foreground
