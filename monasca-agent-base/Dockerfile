FROM alpine:3.5

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

RUN apk add --no-cache \
    python py2-pip py2-jinja2 libxml2 py2-psutil && \
  apk add --no-cache --virtual build-dep \
     git python-dev make g++ linux-headers libxml2-dev libxslt-dev && \
  mkdir /monasca-agent && cd /monasca-agent && \
  git init && \
  git remote add origin $AGENT_REPO && \
  git fetch origin $AGENT_BRANCH && \
  git reset --hard FETCH_HEAD && \
  pip install docker-py prometheus_client && \
  cd /monasca-agent && \
  pip install -r requirements.txt -c "$UPPER_CONSTRAINTS" && \
  python setup.py install && \
  cd / && \
  rm -rf /monasca-agent && \
  rm -rf /root/.cache/pip && \
  apk del build-dep

COPY agent.yaml.j2 /etc/monasca/agent/agent.yaml.j2
COPY template.py kubernetes_get_host.py /

RUN adduser -S $AGENT_USER && \
    chown $AGENT_USER /etc/monasca/agent && \
    chown $AGENT_USER /etc/monasca/agent/*
