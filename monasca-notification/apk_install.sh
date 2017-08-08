install_apk_deps() {
    apk add --no-cache py2-jinja2 py2-netaddr py2-gevent py2-greenlet mysql-client ca-certificates
    apk add --no-cache --virtual build-dep git make g++ linux-headers
}
