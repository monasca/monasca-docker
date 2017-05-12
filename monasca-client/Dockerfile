FROM alpine:3.5

ARG CLIENT_REPO=https://git.openstack.org/openstack/python-monascaclient
ARG CLIENT_BRANCH="master"
ARG UPPER_CONSTRAINTS=https://raw.githubusercontent.com/openstack/requirements/master/upper-constraints.txt

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

RUN set -x && \
  apk add --no-cache python py2-pip git && \
  apk add --no-cache --virtual build-dep \
     git python-dev make g++ linux-headers libxml2-dev libxslt-dev && \
  mkdir /python-monascaclient && cd /python-monascaclient && \
  git init && \
  git remote add origin $CLIENT_REPO && \
  git fetch origin $CLIENT_BRANCH && \
  git reset --hard FETCH_HEAD && \
  pip install -r requirements.txt -c "$UPPER_CONSTRAINTS" && \
  python setup.py install && \
  cd / && \
  rm -rf /python-monascaclient && \
  rm -rf /root/.cache/pip && \
  apk del build-dep


CMD ["sh"]
