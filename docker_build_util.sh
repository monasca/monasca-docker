#!/bin/bash

# A small collection of functions for automating bulk docker image builds.

# usage: build tag build_arg...
# uses global $docker_repo
function build() {
  tag=$1
  shift

  args=()
  for arg in "$@"; do
    args+=("--build-arg $arg")
  done

  if [[ -n "$HTTP_PROXY" ]]; then
    args+=("--build-arg HTTP_PROXY=$HTTP_PROXY")
  fi

  if [[ -n "$HTTPS_PROXY" ]]; then
    args+=("--build-arg HTTPS_PROXY=$HTTPS_PROXY")
  fi

  echo docker build \
    -t ${docker_repo:?}:$tag \
    "${args[@]}" \
    .

  echo docker push ${docker_repo:?}:$tag
}

# usage: retag [old tag] [new tag]
# uses global $docker_repo
function retag() {
  old_tag=$1
  new_tag=$2

  echo docker tag ${docker_repo:?}:$old_tag $docker_repo:$new_tag
  echo docker push ${docker_repo:?}:$new_tag
}
