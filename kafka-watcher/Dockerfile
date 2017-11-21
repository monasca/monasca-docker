# librdkafka is not available in a stable alpine release
from alpine:edge as kafka-watcher-builder

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ARG WATCHER_REPO=https://github.com/monasca/monasca-watchers
ARG WATCHER_BRANCH=master

ENV GOPATH=/go
ENV PROJECT_DIR=$GOPATH/src/github.com/monasca/monasca-watchers

RUN apk add --no-cache openssl py2-jinja2

RUN apk add --no-cache --virtual build-dep librdkafka-dev \
      git go glide make g++ openssl-dev

WORKDIR $PROJECT_DIR
RUN git init && \
    git remote add origin $WATCHER_REPO && \
    git fetch origin $WATCHER_BRANCH && \
    git reset --hard FETCH_HEAD

RUN glide install && \
    go build -o kafka-watcher -tags static main/kafka_watcher.go

FROM alpine:3.6

RUN apk add --no-cache tini

COPY --from=kafka-watcher-builder $PROJECT_DIR/kafka-watcher /kafka-watcher

COPY start.sh /

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/start.sh"]
