#!/bin/ash
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

set -x

PLUGIN_TEMPLATES="/templates"
USER_PLUGINS="/plugins.d"

AGENT_CONF="/etc/monasca/agent"
AGENT_PLUGINS="$AGENT_CONF/conf.d"
AGENT_LOG_DIR="/var/log/monasca/agent/"
AGENT_USER="mon-agent"

adduser -S $AGENT_USER

mkdir -p "$AGENT_PLUGINS"
mkdir -p "$AGENT_LOG_DIR"
chown $AGENT_USER "$AGENT_LOG_DIR"

template () {
  if [ "$CONFIG_TEMPLATE" = "true" ]; then
    python /template.py "$1" "$2"
  else
    cp "$1" "$2"
  fi
}

if [ "$HOSTNAME_FROM_KUBERNETES" = "true" ]; then
  AGENT_HOSTNAME=$(python /kubernetes_get_host.py)
  export AGENT_HOSTNAME
fi

if [ "$DOCKER" = "true" ]; then
  template $PLUGIN_TEMPLATES/docker.yaml.j2 $AGENT_PLUGINS/docker.yaml
fi

# cadvisor: optional in docker, required in k8s
# - docker: CADVISOR_HOST must be defined
# - k8s: either KUBERNETES or KUBERNETES_HOST must be nonempty
if [ -n "$CADVISOR_HOST" -o -n "$KUBERNETES" -o -n "$KUBERNETES_API" ]; then
  template $PLUGIN_TEMPLATES/cadvisor.yaml.j2 $AGENT_PLUGINS/cadvisor.yaml
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
  template "$f" "$AGENT_PLUGINS/$(basename "$f" .j2)"
done

# copy plain user plugins
for f in $USER_PLUGINS/*.yaml; do
  cp "$f" "$AGENT_PLUGINS/$(basename "$f")"
done

template $AGENT_CONF/agent.yaml.j2 $AGENT_CONF/agent.yaml

supervisord --nodaemon -c /etc/supervisor/supervisord.conf
