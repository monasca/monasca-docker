#!/bin/sh

# shellcheck disable=SC2153
if [ -n "$GF_DATABASE_PORT" ]; then
  export GF_DATABASE_HOST=$GF_DATABASE_HOST":"$GF_DATABASE_PORT
fi

python /template.py /etc/grafana/grafana.ini.j2 /etc/grafana/grafana.ini
/go/bin/grafana-server -config /etc/grafana/grafana.ini -homepath /var/lib/grafana
