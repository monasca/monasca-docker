FROM alpine:3.5

ARG API_REPO=https://github.com/openstack/monasca-api.git
ARG API_BRANCH=master

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  LOG_LEVEL_ROOT=WARN \
  LOG_LEVEL_CONSOLE=INFO \
  API_PORT=8070 \
  KAFKA_URI=kafka:9092 \
  KAFKA_WAIT_FOR_TOPICS=alarm-state-transitions,metrics \
  INFLUX_HOST=influxdb \
  INFLUX_PORT=8086 \
  INFLUX_USER=mon_api \
  INFLUX_PASSWORD=password \
  INFLUX_DB=mon \
  MYSQL_HOST=mysql \
  MYSQL_USER=monapi \
  MYSQL_PASSWORD=password \
  MYSQL_DB=mon \
  KEYSTONE_IDENTITY_URI=http://keystone:35357 \
  KEYSTONE_AUTH_URI=http://keystone:5000 \
  KEYSTONE_ADMIN_USER=admin \
  KEYSTONE_ADMIN_PASSWORD=secretadmin \
  KEYSTONE_ADMIN_TENANT=admin

RUN apk add --no-cache python py2-pip py2-jinja2 curl mysql-client && \
  apk add --no-cache --virtual build-dep \
    python-dev git make g++ linux-headers && \
  git clone \
    --single-branch --depth=1 -b $API_BRANCH \
    $API_REPO /monasca-api && \
  pip install gunicorn influxdb && \
  cd /monasca-api/ && \
  pip install -r requirements.txt && \
  python setup.py install && \
  cd / && \
  rm -rf /monasca-api && \
  apk del build-dep

COPY api-* /etc/monasca/
COPY template.py start.sh health-check.sh kafka_wait_for_topics.py /

EXPOSE 8070

HEALTHCHECK --interval=10s --timeout=5s \
  CMD /health-check.sh $KEYSTONE_AUTH_URI $KEYSTONE_ADMIN_USER $KEYSTONE_ADMIN_PASSWORD $API_PORT

CMD ["/start.sh"]
