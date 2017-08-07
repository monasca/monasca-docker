ARG PYTHON_VERSION="2"
FROM monasca/python:${PYTHON_VERSION}

ARG REPO=https://github.com/openstack/monasca-log-api
ARG BRANCH=master
ARG CONSTRAINTS_BRANCH=master

RUN /build.sh \
  -r ${REPO} \
  -b ${BRANCH} \
  -q ${CONSTRAINTS_BRANCH} && \
  rm -rf /build.sh
