#!/bin/bash

sleep 1

admin_username=${KEYSTONE_USERNAME:-"admin"}
admin_password=${KEYSTONE_PASSWORD:-"s3cr3t"}
admin_project=${KEYSTONE_PROJECT:-"admin"}
admin_role=${KEYSTONE_ROLE:-"admin"}
admin_service=${KEYSTONE_SERVICE:-"keystone"}
admin_region=${KEYSTONE_REGION:-"RegionOne"}

if [[ "$KEYSTONE_HOST" ]]; then
    admin_url="http://${KEYSTONE_HOST}:35357"
    public_url="http://${KEYSTONE_HOST}:5000"
    internal_url="http://${KEYSTONE_HOST}:5000"
else
    admin_url=${KEYSTONE_ADMIN_URL:-"http://localhost:35357"}
    public_url=${KEYSTONE_PUBLIC_URL:-"http://localhost:5000"}
    internal_url=${KEYSTONE_INTERNAL_URL:-"http://localhost:5000"}
fi

init_db=true

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

    echo "Updating Keystone config file with mysql credentials..."
    mysql_url="mysql://$mysql_user:$mysql_pass@$mysql_host:$mysql_port/$mysql_db"
    sed -ie \
        "s~^connection = sqlite:////var/lib/keystone/keystone.db$~connection = $mysql_url~" \
        /etc/keystone/keystone.conf

    # check to see if table exists already and skip init if so
    mysql -h ${mysql_host} -u ${mysql_user} -p${mysql_pass} -e "desc ${mysql_db}.migrate_version" > /dev/null
    if [[ $? -eq 0 ]]; then
        init_db=false
    fi
fi

if [[ "$init_db" = true ]]; then
    echo "Database is empty, will perform initialization..."
    keystone-manage db_sync

    echo "Creating bootstrap credentials..."
    keystone-manage bootstrap \
        --bootstrap-password $admin_password \
        --bootstrap-username $admin_username \
        --bootstrap-project-name $admin_project \
        --bootstrap-role-name $admin_role \
        --bootstrap-service-name $admin_service \
        --bootstrap-region-id $admin_region \
        --bootstrap-admin-url $admin_url \
        --bootstrap-public-url $public_url \
        --bootstrap-internal-url $internal_url

    echo "Preloading..."
    python /preload.py
else
    echo "Database is not empty, skipping initialization."
fi

exit 0
