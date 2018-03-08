#!/bin/sh

APACHE_CONF_FILE="/etc/apache2/sites-available/horizon.conf"

if ! grep -q "ProxyPassReverse /grafana" "${APACHE_CONF_FILE}"; then
  # shellcheck disable=SC2016
  sed -i '/<\/Virtualhost>/i\\n'\
'    ProxyPass \/grafana http:\//${GRAFANA_IP}:${GRAFANA_PORT}\n'\
'    ProxyPassReverse \/grafana http:\//${GRAFANA_IP}:${GRAFANA_PORT}'\
'' "${APACHE_CONF_FILE}"
else
  echo "Reverse proxy for Grafana already configured"
fi

j2 /local_settings.py.j2 > /horizon/openstack_dashboard/local/local_settings.py
j2 /monitoring-local_settings.py.j2 > /monasca-ui/monitoring/config/local_settings.py

apachectl -D FOREGROUND
