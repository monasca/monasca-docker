FROM alpine:3.5

arg ALARM_CONTROLLER_REPO=https://github.com/monasca/alarm-definition-controller
arg ALARM_CONTROLLER_BRANCH=master

env GOPATH=/go

run apk add --no-cache --virtual build-dep \
    git go musl-dev && \
  mkdir -p $GOPATH/src/github.com/monasca/alarm-definition-controller && \
  cd $GOPATH/src/github.com/monasca/alarm-definition-controller && \
  git init && \
  git remote add origin $ALARM_CONTROLLER_REPO && \
  git fetch origin $ALARM_CONTROLLER_BRANCH && \
  git reset --hard FETCH_HEAD && \
  go get && \
  go build -tags static && \
  cp alarm-definition-controller /alarm-definition-controller && \
  apk del build-dep && \
  cd / && \
  rm -rf /go

copy start.sh /

cmd ["/start.sh"]
