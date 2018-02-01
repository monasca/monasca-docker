#!/bin/sh

secret() {
    eval "$(python /keystone_shell_vars.py "$1")"
}

shell() {
    if [ "$#" -ne 1 ]; then
        eval "$(python /keystone_shell_vars.py "$1")"
    fi

    LD_PRELOAD=/stack-fix.so ptipython -i /ptpython_init.py
}
