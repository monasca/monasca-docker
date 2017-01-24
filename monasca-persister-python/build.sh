#!/bin/bash

# A small script to build the Python persister against several branches and
# docker hub tags.

set -e

source "$(dirname "$(dirname "$(readlink -f $0)")")/docker_build_util.sh"

# $docker_repo is referenced in docker_build_util.sh
# shellcheck disable=SC2034
docker_repo=${1:-"monasca/persister"}

build_branch master master
retag master master-python

build_branch 1.3.0 1.3.0
retag 1.3.0 1.3
retag 1.3.0 1
retag 1.3.0 1.3.0-python
retag 1.3.0 1.3-python
retag 1.3.0 1-python

build_branch "stable/mitaka" mitaka
retag mitaka mitaka-python

build_branch "stable/newton" newton
retag newton newton-python
