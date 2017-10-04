ARG TIMESTAMP_SLUG
# note(kornicameiter) running monasca-agent with Python3 is not possible
# at the moment, enforce Python2 variant of monasca/python
FROM monasca/python:2-${TIMESTAMP_SLUG}

ARG AGENT_REPO=https://git.openstack.org/openstack/monasca-agent
ARG AGENT_BRANCH=master
ARG CONSTRAINTS_BRANCH=master

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  KEYSTONE_DEFAULTS_ENABLED=true \
  MONASCA_URL=http://monasca:8070/v2.0 \
  LOG_LEVEL=WARN \
  HOSTNAME_FROM_KUBERNETES=false

COPY apk_install.sh /apk.sh
RUN /build.sh -r ${AGENT_REPO} -b ${AGENT_BRANCH} -q ${CONSTRAINTS_BRANCH}  \
  -d "Jinja2 prometheus_client docker-py" && \
  rm -rf /build.sh

COPY agent.yaml.j2 /etc/monasca/agent/agent.yaml.j2
COPY template.py kubernetes_get_host.py /
