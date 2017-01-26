#!/bin/bash

# A small script to build the Python API against several branches and
# docker hub tags.

set -e

source "$(dirname "$(dirname "$(readlink -f $0)")")/docker_build_util.sh"

# $docker_repo is referenced in docker_build_util.sh
# shellcheck disable=SC2034
docker_repo=${1:-"monasca/api"}

build master API_BRANCH=master
retag master master-python
retag master latest
retag master latest-python

# TODO: build stable API branches and releases when one exists that will work
# with the provided config files
