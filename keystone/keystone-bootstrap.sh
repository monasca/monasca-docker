#!/bin/bash
set -e

# wait for keystone API to come up
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

if [[ -e /db-init ]]; then
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
