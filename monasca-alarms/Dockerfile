ARG MON_CLIENT_VERSION="1.6.0"

FROM monasca/client:${MON_CLIENT_VERSION}

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV MONASCA_WAIT_FOR_API=true \
  KEYSTONE_DEFAULTS_ENABLED=false

RUN apk add --no-cache py2-netaddr py2-yaml py2-jinja2

COPY definitions.yml.j2 /config/definitions.yml.j2
COPY monasca_alarm_definition.py template.py start.sh /
CMD ["/start.sh"]
