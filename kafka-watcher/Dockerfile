# librdkafka is not available in a stable alpine release
from alpine:edge

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

arg WATCHER_REPO=https://github.com/monasca/monasca-watchers
arg WATCHER_BRANCH=master

env GOPATH=/go

run apk add --no-cache openssl py2-jinja2 && \
  apk add --no-cache --virtual build-dep \
    librdkafka-dev git go glide make g++ openssl-dev && \
  mkdir -p $GOPATH/src/github.com/monasca/monasca-watchers && \
  cd $GOPATH/src/github.com/monasca/monasca-watchers && \
  git init && \
  git remote add origin $WATCHER_REPO && \
  git fetch origin $WATCHER_BRANCH && \
  git reset --hard FETCH_HEAD && \
  glide install && \
  go build -o kafka-watcher -tags static main/kafka_watcher.go && \
  cp kafka-watcher / && \
  apk del build-dep && \
  cd / && \
  rm -rf $GOPATH

cmd ["/kafka-watcher"]
