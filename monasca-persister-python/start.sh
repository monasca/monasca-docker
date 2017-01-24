#!/bin/sh

if [ "$CONFIG_TEMPLATE" = "true" ]; then
  python template.py \
    /etc/monasca-persister/persister.conf.j2 \
    /etc/monasca-persister/persister.conf
else
  cp /etc/monasca-persister/persister.conf.j2 /etc/monasca-persister/persister.conf
fi

python /usr/lib/python2.7/site-packages/monasca_persister/persister.py \
  --config-file /etc/monasca-persister/persister.conf
