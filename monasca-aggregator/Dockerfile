from golang:1.10.3-alpine3.8 as builder

arg AGGREGATOR_REPO=https://github.com/monasca/monasca-aggregator
arg AGGREGATOR_BRANCH=master

arg GLIDE_PATH=src/github.com/Masterminds/glide

env GOPATH=/go

run apk add --no-cache \
        git \
        g++ \
        librdkafka-dev \
        libressl-dev \
        make \
        py2-jinja2

run git clone https://github.com/Masterminds/glide.git $GOPATH/$GLIDE_PATH && \
  cd $GOPATH/$GLIDE_PATH && \
  git checkout tags/v0.13.1 && \
  make install

run mkdir -p $GOPATH/src/github.com/monasca/monasca-aggregator && \
  cd $GOPATH/src/github.com/monasca/monasca-aggregator && \
  git init && \
  git remote add origin $AGGREGATOR_REPO && \
  git fetch origin $AGGREGATOR_BRANCH && \
  git reset --hard FETCH_HEAD && \
  glide install && \
  go build

from alpine:3.8

run apk add --no-cache \
        libressl \
        librdkafka-dev \
        py2-jinja2

copy --from=builder /go/src/github.com/monasca/monasca-aggregator/monasca-aggregator /
copy --from=builder /go/src/github.com/monasca/monasca-aggregator/aggregation-specifications.yaml /specs/aggregation-specifications.yaml

copy template.py start.sh /
copy config.yaml.j2 /config/config.yaml.j2
expose 8080

cmd ["/start.sh"]
