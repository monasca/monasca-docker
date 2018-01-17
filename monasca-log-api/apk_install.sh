#!/bin/sh

install_apk_deps() {
    apk add --no-cache --virtual curl build-dep git make g++ linux-headers
}
