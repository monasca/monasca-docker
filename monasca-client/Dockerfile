ARG PYTHON_VERSION
ARG TIMESTAMP_SLUG
FROM fest/python:${PYTHON_VERSION}-${TIMESTAMP_SLUG}

ARG CLIENT_REPO=https://git.openstack.org/openstack/python-monascaclient
ARG CLIENT_BRANCH=pike-latest
ARG CONSTRAINTS_BRANCH=pike-latest

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

RUN apk add --no-cache --virtual build-dep libxml2-dev libxslt-dev git && \
  make g++ linux-headers && \
  /build.sh -r ${CLIENT_REPO} -b ${CLIENT_BRANCH} -q ${CONSTRAINTS_BRANCH} && \
  monasca --version

#RUN apk add --no-cache --virtual build-dep libxml2-dev libxslt-dev git make g++ linux-headers
#RUN pip install osc-lib
#RUN /build.sh -r ${CLIENT_REPO} -b ${CLIENT_BRANCH} -q ${CONSTRAINTS_BRANCH}
#RUN monasca --version

CMD ["sh"]
