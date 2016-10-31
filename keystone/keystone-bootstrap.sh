#!/bin/bash

sleep 1

admin_username=${KEYSTONE_USERNAME:-"admin"}
admin_password=${KEYSTONE_PASSWORD:-"s3cr3t"}
admin_project=${KEYSTONE_PROJECT:-"admin"}
admin_role=${KEYSTONE_ROLE:-"admin"}
admin_service=${KEYSTONE_SERVICE:-"keystone"}
admin_region=${KEYSTONE_REGION:-"RegionOne"}

admin_url=${KEYSTONE_ADMIN_URL:-"http://localhost:35357"}
public_url=${KEYSTONE_PUBLIC_URL:-"http://localhost:5000"}
internal_url=${KEYSTONE_INTERNAL_URL:-"http://localhost:5000"}

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

exit 0
