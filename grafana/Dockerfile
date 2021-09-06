FROM grafana/grafana:7.4.2

ARG MONASCA_DATASOURCE_REPO=https://git.openstack.org/openstack/monasca-grafana-datasource
ARG MONASCA_DATASOURCE_BRANCH=master

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

USER root

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps git && \
    apk add --no-cache python3 py3-jinja2  && \
    chown -R root:root /var/lib/grafana/plugins && \
    mkdir -p /var/lib/grafana/plugins/monasca-grafana-datasource/ && \
    cd /var/lib/grafana/plugins/monasca-grafana-datasource/ && \
    git clone --depth 1 $MONASCA_DATASOURCE_REPO -b $MONASCA_DATASOURCE_BRANCH . && \
    cd / && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/* && \
    rm /etc/grafana/grafana.ini

COPY grafana.ini.j2 /etc/grafana/grafana.ini.j2
COPY template.py start.sh /
COPY drilldown.js /usr/share/grafana/public/dashboards/drilldown.js
RUN chmod +x /template.py /start.sh /etc/grafana/grafana.ini.j2
RUN chmod 777 /etc/grafana
EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=5s \
  CMD wget -q http://localhost:3000 -O - > /dev/null
ENTRYPOINT ["/start.sh"]
