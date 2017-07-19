#!/bin/bash

# A small script to build the Python API against several branches and
# docker hub tags.

set -e

source "$(dirname "$(dirname "$(readlink -f $0)")")/docker_build_util.sh"

# constraints
CONSTRAINTS_OCATA=stable/ocata

# $docker_repo is referenced in docker_build_util.sh
# shellcheck disable=SC2034
docker_repo=${1:-"kornicameister/log-api"}

build master LOG_API_BRANCH=master
build ocata LOG_API_BRANCH=stable/ocata CONSTRAINTS_BRANCH=$CONSTRAINTS_OCATA

# releases
build 2.2.1 LOG_API_BRANCH=2.2.1
build 2.1.0 LOG_API_BRANCH=2.1.0
build 2.0.0 LOG_API_BRANCH=2.0.0
build 1.4.1 LOG_API_BRANCH=1.4.1 CONSTRAINTS_BRANCH=$CONSTRAINTS_OCATA

# latest release
retag 2.2.1 latest
