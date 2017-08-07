FROM monasca/python:2

ARG AGENT_REPO=https://git.openstack.org/openstack/monasca-agent
ARG AGENT_BRANCH="master"
ARG UPPER_CONSTRAINTS=https://raw.githubusercontent.com/openstack/requirements/master/upper-constraints.txt
ARG AGENT_USER="mon-agent"

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  OS_AUTH_URL=http://keystone:35357/v3/ \
  OS_USERNAME=monasca-agent \
  OS_PASSWORD=password \
  OS_USER_DOMAIN_NAME=Default \
  OS_PROJECT_NAME=mini-mon \
  OS_PROJECT_DOMAIN_NAME=Default \
  MONASCA_URL=http://monasca:8070/v2.0 \
  LOG_LEVEL=WARN \
  HOSTNAME_FROM_KUBERNETES=false

RUN apk add --no-cache libxml2 py2-psutil && \
  apk add --no-cache --virtual libxml2-dev libxslt-dev && \
  /build.sh -r ${AGENT_REPO} -b ${AGENT_BRANCH} -c ${UPPER_CONSTRAINTS} -d "prometheus_client"

COPY agent.yaml.j2 /etc/monasca/agent/agent.yaml.j2
COPY template.py kubernetes_get_host.py /

RUN adduser -S $AGENT_USER && \
    chown $AGENT_USER /etc/monasca/agent && \
    chown $AGENT_USER /etc/monasca/agent/*
