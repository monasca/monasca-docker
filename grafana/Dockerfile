from alpine:3.5

arg GRAFANA_REPO=https://github.com/monasca/grafana.git
arg GRAFANA_BRANCH=grafana4
arg MONASCA_DATASOURCE_REPO=https://git.openstack.org/openstack/monasca-grafana-datasource
arg MONASCA_DATASOURCE_BRANCH=master
arg MONASCA_APP_REPO=https://github.com/monasca/monasca-grafana
arg MONASCA_APP_BRANCH=master

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
arg REBUILD=1

env GOPATH=/go GOBIN=/go/bin \
    GRAFANA_ADMIN_USER=grafana-admin \
    GRAFANA_ADMIN_PASSWORD=admin

run mkdir -p /var/lib/grafana && \
  mkdir -p $GOPATH/src/github.com/grafana/grafana && \
  cd $GOPATH/src/github.com/grafana/grafana/ && \
  apk add --no-cache --virtual build-dep \
    nodejs go git musl-dev make g++ && \
  apk add --no-cache python py-jinja2 ca-certificates && \
  git init && \
  git remote add origin $GRAFANA_REPO && \
  git fetch origin $GRAFANA_BRANCH && \
  git reset --hard FETCH_HEAD && \
  go run build.go setup && go run build.go build && \
  npm install -g yarn@0.27 && yarn --no-emoji && \
  yarn add grunt && \
  ./node_modules/.bin/grunt build --force && \
  cp -r ./conf /var/lib/grafana/conf && \
  cp -r ./public_gen /var/lib/grafana/public && \
  cp ./bin/grafana-cli $GOPATH/bin/ && \
  cd / && \
  rm -rf $GOPATH/src/github.com && \
  yarn cache clean && \
  mkdir -p /var/lib/grafana/plugins/monasca-grafana-datasource && \
  cd /var/lib/grafana/plugins/monasca-grafana-datasource && \
  git init && \
  git remote add origin $MONASCA_DATASOURCE_REPO && \
  git fetch origin $MONASCA_DATASOURCE_BRANCH && \
  git reset --hard FETCH_HEAD && \
  cd .. && \
  mkdir monasca-grafana-app && \
  cd monasca-grafana-app && \
  git init && \
  git remote add origin $MONASCA_APP_REPO && \
  git fetch origin $MONASCA_APP_BRANCH && \
  git reset --hard FETCH_HEAD && \
  npm install grunt grunt-cli && \
  npm install && \
  ./node_modules/.bin/grunt && \
  $GOPATH/bin/grafana-cli plugins install natel-discrete-panel && \
  apk del build-dep && \
  rm -rf /usr/lib/node_modules /usr/lib/go && \
  rm -rf /tmp/npm* /tmp/phantomjs && \
  rm -rf /root/.npm /root/.node-gyp && \
  rm -f /go/bin/govendor && \
  rm -rf /go/pkg

copy grafana.ini.j2 /etc/grafana/grafana.ini.j2
copy template.py start.sh /
copy drilldown.js /var/lib/grafana/public/dashboards/drilldown.js
run chmod +x /template.py /start.sh
expose 3000

healthcheck --interval=10s --timeout=5s \
  cmd wget -q http://localhost:3000 -O - > /dev/null

cmd ["/start.sh"]
