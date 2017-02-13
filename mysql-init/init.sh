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
    --connect_timeout=10 \
    --wait=10
if [ $? -ne 0 ]; then
  echo "Unable to reach MySQL, exiting..."
  sleep 1
  exit 1
fi

set -e

for f in $USER_SCRIPTS/*.sql; do
  if [ -e "$f" ]; then
    echo "Running script: $f"
    mysql --host="$MYSQL_INIT_HOST" \
        --user="$MYSQL_INIT_USERNAME" \
        --port=$MYSQL_INIT_PORT \
        --password="$MYSQL_INIT_PASSWORD" < "$f"
  fi
done

if [ -n "$MYSQL_INIT_SET_PASSWORD" ]; then
  echo "Updating password for $MYSQL_INIT_USERNAME..."

  set +x
  mysqladmin password \
      --host="$MYSQL_INIT_HOST" \
      --port=$MYSQL_INIT_PORT \
      --user="$MYSQL_INIT_USERNAME" \
      --password="$MYSQL_INIT_PASSWORD" \
      "$MYSQL_INIT_SET_PASSWORD"
elif [ "$MYSQL_INIT_RANDOM_PASSWORD" = "true" ]; then
  echo "Resetting $MYSQL_INIT_USERNAME password..."

  set +x
  pw=$(pwgen -1 32)
  mysqladmin password \
      --host="$MYSQL_INIT_HOST" \
      --port=$MYSQL_INIT_PORT \
      --user="$MYSQL_INIT_USERNAME" \
      --password="$MYSQL_INIT_PASSWORD" \
      "$pw"
  echo "GENERATED $MYSQL_INIT_USERNAME PASSWORD: $pw"
  MYSQL_INIT_PASSWORD="$pw"
fi

if [ "$MYSQL_INIT_DISABLE_REMOTE_ROOT" = "true" ]; then
  echo "Disabling remote root login..."
  mysql --host="$MYSQL_INIT_HOST" \
      --user="$MYSQL_INIT_USERNAME" \
      --port=$MYSQL_INIT_PORT \
      --password="$MYSQL_INIT_PASSWORD" < /disable-remote-root.sql
fi

echo "mysql-init exiting successfully"
