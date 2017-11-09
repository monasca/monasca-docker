#!/bin/sh

install_apk_deps() {
    apk add --no-cache --virtual build-dep
}
