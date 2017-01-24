#!/bin/bash

# A small collection of functions for automating bulk docker image builds.

function build_branch() {
  branch=$1
  tag=$2

  args=()
  if [[ -n "$HTTP_PROXY" ]]; then
    args+=("--build-arg HTTP_PROXY=$HTTP_PROXY")
  fi

  if [[ -n "$HTTPS_PROXY" ]]; then
    args+=("--build-arg HTTPS_PROXY=$HTTPS_PROXY")
  fi

  docker build \
    -t ${docker_repo:?}:$tag \
    --build-arg PERSISTER_BRANCH=$branch \
    "${args[@]}" \
    .

  docker push ${docker_repo:?}/$tag
}

function retag() {
  old_tag=$1
  new_tag=$2

  docker tag ${docker_repo:?}:$old_tag $docker_repo:$new_tag
  docker push ${docker_repo:?}:$new_tag
}
