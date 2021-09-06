#!/bin/sh
# shellcheck disable=SC2153
if [ -n "$GF_DATABASE_PORT" ]; then
  export GF_DATABASE_HOST=$GF_DATABASE_HOST":"$GF_DATABASE_PORT
fi

export GRAFANA_LOG_LEVEL=${GRAFANA_LOG_LEVEL:-"warn"}

FILENAME=/usr/share/grafana/public/dashboards/drilldown.js
if [ ! -f $FILENAME ]; then
  copy /drilldown.js /usr/share/grafana/public/dashboards/drilldown.js
fi

python3 /template.py /etc/grafana/grafana.ini.j2 /etc/grafana/grafana.ini
exec /run.sh
