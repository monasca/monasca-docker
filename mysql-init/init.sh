#!/bin/sh
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

set -x

MYSQL_INIT_HOST=${MYSQL_INIT_HOST:-"mysql"}
MYSQL_INIT_PORT=${MYSQL_INIT_PORT:-"3306"}
MYSQL_INIT_USERNAME=${MYSQL_INIT_USERNAME:-"root"}
MYSQL_INIT_PASSWORD=${MYSQL_INIT_PASSWORD:-"secretmysql"}

USER_SCRIPTS="/mysql-init.d"

mysqladmin ping \
    --host="$MYSQL_INIT_HOST" \
    --port=$MYSQL_INIT_PORT \
    --user="$MYSQL_INIT_USERNAME" \
    --password="$MYSQL_INIT_PASSWORD" \
    --wait=10
if [ $? -ne 0 ]; then
  echo "Unable to reach MySQL, exiting..."
  sleep 1
  exit 1
fi

for f in $USER_SCRIPTS/*.sql; do
  if [ -e "$f" ]; then
    echo "Running script: $f"
    mysql --host="$MYSQL_INIT_HOST" \
        --user="$MYSQL_INIT_USERNAME" \
        --port=$MYSQL_INIT_PORT \
        --password="$MYSQL_INIT_PASSWORD" < "$f"
  fi
done
