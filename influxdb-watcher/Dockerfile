# librdkafka is not available in a stable alpine release
FROM alpine:edge as influxdb-watcher-builder

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ARG WATCHER_REPO=https://github.com/monasca/monasca-watchers
ARG WATCHER_BRANCH=master

ENV GOPATH=/go
ENV PROJECT_DIR=$GOPATH/src/github.com/monasca/monasca-watchers
ENV INFLUXDB_ADDRESS=http://goodly-alligator-influxdb:8086

RUN apk add --no-cache openssl-dev \
      git go glide g++

WORKDIR $PROJECT_DIR
RUN git init && \
    git remote add origin $WATCHER_REPO && \
    git fetch origin $WATCHER_BRANCH && \
    git reset --hard FETCH_HEAD


RUN cd $PROJECT_DIR && \
    glide install && \
    go build -o influxdb-watcher -tags static main/influxdb_watcher.go

FROM alpine:3.6

ENV INFLUXDB_ADDRESS=http://goodly-alligator-influxdb:8086

RUN apk add --no-cache openssl tini

COPY --from=influxdb-watcher-builder /go/src/github.com/monasca/monasca-watchers/influxdb-watcher /influxdb-watcher

COPY start.sh /

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/start.sh"]
