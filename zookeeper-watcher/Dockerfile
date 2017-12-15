FROM alpine:3.6 as zookeeper-watcher-builder

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ARG WATCHER_REPO=https://github.com/monasca/monasca-watchers
ARG WATCHER_BRANCH=master

ENV GOPATH=/go
ENV PROJECT_DIR=$GOPATH/src/github.com/monasca/monasca-watchers

RUN apk add --no-cache openssl-dev git go glide g++

WORKDIR $PROJECT_DIR
RUN git init && \
    git remote add origin $WATCHER_REPO && \
    git fetch origin $WATCHER_BRANCH && \
    git reset --hard FETCH_HEAD

RUN glide install && \
    go build -o zookeeper-watcher -tags static main/zookeeper_watcher.go

FROM alpine:3.6

RUN apk add --no-cache openssl tini

COPY --from=zookeeper-watcher-builder /go/src/github.com/monasca/monasca-watchers/zookeeper-watcher /zookeeper-watcher

COPY start.sh /

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/start.sh"]
