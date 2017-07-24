#!/bin/sh

set -x

REPO="${1}"
BRANCH="${2}"

# list of extras i.e. monasca-agent['libvirt']
EXTRAS="${3:-'-1'}"

# extra dependencies not listed anywhere in project
# neither in requirements not in setup.cfg extras
EXTRA_DEPS="${4:-'-1'}"

# requirements file for given OpenStack release
CONSTRAINTS_FILE="${5}"

function install() {
    git init
    git remote add origin $REPO
    git fetch origin $BRANCH
    git reset --hard FETCH_HEAD

    if [ $EXTRA_DEPS != -1 ]; then
        pip install --no-cache-dir $EXTRA_DEPS -c $CONSTRAINTS_FILE
    fi
    if [ $EXTRA != -1 ]; then
        for extra in $EXTRA[@]; do
            pip install --no-cache-dir .[${extra}] -c $CONSTRAINTS_FILE
        done
    fi

    pip install --no-cache-dir -r requirements.txt -c $CONSTRAINTS_FILE
    pip install --no-cache-dir . -c $CONSTRAINTS_FILE
}

function print_env() {
    cat << EOF
Build environment:
PROJECT=${REPO}@${BRANCH}
EXTRA=${EXTRA}
CONSTRAINTS=${CONSTRAINTS_FILE}
EXTRA_DEPENDENCIES=${EXTRA_DEPS}
EOF
}

if [ -n "$REPO" ] && [ -n "$BRANCH" ]; then
    print_env
    install
fi
