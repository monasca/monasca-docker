#!/bin/bash

# A small script to build the Python API against several branches and
# docker hub tags.

set -e

source "$(dirname "$(dirname "$(readlink -f $0)")")/docker_build_util.sh"

# constraints
CONSTRAINTS_BASE=https://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt
CONSTRAINTS_OCATA=$CONSTRAINTS_BASE?h=stable/ocata
CONSTRAINTS_MITAKA=$CONSTRAINTS_BASE?h=stable/mitaka
CONSTRAINTS_NEWTON=$CONSTRAINTS_BASE?h=stable/newton

# $docker_repo is referenced in docker_build_util.sh
# shellcheck disable=SC2034
docker_repo=${1:-"kornicameister/monasca-log-api"}

build master LOG_API_BRANCH=master

build ocata LOG_API_BRANCH=stable/ocata CONSTRAINTS_FILE=$CONSTRAINTS_OCATA
build newton LOG_API_BRANCH=stable/newton CONSTRAINTS_FILE=$CONSTRAINTS_NEWTON
build mitaka LOG_API_BRANCH=stable/mitaka CONSTRAINTS_FILE=$CONSTRAINTS_MITAKA

# releases
build 2.1.0 LOG_API_BRANCH=2.1.0
build 2.0.0 LOG_API_BRANCH=2.0.0
build 1.4.1 LOG_API_BRANCH=1.4.1 CONSTRAINTS_FILE=$CONSTRAINTS_OCATA

# latest release
retag 2.1.0 latest
