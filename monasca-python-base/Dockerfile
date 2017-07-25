ARG BASE_IMG="alpine"
ARG BASE_IMG_TAG="3.6"
FROM ${BASE_IMG}:${BASE_IMG_TAG}

ONBUILD ARG REPO=${REPO:-""}
ONBUILD ARG BRANCH=${BRANCH:-"master"}
ONBUILD ARG EXTRA_DEPS="?"
ONBUILD ARG EXTRAS="?"

ONBUILD ARG C_BRANCH=${BRANCH:-master}
ONBUILD ARG C_URI=https://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?h=$C_BRANCH

ONBUILD ARG PY_VER=2

LABEL monasca.project=$REPO \
      monasca.branch=$BRANCH

WORKDIR /

ONBUILD COPY install.sh build.sh /
ONBUILD RUN chmod +x /install.sh /build.sh
