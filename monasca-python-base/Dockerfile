FROM alpine:3.6

ARG REPO=""
ARG BRANCH=master

ARG EXTRA_DEPS=-1
ARG EXTRAS=-1

ARG CONSTRAINTS_BRANCH=master
ARG CONSTRAINTS_FILE=https://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?h=$CONSTRAINTS_BRANCH

ARG PYTHON_VERSION=2

WORKDIR /
COPY install_app.sh /

RUN apk add --no-cache python${PYTHON_VERSION} py${PYTHON_VERSION}-pip py${PYTHON_VERSION}-jinja2 curl && \
  apk add --no-cache --virtual build-dep python${PYTHON_VERSION}-dev git make g++ linux-headers && \
  mkdir -p /app && cd /app && \
  chmod +x /install_app.sh && \
  sh /install_app.sh ${REPO} ${BRANCH} ${EXTRAS} ${EXTRA_DEPS} ${CONSTRAINTS_FILE} && \
  cd / && \
  rm -rf /app /install_app.sh && \
  apk del build-dep
