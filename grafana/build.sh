#!/bin/bash

# A small script to build the grafana against several branches and
# docker hub tags.

set -e

source "$(dirname "$(dirname "$(readlink -f $0)")")/docker_build_util.sh"

# $docker_repo is referenced in docker_build_util.sh
# shellcheck disable=SC2034
docker_repo=${1:-"monasca/grafana"}

build 4.1.0-pre1-1.0.0
retag 4.1.0-pre1-1.0.0 latest
