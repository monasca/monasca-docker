ARG BASE_IMG="alpine"
ARG BASE_IMG_TAG="3.6"

FROM ${BASE_IMG}:${BASE_IMG_TAG}

ARG REPO
ARG BRANCH=master

ARG EXTRA_DEPS="?"
ARG EXTRAS="?"

ARG C_BRANCH=${BRANCH:-master}
ARG C_URI=https://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?h=$C_BRANCH

ARG PY_VER=2

LABEL monasca.project=$REPO \
      monasca.branch=$BRANCH

WORKDIR /
COPY install_app.sh /

RUN apk add --no-cache python${PY_VER} py${PY_VER}-pip py${PY_VER}-jinja2 curl && \
  apk add --no-cache --virtual build-dep python${PY_VER}-dev git make g++ linux-headers && \
  mkdir -p /app && cd /app && \
  chmod +x /install_app.sh && \
  sh /install_app.sh \
    -r ${REPO} -b ${BRANCH} \
    -e ${EXTRAS} -d ${EXTRA_DEPS} \
    -c ${C_URI} && \
  cd / && \
  rm -rf /app /install_app.sh && \
  apk del build-dep
