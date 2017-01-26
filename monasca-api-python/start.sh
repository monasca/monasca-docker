#!/bin/sh

if [ "$CONFIG_TEMPLATE" = "true" ]; then
  python template.py \
    /etc/monasca/api-config.conf.j2 \
    /etc/monasca/api-config.conf

  python template.py \
    /etc/monasca/api-config.ini.j2 \
    /etc/monasca/api-config.ini

  python template.py \
    /etc/monasca/api-logging.conf.j2 \
    /etc/monasca/api-logging.conf
else
  cp /etc/monasca/api-config.conf.j2 /etc/monasca/api-config.conf
  cp /etc/monasca/api-config.ini.j2 /etc/monasca/api-config.ini
  cp /etc/monasca/api-logging.conf.j2 /etc/monasca/api-logging.conf
fi

gunicorn --capture-output \
  -n monasca-api \
  -k eventlet \
  --worker-connections=2000 \
  --backlog=1000 \
  --paste /etc/monasca/api-config.ini \
  -w 9
