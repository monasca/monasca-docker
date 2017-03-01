#!/bin/bash

# A small script to build the notification engine against several branches and
# docker hub tags.

set -e

source "$(dirname "$(dirname "$(readlink -f $0)")")/docker_build_util.sh"

# $docker_repo is referenced in docker_build_util.sh
# shellcheck disable=SC2034
docker_repo=${1:-"monasca/notification"}

build master NOTIFICATION_BRANCH=master
retag master latest

# TODO: build stable branches and releases when one exists that includes
# necessary patches
