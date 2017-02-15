#!/bin/bash

# A small script to build the kafka container against several kafka versions and
# docker hub tags.

set -e

source "$(dirname "$(dirname "$(readlink -f $0)")")/docker_build_util.sh"

# $docker_repo is referenced in docker_build_util.sh
# shellcheck disable=SC2034
docker_repo=${1:-"monasca/kafka"}

# TODO something about this build script prevents the kafka tarball from being
# downloaded successfully. Will need to build manually until solved.

build 0.9.0.1-2.11
retag 0.9.0.1-2.11 latest
