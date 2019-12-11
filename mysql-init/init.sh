#!/bin/sh
# (C) Copyright 2017 Hewlett Packard Enterprise Development LP

MYSQL_INIT_HOST=${MYSQL_INIT_HOST:-"mysql"}
MYSQL_INIT_PORT=${MYSQL_INIT_PORT:-"3306"}
MYSQL_INIT_USERNAME=${MYSQL_INIT_USERNAME:-"root"}
MYSQL_INIT_PASSWORD=${MYSQL_INIT_PASSWORD:-"secretmysql"}
MYSQL_INIT_SCHEMA_DATABASE=${MYSQL_INIT_DATABASE:-"mysql_init_schema"}

MYSQL_INIT_WAIT_RETRIES=${MYSQL_INIT_WAIT_RETRIES:-"24"}
MYSQL_INIT_WAIT_DELAY=${MYSQL_INIT_WAIT_DELAY:-"5"}

USER_SCRIPTS="/mysql-init.d"
UPGRADE_SCRIPTS="/mysql-upgrade.d"

wait_mysql() {
  echo "Waiting for MySQL to become available..."
  success="false"
  for i in $(seq "$MYSQL_INIT_WAIT_RETRIES"); do
    if mysqladmin status \
        --host="$MYSQL_INIT_HOST" \
        --port="$MYSQL_INIT_PORT" \
        --user="$MYSQL_INIT_USERNAME" \
        --password="$MYSQL_INIT_PASSWORD" \
        --connect_timeout=10; then
      echo "MySQL is available, continuing..."
      success="true"
      break
    else
      echo "Connection attempt $i of $MYSQL_INIT_WAIT_RETRIES failed"
      sleep "$MYSQL_INIT_WAIT_DELAY"
    fi
  done

  if [ "$success" != "true" ]; then
      echo "Unable to reach MySQL database! Exiting..."
      sleep 1
      exit 1
  fi
}

