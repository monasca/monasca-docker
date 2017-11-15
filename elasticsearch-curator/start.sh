#!/bin/sh
# (C) Copyright 2017 FUJITSU LIMITED

ELASTICSEARCH_WAIT_RETRIES=${ELASTICSEARCH_WAIT_RETRIES:-"24"}
ELASTICSEARCH_WAIT_DELAY=${ELASTICSEARCH_WAIT_DELAY:-"5"}

/p2 -t /action.yml.j2 -i actions.yml > /action.yml

if [ "$WAIT_FOR_ELASTICSEARCH" = "true" ]; then
    RETRIES=$ELASTICSEARCH_WAIT_RETRIES \
      SLEEP_LENGTH=$ELASTICSEARCH_WAIT_DELAY \
      /wait-for.sh "${ELASTICSEARCH_URI}" && crond -f
else
    crond -f
fi
