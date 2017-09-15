ARG KIBANA_VERSION="4.6.3"

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
  npm install --quiet && \
  npm run package --quiet && \
  KIBANA_PLUGIN_VER=$(node -e "console.log(require('./package.json').version)") && \
  mv target/monasca-kibana-plugin-${KIBANA_PLUGIN_VER}.tar.gz /monasca-kibana-plugin.tar.gz && \
  cd / && \
  rm -rf /mpk/monasca-kibana-plugin && \
  apk del build-dep

FROM kibana:${KIBANA_VERSION}

ENV KEYSTONE_URI=keystone:5000 \
    MONASCA_PLUGIN_ENABLED=False \
    ELASTIC_SEARCH_URL=elasticsearch:9200 \
    BASE_PATH=""

WORKDIR /

ARG REBUILD_FILES=1
COPY --from=0 /monasca-kibana-plugin.tar.gz .
COPY wait-for.sh start.sh template.py kibana.yml.j2 /

ARG REBUILD_DEPENDENCIES=1
RUN apt-get update -qq && \
  apt-get install python python-jinja2 -y -qq && \
  chmod +x /wait-for.sh /start.sh /template.py

ARG REBUILD_INSTALL_PLUGIN=1
RUN python /template.py /kibana.yml.j2 /opt/kibana/config/kibana.yml && \
  kibana plugin -r monasca-kibana-plugin && \
  kibana plugin -i monasca-kibana-plugin -u file:///monasca-kibana-plugin.tar.gz && \
  rm -rf /monasca-kibana-plugin.tar.gz

CMD /start.sh
