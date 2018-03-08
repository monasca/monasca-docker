#!/bin/sh

if [ -n "$GF_DATABASE_PORT" ]; then
  export GF_DATABASE_HOST=$GF_DATABASE_HOST":"$GF_DATABASE_PORT
fi

export GRAFANA_LOG_LEVEL=${GRAFANA_LOG_LEVEL:-"warn"}

FILENAME=/var/lib/grafana/public/dashboards/drilldown.js
if [ ! -f $FILENAME ]; then
   copy /drilldown.js /var/lib/grafana/public/dashboards/drilldown.js
fi

python /template.py /etc/grafana/grafana.ini.j2 /etc/grafana/grafana.ini
/go/bin/grafana-server -config /etc/grafana/grafana.ini -homepath /var/lib/grafana
