# librdkafka is not available in a stable alpine release
from alpine:edge

arg AGGREGATOR_REPO=https://github.com/monasca/monasca-aggregator
arg AGGREGATOR_BRANCH=master

env GOPATH=/go

run apk add --no-cache openssl py2-jinja2 && \
  apk add --no-cache --virtual build-dep \
    librdkafka-dev git go glide make g++ openssl-dev && \
  mkdir -p $GOPATH/src/github.com/monasca/monasca-aggregator && \
  cd $GOPATH/src/github.com/monasca/monasca-aggregator && \
  git init && \
  git remote add origin $AGGREGATOR_REPO && \
  git fetch origin $AGGREGATOR_BRANCH && \
  git reset --hard FETCH_HEAD && \
  glide install && \
  go build -tags static && \
  cp monasca-aggregator /monasca-aggregator && \
  cp aggregation-specifications.yaml / && \
  apk del build-dep && \
  cd / && \
  rm -rf /go

copy config.yaml.j2 template.py start.sh /
expose 8080

cmd ["/start.sh"]
