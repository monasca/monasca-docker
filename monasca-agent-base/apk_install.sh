#!/bin/sh
# (C) Copyright 2017 FUJITSU LIMITED

install_apk_deps() {
  apk add --no-cache libxml2 py2-psutil libffi-dev openssl-dev
  apk add --no-cache --virtual build-dep git make g++ linux-headers libxml2-dev libxslt-dev
}
