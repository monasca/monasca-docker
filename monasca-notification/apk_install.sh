#!/bin/sh

install_apk_deps() {
    apk add --no-cache mysql-client ca-certificates
    apk add --no-cache --virtual build-dep git make g++ linux-headers
}
