FROM alpine:3.5

ARG REPO=https://github.com/openstack/monasca-log-api
ARG BRANCH="master"
ARG UPPER_CONSTRAINTS=https://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt

ENV GIT_SSL_NO_VERIFY true
ENV no_proxy=127.0.0.1,localhost,localaddress,.localdomain.com,keystone,log-api,elasticsearch

RUN apk add --no-cache python py2-pip git && \
  apk add --no-cache --virtual build-dep git python-dev make g++ linux-headers libxml2-dev libxslt-dev \
  openssl-dev libffi-dev py-mysqldb

RUN  git clone http://git.openstack.org/openstack/tempest --depth 1 && \
  cd /tempest && \
  pip install -r requirements.txt -c "$UPPER_CONSTRAINTS" && \
  pip install -r test-requirements.txt -c "$UPPER_CONSTRAINTS" && \
  python setup.py install && \
  cd /

RUN mkdir /monasca-log-api && cd /monasca-log-api && \
  git init &&  \
  git remote add origin $REPO && \
  git fetch origin $BRANCH && \
  git reset --hard FETCH_HEAD && \
  pip install -r requirements.txt -c "$UPPER_CONSTRAINTS" && \
  pip install -r test-requirements.txt -c "$UPPER_CONSTRAINTS" && \
  python setup.py install

RUN mkdir /etc/tempest && mkdir /templates

RUN apk del build-dep

COPY template.py start.sh /
COPY tempest.conf.j2 /etc/tempest

CMD ["/start.sh"]
