#!/bin/sh

set -x

OPTS=`getopt -n 'parse-options' -o r:b:e:d:c: --l repo:branch:extras:deps: -- "$@"`
if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 1 ; fi

echo "$OPTS"
eval set -- "$OPTS"

while true; do
    case "${1}" in
        -r | --repo) REPO=${2}; shift 2 ;;
        -b | --branch) BRANCH=${2}; shift 2 ;;
        -e | --extras) EXTRAS=${2}; shift 2 ;;
        -d | --deps) EXTRA_DEPS=${2}; shift 2 ;;
        -c) CONSTRAINTS=${2}; shift 2 ;;
        -- ) shift; break ;;
        * ) break ;;
    esac
done

function install() {
    if [[ "${EXTRA_DEPS}" != "?" ]]; then
        for extra in ${EXTRA_DEPS:-""}; do
            pip install --no-cache-dir $extra -c $CONSTRAINTS
        done
    fi
    if [[ "${EXTRAS}" != "?" ]]; then
        for extra in ${EXTRAS:-""}; do
            pip install --no-cache-dir .[${extra}] -c $CONSTRAINTS
        done
    fi
    pip install --no-cache-dir . -c $CONSTRAINTS
}

function clone() {
    git init
    git remote add origin $REPO
    git fetch origin $BRANCH
    git reset --hard FETCH_HEAD
}

function print_env() {
    cat << EOF
Build environment:
PROJECT=${REPO}@${BRANCH}
EXTRAS=${EXTRAS}
CONSTRAINTS=${CONSTRAINTS}
EXTRA_DEPENDENCIES=${EXTRA_DEPS}
EOF
}

if [ -n "$REPO" ] && [ -n "$BRANCH" ]; then
    print_env
    clone
    install
fi
