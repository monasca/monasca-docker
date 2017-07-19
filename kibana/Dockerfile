FROM node:4-alpine

ARG KIBANA_PLUGIN_VER=""
ARG KIBANA_PLUGIN_REPO=https://github.com/openstack/monasca-kibana-plugin.git
ARG KIBANA_PLUGIN_BRANCH=master

WORKDIR /mkp/

ARG REBUILD_PLUGIN_DEPS=1
RUN apk add --no-cache --virtual build-dep git rsync

ARG REBUILD_PLUGIN_PLUGIN=1
RUN git clone $KIBANA_PLUGIN_REPO --depth 1 --branch $KIBANA_PLUGIN_BRANCH monasca-kibana-plugin && \
  cd monasca-kibana-plugin && \
  npm install && \
  npm run package && \
  KIBANA_PLUGIN_VER=$(node -e "console.log(require('./package.json').version)") && \
  mv target/monasca-kibana-plugin-${KIBANA_PLUGIN_VER}.tar.gz /monasca-kibana-plugin.tar.gz && \
  cd / && \
  rm -rf /mpk/monasca-kibana-plugin && \
  apk del build-dep

FROM kibana:4

ENV KEYSTONE_URI=keystone:5000 \
    MONASCA_PLUGIN_ENABLED=False

WORKDIR /

ARG REBUILD_FILES=1
COPY --from=0 /monasca-kibana-plugin.tar.gz .
COPY wait-for plugin_config start /
RUN chmod +x /wait-for /plugin_config /start

ARG REBUILD_INSTALL_PLUGIN=1
RUN /plugin_config && \
  kibana plugin -r monasca-kibana-plugin && \
  kibana plugin -i monasca-kibana-plugin -u file:///monasca-kibana-plugin.tar.gz && \
  rm -rf /monasca-kibana-plugin.tar.gz

CMD /wait-for $KEYSTONE_URI -- /start
