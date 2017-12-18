FROM alpine:3.6

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1
ARG WATCHER_REPO=https://github.com/monasca/monasca-watchers
ARG WATCHER_BRANCH=master

ENV GOPATH=/go
ENV PROJECT_DIR=$GOPATH/src/github.com/monasca/monasca-watchers

WORKDIR $PROJECT_DIR

RUN apk update && \
    apk add --no-cache openssl-dev openssl tini\
    git go glide g++ && \
    cd $PROJECT_DIR && \
    git init && \
    git remote add origin $WATCHER_REPO && \
    git fetch origin $WATCHER_BRANCH && \
    git reset --hard FETCH_HEAD && \
    glide install && \
    go build -o /influxdb-watcher -tags static main/influxdb_watcher.go

COPY start.sh /

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/start.sh"]
