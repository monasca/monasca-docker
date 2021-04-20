#!/bin/sh

# shellcheck disable=SC1091
. /root/.keystonerc

if [ -t 1 ]; then
    echo "Press enter to continue..."

    # shellcheck disable=SC2162
    read

    echo ""
    echo "Usage:"
    echo "  secret    <secret name>  - load a different secret"
    echo "  shell     [secret name]  - open a python shell with keystone and k8s clients"
    echo "  openstack [...]          - use the openstack client"
    echo "  monasca   [...]          - use the monasca client"
    echo ""

    if [ -n "$KEYSTONE_SECRET" ]; then
        secret "$KEYSTONE_SECRET"
    fi

    if [ -n "$KEYSTONE_SHELL" ]; then
        shell
    else
        sh -l
    fi
else
    if [ -n "$KEYSTONE_SECRET" ]; then
        if ! secret "$KEYSTONE_SECRET"; then
            echo "Could not find secret: $KEYSTONE_SECRET"
            sleep 5
            exit 1
        fi

        if python -c "import keystone_shell_vars; keystone_shell_vars.get_keystone_client()"; then
            echo "Keystone connection successful!"
            sleep 1
            exit 0
        else
            echo "Could not connect to keystone!"
            sleep 5
            exit 1
        fi
    else
        echo "No \$KEYSTONE_SECRET defined, nothing to do!"
        echo "Either run interactively (-i -t) or specify \$KEYSTONE_SECRET"
        echo "to verify connection."
        sleep 5
        exit 0
    fi
fi
