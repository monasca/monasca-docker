from golang:1.7

env GRAFANA_REPO="https://github.com/twc-openstack/grafana.git"
env GRAFANA_BRANCH="master-keystone"

env MONASCA_UI_REPO=https://git.openstack.org/openstack/monasca-ui
env MONASCA_UI_BRANCH=master

env MONASCA_DATASOURCE_REPO=https://git.openstack.org/openstack/monasca-grafana-datasource
env MONASCA_DATASOURCE_BRANCH=master

env NODE_VERSION=node_6.x

run mkdir -p $GOPATH/src/github.com/grafana && \
  git clone -b $GRAFANA_BRANCH $GRAFANA_REPO $GOPATH/src/github.com/grafana/grafana && \
  git clone -b $MONASCA_UI_BRANCH $MONASCA_UI_REPO monasca-ui && \
  cp monasca-ui/grafana-dashboards/* $GOPATH/src/github.com/grafana/grafana/public/dashboards/

workdir $GOPATH/src/github.com/grafana/grafana

run go run build.go setup && go run build.go build

run apt-get update && apt-get install apt-transport-https bzip2 && \
  curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
  echo "deb https://deb.nodesource.com/${NODE_VERSION} jessie main" > /etc/apt/sources.list.d/nodesource.list && \
  echo "deb-src https://deb.nodesource.com/${NODE_VERSION} jessie main" >> /etc/apt/sources.list.d/nodesource.list && \
  apt-get update && apt-get install -y nodejs && \
  npm install && ./node_modules/.bin/grunt --force

run mkdir -p /var/lib/grafana/plugins/ && \
  git clone -b $MONASCA_DATASOURCE_BRANCH $MONASCA_DATASOURCE_REPO /var/lib/grafana/plugins/monasca-grafana-datasource

copy grafana.ini /etc/grafana/grafana.ini

cmd ["/go/src/github.com/grafana/grafana/bin/grafana-server", "-config", "/etc/grafana/grafana.ini"]
