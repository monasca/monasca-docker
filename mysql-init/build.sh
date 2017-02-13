#!/bin/bash

# A small script to build the mysql-init container against several docker hub
# tags.

set -e

source "$(dirname "$(dirname "$(readlink -f $0)")")/docker_build_util.sh"

# $docker_repo is referenced in docker_build_util.sh
# shellcheck disable=SC2034
docker_repo=${1:-"monasca/mysql-init"}

build 1.0.0
retag 1.0.0 1.0
retag 1.0.0 1
retag 1.0.0 latest
