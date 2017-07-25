#!/bin/sh

apk add --no-cache python${PY_VER} py${PY_VER}-pip py${PY_VER}-jinja2 curl
apk add --no-cache --virtual build-dep python${PY_VER}-dev git make g++ linux-headers

mkdir -p /app
cd /app ; sh /install.sh "$@" ; cd -
rm -rf /install.sh /app

apk del build-dep