clean_install() {
  echo "MySQL has not yet been initialized. Initial schemas will be applied."

  set -e

  for f in "$USER_SCRIPTS"/*.sql.j2; do
    if [ -e "$f" ]; then
      echo "Applying template: $f"
      python /template.py "$f" "$USER_SCRIPTS/$(basename "$f" .j2)"
    fi
  done

  for f in "$USER_SCRIPTS"/*.sql; do
    # SQL files with zero length are ignored
    if [ -s "$f" ]; then
      echo "Running script: $f"
      mysql --host="$MYSQL_INIT_HOST" \
          --user="$MYSQL_INIT_USERNAME" \
          --port="$MYSQL_INIT_PORT" \
          --password="$MYSQL_INIT_PASSWORD" < "$f"
    fi
  done

  if [ -n "$MYSQL_INIT_SET_PASSWORD" ]; then
    echo "Updating password for $MYSQL_INIT_USERNAME..."

    set +x
    mysqladmin password \
        --host="$MYSQL_INIT_HOST" \
        --port="$MYSQL_INIT_PORT" \
        --user="$MYSQL_INIT_USERNAME" \
        --password="$MYSQL_INIT_PASSWORD" \
        "$MYSQL_INIT_SET_PASSWORD"
  elif [ "$MYSQL_INIT_RANDOM_PASSWORD" = "true" ]; then
    echo "Resetting $MYSQL_INIT_USERNAME password..."

    set +x
    pw=$(pwgen -1 32)
    mysqladmin password \
        --host="$MYSQL_INIT_HOST" \
        --port="$MYSQL_INIT_PORT" \
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
        --port="$MYSQL_INIT_PORT" \
        --password="$MYSQL_INIT_PASSWORD" < /disable-remote-root.sql
  fi
}

schema_upgrade() {
  version="$1"

  # ash doesn't support arrays, this seems to be the most concise way to get
  # fields by index

  # shellcheck disable=SC2086
  set $version
  if [ "$#" -ne "3" ]; then
    echo "Invalid version: '$version'"
    sleep 1
    exit 1
  fi
  c_major=$1
  c_minor=$2
  c_patch=$3
  echo "Upgrading MySQL, current version: major=$c_major minor=$c_minor patch=$c_patch"

  any_applied="false"
  last_major=$c_major
  last_minor=$c_minor
  last_patch=$c_patch
  # shellcheck disable=SC2012
  for diff_version in $(ls $UPGRADE_SCRIPTS | sort -V); do
    if [ ! -d "$UPGRADE_SCRIPTS/$diff_version" ]; then
      echo "Ignoring: $UPGRADE_SCRIPTS/$diff_version"
      continue
    fi

    # we explicitly want to word-split here...
    # shellcheck disable=SC2046
    set $(echo "$diff_version" | tr '.' ' ')
    if [ "$#" -ne "3" ]; then
      echo "Invalid version number in upgrade directory, quitting! $diff_version"
      sleep 1
      exit 1
    fi

    d_major=$1
    d_minor=$2
    d_patch=$3

    if [ "$d_major" -le "$c_major" ] && [ "$d_minor" -le "$c_minor" ] && [ "$d_patch" -le "$c_patch" ]; then
      echo "Skipping update $diff_version (too old)"
      continue
    fi

    if [ "$d_major" -gt "$c_major" ] && [ "$d_minor" -gt "$c_minor" ] && [ "$d_patch" -gt "$c_patch" ]; then
      echo "Warning: update too new: $diff_version. This update will not be applied!"
      echo "Make sure to update SCHEMA_MAJOR_REV, SCHEMA_MINOR_REV, and SCHEMA_PATCH_REV!"
      echo "No futher updates will be applied."
      break
    fi

    echo "Applying update: $diff_version"

    for f in "$UPGRADE_SCRIPTS"/"$diff_version"/*.sql.j2; do
      if [ -e "$f" ]; then
        echo "Applying template: $f"
        python /template.py "$f" "$UPGRADE_SCRIPTS/$diff_version/$(basename "$f" .j2)"
      fi
    done

    for f in "$UPGRADE_SCRIPTS"/"$diff_version"/*.sql; do
      # SQL files with zero length are ignored
      if [ -s "$f" ]; then
        echo "Running script: $f"
        set +x
        mysql --host="$MYSQL_INIT_HOST" \
            --user="$MYSQL_INIT_USERNAME" \
            --port="$MYSQL_INIT_PORT" \
            --password="$MYSQL_INIT_PASSWORD" < "$f"
        set -x
        any_applied="true"
      fi
    done

    last_major=$d_major
    last_minor=$d_minor
    last_patch=$d_patch
  done

  if [ "$any_applied" = "true" ]; then
    database=${MYSQL_INIT_SCHEMA_DATABASE:-"mysql_init_schema"}
    echo "Recording version in $database: $last_major.$last_minor.$last_patch"
    query="insert into schema_version (major, minor, patch) values ($last_major, $last_minor, $last_patch);"
    set +x
    echo "$query" | mysql \
        --host="$MYSQL_INIT_HOST" \
        --user="$MYSQL_INIT_USERNAME" \
        --port="$MYSQL_INIT_PORT" \
        --password="$MYSQL_INIT_PASSWORD" \
        "$database"
    set -x
    echo "Finished applying updates."
  else
    echo "No updates to apply!"
  fi


}

wait_mysql
query="select major, minor, patch from schema_version order by id desc limit 1;"
if version=$(echo "$query" | mysql \
    --host="$MYSQL_INIT_HOST" \
    --user="$MYSQL_INIT_USERNAME" \
    --port="$MYSQL_INIT_PORT" \
    --password="$MYSQL_INIT_PASSWORD" \
    --silent \
    "$MYSQL_INIT_SCHEMA_DATABASE"); then
  schema_upgrade "$version"
else
  clean_install
fi

echo "mysql-init exiting successfully"
return 0
