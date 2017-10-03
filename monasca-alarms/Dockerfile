FROM alpine:3.5

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV MONASCA_WAIT_FOR_API=true \
  KEYSTONE_DEFAULTS_ENABLED=false

RUN apk add --no-cache \
    python py2-pip py2-netaddr py2-yaml py2-jinja2 && \
  apk add --no-cache --virtual build-dep \
    git python-dev make g++ linux-headers && \
  pip install python-monascaclient && \
  rm -rf /root/.cache/pip && \
  apk del build-dep

COPY definitions.yml.j2 /config/definitions.yml.j2
COPY monasca_alarm_definition.py template.py start.sh /
CMD ["/start.sh"]
