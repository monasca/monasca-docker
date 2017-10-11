ARG PYTHON_VERSION="2"
ARG ALPINE_VERSION="3.6"

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

COPY build.sh stack-fix.c entrypoint.sh /
RUN chmod +x /build.sh && \
  chmod +x /entrypoint.sh

RUN apk add --no-cache ca-certificates tini && \
  apk add --no-cache --virtual build-dep musl-dev linux-headers git make g++ linux-headers && \
  gcc -shared -fPIC /stack-fix.c -o /stack-fix.so && \
  apk del build-dep

ENTRYPOINT ["/entrypoint.sh"]
