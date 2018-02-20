#!/bin/sh

j2 /local_settings.py.j2 > /horizon/openstack_dashboard/local/local_settings.py
j2 /monitoring-local_settings.py.j2 > /monasca-ui/monitoring/config/local_settings.py

apachectl -D FOREGROUND
