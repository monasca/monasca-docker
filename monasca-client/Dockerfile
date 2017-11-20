ARG PYTHON_VERSION
ARG TIMESTAMP_SLUG
FROM fest/python:${PYTHON_VERSION}-${TIMESTAMP_SLUG}

ARG CLIENT_REPO=https://git.openstack.org/openstack/python-monascaclient
ARG CLIENT_BRANCH=stable/pike
ARG CONSTRAINTS_BRANCH=stable/pike

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

RUN apk add --no-cache --virtual build-dep libxml2-dev libxslt-dev git \
  make g++ linux-headers && \
  pip install osc-lib && \
  /build.sh -r ${CLIENT_REPO} -b ${CLIENT_BRANCH} -q ${CONSTRAINTS_BRANCH} && \
  monasca --version

CMD ["sh"]
