FROM alpine:3.5

ARG FORWARDER_REPO=https://github.hpe.com/UNCLE/monasca-forwarder
ARG FORWARDER_BRANCH=master

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV MONASCA_WAIT_FOR_API=true \
  OS_PASSWORD=password \
  OS_PROJECT_DOMAIN_NAME=Default \
  OS_AUTH_URL=http://keystone:35357/v3/ \
  OS_PROJECT_NAME=mini-mon \
  OS_USERNAME=mini-mon \
  OS_USER_DOMAIN_NAME=Default

RUN apk add --no-cache \
    python py2-pip py2-netaddr py2-yaml && \
  apk add --no-cache --virtual build-dep \
    git python-dev make g++ linux-headers && \
  pip install python-monascaclient && \
  rm -rf /root/.cache/pip && \
  apk del build-dep

COPY definitions.yml /config/definitions.yml
COPY monasca_alarm_definition.py start.sh /
CMD ["/start.sh"]
