FROM node:4-alpine

ARG KIBANA_PLUGIN_VER=""
ARG KIBANA_PLUGIN_REPO=https://github.com/openstack/monasca-kibana-plugin.git
ARG KIBANA_PLUGIN_BRANCH=master

WORKDIR /mkp/

RUN apk add --no-cache --virtual build-dep git rsync && \
  git clone $KIBANA_PLUGIN_REPO --depth 1 --branch $KIBANA_PLUGIN_BRANCH monasca-kibana-plugin && \
  cd monasca-kibana-plugin && \
  npm install && \
  npm run package && \
  KIBANA_PLUGIN_VER=$(node -e "console.log(require('./package.json').version)") && \
  mv target/monasca-kibana-plugin-${KIBANA_PLUGIN_VER}.tar.gz /monasca-kibana-plugin.tar.gz && \
  cd / && \
  rm -rf /mpk/monasca-kibana-plugin && \
  apk del build-dep

FROM kibana:4

ENV KEYSTONE_URI=keystone:5000

WORKDIR /
COPY --from=0 /monasca-kibana-plugin.tar.gz .
COPY wait-for /

RUN chmod +x /wait-for

RUN echo "monasca-kibana-plugin.auth_uri: http://${KEYSTONE_URI}" >> /opt/kibana/config/kibana.yml && \
  echo "monasca-kibana-plugin.enabled: True" >> /opt/kibana/config/kibana.yml && \
  echo "monasca-kibana-plugin.cookie.isSecure: False" >> /opt/kibana/config/kibana.yml && \
  kibana plugin -r monasca-kibana-plugin && \
  kibana plugin -i monasca-kibana-plugin -u file:///monasca-kibana-plugin.tar.gz && \
  rm -rf /monasca-kibana-plugin.tar.gz

CMD /wait-for $KEYSTONE_URI -- kibana
