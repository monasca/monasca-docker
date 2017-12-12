#!/bin/sh
# (C) Copyright 2017 FUJITSU LIMITED

ELASTICSEARCH_WAIT_RETRIES=${ELASTICSEARCH_WAIT_RETRIES:-"24"}
ELASTICSEARCH_WAIT_DELAY=${ELASTICSEARCH_WAIT_DELAY:-"5"}

j2 /action.yml.j2 > /action.yml
j2 /crontab.j2 > /var/spool/cron/crontabs/curator

if [ "$WAIT_FOR_ELASTICSEARCH" = "true" ]; then
    RETRIES=$ELASTICSEARCH_WAIT_RETRIES \
      SLEEP_LENGTH=$ELASTICSEARCH_WAIT_DELAY \
      /wait-for.sh "${ELASTICSEARCH_URI}" && \
        crontab /var/spool/cron/crontabs/curator && \
        crond -f
else
    crontab /var/spool/cron/crontabs/curator && \
      crond -f
fi
