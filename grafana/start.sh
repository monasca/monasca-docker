#!/bin/sh

python /template.py /etc/grafana/grafana.ini.j2 /etc/grafana/grafana.ini
/go/bin/grafana-server -config /etc/grafana/grafana.ini -homepath /var/lib/grafana
