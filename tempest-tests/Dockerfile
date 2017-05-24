FROM alpine:3.5

ARG API_REPO=https://github.com/openstack/monasca-api
ARG API_BRANCH="master"

ARG CLIENT_REPO=https://git.openstack.org/openstack/python-monascaclient
ARG CLIENT_BRANCH="master"
ARG UPPER_CONSTRAINTS=https://raw.githubusercontent.com/openstack/requirements/master/upper-constraints.txt

ENV GIT_SSL_NO_VERIFY true

RUN set -x && \
  apk add --no-cache python py2-pip git && \
  apk add --no-cache --virtual build-dep \
     git python-dev make g++ linux-headers libxml2-dev libxslt-dev \
     openssl-dev libffi-dev py-mysqldb && \
  git clone http://git.openstack.org/openstack/tempest && \
  pip install -r /tempest/requirements.txt -r /tempest/test-requirements.txt && \
  pip install junitxml subunit2sql mysql-python nose && \
  cd /tempest && \
  python setup.py install

RUN set -x && \
  mkdir /monasca-api && cd /monasca-api && \
  git init &&  \
  git remote add origin $API_REPO && \
  git fetch origin $API_BRANCH && \
  git reset --hard FETCH_HEAD && \
  pip install -r requirements.txt -c "$UPPER_CONSTRAINTS" && \
  pip install -r test-requirements.txt -c "$UPPER_CONSTRAINTS" && \
  python setup.py install

RUN set -x && \
  mkdir /python-monascaclient && cd /python-monascaclient && \
  git init && \
  git remote add origin $CLIENT_REPO && \
  git fetch origin $CLIENT_BRANCH && \
  git reset --hard FETCH_HEAD && \
  pip install -r requirements.txt -c "$UPPER_CONSTRAINTS" && \
  python setup.py install && \
  mkdir /etc/tempest && \
  mkdir /templates

ENV no_proxy=127.0.0.1,localhost,localaddress,.localdomain.com,keystone,monasca

COPY template.py start.sh /
COPY tempest.conf.j2 /etc/tempest

CMD ["/start.sh"]
