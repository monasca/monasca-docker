#!/bin/bash
set -e

sleep 5

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

if [[ "$KUBERNETES_RESOLVE_PUBLIC_ENDPOINTS" = "true" ]]; then
    keystone_service_name=${KEYSTONE_SERVICE_NAME:-"keystone"}
    if service_url=$(python /k8s_get_service.py "${keystone_service_name}" http); then
        public_url="http://${service_url}"
    else
        echo "ERROR: Failed to get public URL from Kubernetes API!"
    fi

    if service_admin_url=$(python /k8s_get_service.py "${keystone_service_name}" admin); then
      admin_url="http://${service_admin_url}"
    else
      # not ERROR since this is somewhat less fatal
      echo "WARNING: Failed to get admin URL from Kubernetes API!"
    fi
fi

if [[ -e /db-init ]]; then
    echo "Creating bootstrap credentials..."
    keystone-manage bootstrap \
        --bootstrap-password "$admin_password" \
        --bootstrap-username "$admin_username" \
        --bootstrap-project-name "$admin_project" \
        --bootstrap-role-name "$admin_role" \
        --bootstrap-service-name "$admin_service" \
        --bootstrap-region-id "$admin_region" \
        --bootstrap-admin-url "$admin_url" \
        --bootstrap-public-url "$public_url" \
        --bootstrap-internal-url "$internal_url"

    sleep 5

    echo "Waiting for keystone to become available at $admin_url..."
    success=false
    for i in {1..10}; do
        if curl -sSf "$admin_url" > /dev/null; then
            echo "Keystone API is up, continuing..."
            success=true
            break
        else
            echo "Connection to keystone failed, attempt #$i of 10"
            sleep 1
        fi
    done

    if [[ "$success" = false ]]; then
        echo "Connection failed after max retries, preload may fail!"
    fi

    echo "Preloading..."
    python /preload.py
else
    echo "Database is not empty, skipping initialization."
fi

exit 0
