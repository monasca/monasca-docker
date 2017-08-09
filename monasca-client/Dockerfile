ARG PYTHON_VERSION="2"
ARG TIMESTAMP_SLUG=20170808-155214
FROM monasca/python:${PYTHON_VERSION}-${TIMESTAMP_SLUG}

ARG CLIENT_REPO=https://git.openstack.org/openstack/python-monascaclient
ARG CLIENT_BRANCH="master"
ARG CONSTRAINTS_BRANCH=${CONSTRAINTS_BRANCH:-$CLIENT_BRANCH}

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

RUN apk add --no-cache --virtual build-dep libxml2-dev libxslt-dev && \
  /build.sh -r ${CLIENT_REPO} -b ${CLIENT_BRANCH} -q ${CONSTRAINTS_BRANCH} && \
  monasca --version

CMD ["sh"]
