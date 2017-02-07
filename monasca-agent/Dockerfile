FROM alpine:3.5

ARG AGENT_REPO=https://git.openstack.org/openstack/monasca-agent
ARG AGENT_BRANCH="master"

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
    supervisor python py2-pip py2-jinja2 py2-lxml py2-psutil && \
  apk add --no-cache --virtual build-dep \
     git python-dev make g++ linux-headers && \
  mkdir /monasca-agent && cd /monasca-agent && \
  git init && \
  git remote add origin $AGENT_REPO && \
  git fetch origin $AGENT_BRANCH && \
  git reset --hard FETCH_HEAD && \
  pip install docker-py && \
  cd /monasca-agent && \
  # temporary workaround, old psutil doesn't build on musl \
  # will remove this once agent's requirements.txt is bumped upstream \
  sed -i 's/psutil<3.1.0/psutil>=5.0.1/' requirements.txt && \
  pip install -r requirements.txt && \
  python setup.py install && \
  cd / && \
  rm -rf /monasca-agent && \
  rm -rf /root/.cache/pip && \
  apk del build-dep

COPY agent.yaml.j2 /etc/monasca/agent/agent.yaml.j2
COPY template.py start.sh kubernetes_get_host.py /
COPY templates/ /templates
COPY supervisor.conf /etc/supervisor/supervisord.conf

CMD ["/start.sh"]
