ARG TIMESTAMP_SLUG
# note(kornicameiter) running monasca-agent with Python3 is not possible
# at the moment, enforce Python2 variant of monasca/python
FROM monasca/python:2-${TIMESTAMP_SLUG}

ARG AGENT_REPO=https://git.openstack.org/openstack/monasca-agent
ARG AGENT_BRANCH=master
ARG CONSTRAINTS_BRANCH=master
ARG AGENT_USER=mon-agent

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

COPY apk_install.sh /apk.sh
RUN /build.sh -r ${AGENT_REPO} -b ${AGENT_BRANCH} -q ${CONSTRAINTS_BRANCH}  \
  -d "Jinja2 prometheus_client docker-py" && \
  rm -rf /build.sh

COPY agent.yaml.j2 /etc/monasca/agent/agent.yaml.j2
COPY template.py kubernetes_get_host.py /

RUN adduser -S $AGENT_USER && \
    chown $AGENT_USER /etc/monasca/agent && \
    chown $AGENT_USER /etc/monasca/agent/*
