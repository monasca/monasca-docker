FROM alpine:3.5

arg SMOKE_TEST_REPO=https://github.com/monasca/smoke-test
arg SMOKE_TEST_BRANCH=master

env GOPATH=/go

run apk add --no-cache --virtual build-dep \
    git go musl-dev && \
  apk add --no-cache ca-certificates && \
  mkdir -p $GOPATH/src/github.com/monasca/smoke-test && \
  cd $GOPATH/src/github.com/monasca/smoke-test && \
  git init && \
  git remote add origin $SMOKE_TEST_REPO && \
  git fetch origin $SMOKE_TEST_BRANCH && \
  git reset --hard FETCH_HEAD && \
  go get && \
  go build -tags static && \
  cp smoke-test /smoke-test && \
  apk del build-dep && \
  cd / && \
  rm -rf /go

copy start.sh /
expose 8080

cmd ["/start.sh"]
