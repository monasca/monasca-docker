#!/bin/bash

if [[ "$KEYSTONE_DATABASE_BACKEND" =  "mysql" ]]; then
    mysql_host=${KEYSTONE_MYSQL_HOST:-"keystone-mysql"}
    mysql_port=${KEYSTONE_MYSQL_TCP_PORT:-"3306"}
    mysql_user=${KEYSTONE_MYSQL_USER:-"keystone"}
    mysql_pass=${KEYSTONE_MYSQL_PASSWORD:-"keystone"}
    mysql_db=${KEYSTONE_MYSQL_DATABASE:-"keystone"}

    echo "Waiting for mysql to become available..."
    mysqladmin ping \
        --host="$mysql_host" \
        --user="$mysql_user" \
        --password="$mysql_pass" \
        --wait=5
    if [[ $? -ne 0 ]]; then
        echo "Unable to reach MySQL database! Exiting..."
        sleep 1
        exit 1
    fi

    echo "Updating Keystone config file with mysql credentials..."
    mysql_url="mysql://$mysql_user:$mysql_pass@$mysql_host:$mysql_port/$mysql_db"
    sed -ie \
        "s~^connection = sqlite:////var/lib/keystone/keystone.db$~connection = $mysql_url~" \
        /etc/keystone/keystone.conf

    # check to see if table exists already and skip init if so
    mysql -h ${mysql_host} -u ${mysql_user} -p${mysql_pass} -e "desc ${mysql_db}.migrate_version" &> /dev/null
    if [[ $? -eq 0 ]]; then
        echo "MySQL database has already been initialized, skipping..."
    else
        echo "Syncing keystone database to MySQL..."
        keystone-manage db_sync
        touch /db-init
    fi
else
    echo "Syncing keystone database to sqlite..."
    keystone-manage db_sync
    touch /db-init
fi

supervisord --nodaemon -c /etc/supervisor/supervisord.conf

if [[ -e /kill-supervisor ]]; then
    echo "Exiting uncleanly due to bootstrap failure!"
    exit 1
else
    echo "Existing cleanly..."
    exit 0
fi
