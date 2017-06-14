#!/bin/bash

# A small script to build the agent against several branches and docker hub
# tags.

set -e

source "$(dirname "$(dirname "$(readlink -f $0)")")/docker_build_util.sh"

# $docker_repo is referenced in docker_build_util.sh
# shellcheck disable=SC2034
docker_repo=${1:-"monasca/agent-base"}

build master AGENT_BRANCH=master
retag master latest

# TODO: build stable agent branches and releases when one exists that includes
# necessary plugins (docker, k8s, k8s api, etc)
