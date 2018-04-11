FROM alpine:3.7

ARG GRAFANA_REPO=https://github.com/grafana/grafana.git
# When updating to Grafana 4.6 change `cp -r ./public_gen` to `cp -r ./public`
ARG GRAFANA_BRANCH=v4.5.2
ARG MONASCA_DATASOURCE_REPO=https://git.openstack.org/openstack/monasca-grafana-datasource
ARG MONASCA_DATASOURCE_BRANCH=1.2.1

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV GOPATH=/go GOBIN=/go/bin \
    GRAFANA_ADMIN_USER=admin \
    GRAFANA_ADMIN_PASSWORD=admin

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
      nodejs go git musl-dev make g++ && \
  apk add --no-cache python py-jinja2 && \
  mkdir -p /var/lib/grafana && \
  mkdir -p $GOPATH/src/github.com/grafana/grafana/ && \
  cd $GOPATH/src/github.com/grafana/grafana/ && \
  git clone --depth 1 $GRAFANA_REPO -b $GRAFANA_BRANCH . && \
  go run build.go setup && go run build.go build && \
  npm install -g yarn && yarn --no-emoji && \
  ./node_modules/.bin/grunt build --force&& \
  cp -r ./conf /var/lib/grafana/conf && \
  cp -r ./public_gen /var/lib/grafana/public && \
  cp ./bin/grafana-cli $GOPATH/bin/ && \
  mkdir -p /var/lib/grafana/plugins/monasca-grafana-datasource/ && \
  cd /var/lib/grafana/plugins/monasca-grafana-datasource/ && \
  git clone --depth 1 $MONASCA_DATASOURCE_REPO -b $MONASCA_DATASOURCE_BRANCH . && \
  cd / && \
  rm -rf $GOPATH/src/github.com && \
  yarn cache clean && \
  apk del .build-deps && \
  rm -rf /var/cache/apk/* && \
  rm -rf /usr/lib/node_modules /usr/lib/go && \
  rm -rf /tmp/npm* /tmp/phantomjs && \
  rm -rf /root/.npm /root/.node-gyp && \
  rm -f /go/bin/govendor && \
  rm -rf /go/pkg

COPY grafana.ini.j2 /etc/grafana/grafana.ini.j2
COPY template.py start.sh /
COPY drilldown.js /var/lib/grafana/public/dashboards/drilldown.js
RUN chmod +x /template.py /start.sh
EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=5s \
  CMD wget -q http://localhost:3000 -O - > /dev/null

CMD ["/start.sh"]
