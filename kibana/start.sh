#!/usr/bin/env bash

python /template.py /kibana.yml.j2 /opt/kibana/config/kibana.yml

if [ "$MONASCA_PLUGIN_ENABLED" == True ]; then
    /wait-for.sh "$KEYSTONE_URI" -- kibana
else
    kibana
fi
