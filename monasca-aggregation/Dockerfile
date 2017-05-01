# librdkafka is not available in a stable alpine release
from alpine:edge

arg AGGREGATION_REPO=https://github.com/monasca/monasca-aggregator
arg AGGREGATION_BRANCH=master

env GOPATH=/go

run echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories && \
  apk add --no-cache openssl py2-jinja2 && \
  apk add --no-cache --virtual build-dep \
    librdkafka-dev git go make g++ openssl-dev && \
  mkdir -p $GOPATH/src/github.com/monasca/monasca-aggregator && \
  cd $GOPATH/src/github.com/monasca/monasca-aggregator && \
  git init && \
  git remote add origin $AGGREGATION_REPO && \
  git fetch origin $AGGREGATION_BRANCH && \
  git reset --hard FETCH_HEAD && \
  go get && \
  go build -tags static && \
  cp monasca-aggregation /monasca-aggregation && \
  cp aggregation-specifications.yaml / && \
  apk del build-dep && \
  cd / && \
  rm -rf /go

copy config.yaml.j2 template.py start.sh /
expose 8080

cmd ["/start.sh"]
