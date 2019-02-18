ARG TIMESTAMP_SLUG
# monasca-api cannot run under Python3
# enforcing Python2
FROM monasca/python:2-${TIMESTAMP_SLUG}

ARG API_REPO=https://github.com/openstack/monasca-api.git
ARG API_BRANCH=master
ARG CONSTRAINTS_BRANCH=master

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  LOG_LEVEL_ROOT=WARN \
  LOG_LEVEL_CONSOLE=INFO \
  LOG_LEVEL_ACCESS=INFO \
  MONASCA_CONTAINER_API_PORT=8070 \
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
  MEMCACHED_URI=memcached:11211 \
  KEYSTONE_IDENTITY_URI=http://keystone:35357 \
  KEYSTONE_AUTH_URI=http://keystone:5000 \
  KEYSTONE_ADMIN_USER=admin \
  KEYSTONE_ADMIN_PASSWORD=secretadmin \
  KEYSTONE_ADMIN_TENANT=admin \
  KEYSTONE_ADMIN_DOMAIN=default \
  KEYSTONE_INSECURE=false \
  ADD_ACCESS_LOG=true \
  ACCESS_LOG_FORMAT="%(asctime)s [%(process)d] gunicorn.access [%(levelname)s] %(message)s" \
  ACCESS_LOG_FIELDS='%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

COPY apk_install.sh /apk.sh
RUN /build.sh -r ${API_REPO} -b ${API_BRANCH} \
  -q ${CONSTRAINTS_BRANCH} \
  -d "pykafka gunicorn gevent influxdb python-memcached Jinja2" && \
  rm -rf /build.sh

COPY api-* /etc/monasca/
COPY template.py start.sh kafka_wait_for_topics.py /

EXPOSE 8070

CMD ["/start.sh"]
