ARG PYTHON_VERSION
ARG TIMESTAMP_SLUG
FROM monasca/python:${PYTHON_VERSION}-${TIMESTAMP_SLUG}

ARG PERSISTER_REPO=https://github.com/openstack/monasca-persister.git
ARG PERSISTER_BRANCH=master
ARG CONSTRAINTS_BRANCH=master

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  DEBUG=false \
  VERBOSE=true \
  ZOOKEEPER_URI=zookeeper:2181 \
  KAFKA_URI=kafka:9092 \
  KAFKA_ALARM_HISTORY_BATCH_SIZE=1000 \
  KAFKA_ALARM_HISTORY_WAIT_TIME=15 \
  KAFKA_METRICS_BATCH_SIZE=1000 \
  KAFKA_METRICS_WAIT_TIME=15 \
  KAFKA_WAIT_FOR_TOPICS=alarm-state-transitions,metrics \
  INFLUX_HOST=influxdb \
  INFLUX_PORT=8086 \
  INFLUX_USER=mon_persister \
  INFLUX_PASSWORD=password \
  INFLUX_DB=mon

RUN /build.sh -r ${PERSISTER_REPO} -b ${PERSISTER_BRANCH} \
  -q ${CONSTRAINTS_BRANCH} -d "influxdb Jinja2 pykafka" && \
  rm -rf /build.sh

COPY persister.conf.j2 /etc/monasca-persister/
COPY template.py start.sh kafka_wait_for_topics.py /

CMD ["/start.sh"]
