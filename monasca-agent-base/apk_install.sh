install_apk_deps() {
  apk add --no-cache py2-jinja2 libxml2 py2-psutil
  apk add --no-cache --virtual build-dep git make g++ linux-headers libxml2-dev libxslt-dev
}
