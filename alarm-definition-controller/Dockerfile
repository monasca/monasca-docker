FROM alpine:3.6 as go-builder

ARG ADC_REPO=https://github.com/monasca/alarm-definition-controller
ARG ADC_BRANCH=master

ENV GOPATH=/go CGO_ENABLED=0 GOOS=linux

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

RUN apk add --no-cache git go glide make g++ openssl-dev musl-dev
RUN mkdir -p $GOPATH/src/github.com/monasca/alarm-definition-controller

WORKDIR $GOPATH/src/github.com/monasca/alarm-definition-controller

RUN git init && \
    git remote add origin $ADC_REPO && \
    git fetch origin $ADC_BRANCH && \
    git reset --hard FETCH_HEAD

RUN glide install && \
    go build -a -o ./adc

FROM alpine:3.6

RUN apk add --no-cache ca-certificates tini

COPY --from=go-builder \
    /go/src/github.com/monasca/alarm-definition-controller/adc \
    /adc

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/adc"]
