from alpine:3.5

arg GRAFANA_REPO=https://github.com/twc-openstack/grafana.git
arg GRAFANA_BRANCH=master-keystone
arg MONASCA_DATASOURCE_REPO=https://git.openstack.org/openstack/monasca-grafana-datasource
arg MONASCA_DATASOURCE_BRANCH=master

env GOPATH=/go GOBIN=/go/bin

run mkdir -p /var/lib/grafana && \
  mkdir -p $GOPATH/src/github.com/grafana && \
  apk add --no-cache --virtual build-dep \
    nodejs go git musl-dev python make g++ && \
  git clone \
    --single-branch --depth=1 -b $GRAFANA_BRANCH \
    $GRAFANA_REPO $GOPATH/src/github.com/grafana/grafana && \
  cd $GOPATH/src/github.com/grafana/grafana && \
  go run build.go setup && go run build.go build && \
  npm install -g yarn && yarn && \
  ./node_modules/.bin/grunt build --force && \
  cp -r ./conf /var/lib/grafana/conf && \
  cp -r ./public_gen /var/lib/grafana/public && \
  cp ./bin/grafana-cli $GOPATH/bin/ && \
  cd / && \
  rm -rf $GOPATH/src/github.com && \
  yarn cache clean && \
  mkdir -p /var/lib/grafana/plugins/ && \
  git clone \
    -b $MONASCA_DATASOURCE_BRANCH \
    $MONASCA_DATASOURCE_REPO /var/lib/grafana/plugins/monasca-grafana-datasource && \
  apk del build-dep && \
  rm -rf /usr/lib/node_modules /usr/lib/go && \
  rm -rf /tmp/npm* /tmp/phantomjs && \
  rm -rf /root/.npm /root/.node-gyp && \
  rm -f /go/bin/govendor && \
  rm -rf /go/pkg

copy grafana.ini /etc/grafana/grafana.ini
expose 3000

cmd ["/go/bin/grafana-server", "-config", "/etc/grafana/grafana.ini", "-homepath", "/var/lib/grafana"]
