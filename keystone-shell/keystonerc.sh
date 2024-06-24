#!/bin/sh

secret() {
    if [ "$#" -ne 1 ]; then
        echo "A secret name is required."
        echo "Usage: secret <name>"
        return 1
    fi

    eval "$(python /keystone_shell_vars.py "$1")"
}

shell() {
    if [ "$#" -eq 1 ]; then
        eval "$(python /keystone_shell_vars.py "$1")"
    fi

    LD_PRELOAD=/stack-fix.so ptipython -i /ptpython_init.py
}
