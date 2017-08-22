#!/bin/ash
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

set -x

PLUGIN_TEMPLATES="/templates"
USER_PLUGINS="/plugins.d"

AGENT_CONF="/etc/monasca/agent"
AGENT_PLUGINS="$AGENT_CONF/conf.d"

mkdir -p "$AGENT_PLUGINS"

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

# apply user templates
for f in $USER_PLUGINS/*.yaml.j2; do
  if [ -e "$f" ]; then
    template "$f" "$AGENT_PLUGINS/$(basename "$f" .j2)"
  fi
done

# copy plain user plugins
for f in $USER_PLUGINS/*.yaml; do
  if [ -e "$f" ]; then
    cp "$f" "$AGENT_PLUGINS/$(basename "$f")"
  fi
done

template $AGENT_CONF/agent.yaml.j2 $AGENT_CONF/agent.yaml

/usr/bin/monasca-collector foreground
