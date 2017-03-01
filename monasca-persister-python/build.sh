#!/bin/bash

# A small script to build the Python persister against several branches and
# docker hub tags.

set -e

source "$(dirname "$(dirname "$(readlink -f $0)")")/docker_build_util.sh"

# $docker_repo is referenced in docker_build_util.sh
# shellcheck disable=SC2034
docker_repo=${1:-"monasca/persister"}

build master PERSISTER_BRANCH=master
retag master master-python

build 1.4.0 PERSISTER_BRANCH=1.4.0
retag 1.4.0 1.4
retag 1.4.0 1
retag 1.4.0 1.4.0-python
retag 1.4.0 1.4-python
retag 1.4.0 1-python

build 1.3.0 PERSISTER_BRANCH=1.3.0
retag 1.3.0 1.3
retag 1.3.0 1.3.0-python
retag 1.3.0 1.3-python

build mitaka PERSISTER_BRANCH="stable/mitaka"
retag mitaka mitaka-python

build newton PERSISTER_BRANCH="stable/newton"
retag newton newton-python

retag 1.4.0 latest
retag 1.4.0 latest-python
