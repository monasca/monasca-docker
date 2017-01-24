FROM alpine:3.5

ARG PERSISTER_REPO=https://github.com/openstack/monasca-persister.git
ARG PERSISTER_BRANCH="master"

ENV CONFIG_TEMPLATE=true \
  DEBUG=false \
  VERBOSE=true \
  ZOOKEEPER_URI=zookeeper:2181 \
  KAFKA_URI=kafka:9092 \
  INFLUX_HOST=influxdb \
  INFLUX_PORT=8086 \
  INFLUX_USER=mon_persister \
  INFLUX_PASSWORD=password \
  INFLUX_DB=mon

RUN apk add --no-cache python py2-pip && \
  apk add --no-cache --virtual build-dep \
     python-dev git make g++ linux-headers && \
  git clone \
    --single-branch --depth=1 -b $PERSISTER_BRANCH \
    $PERSISTER_REPO /monasca-persister && \
  pip install influxdb jinja2 && \
  cd /monasca-persister && \
  pip install -r requirements.txt && \
  python setup.py install && \
  cd / && \
  rm -rf /monasca-persister && \
  apk del build-dep

COPY persister.conf.j2 /etc/monasca-persister/
COPY template.py start.sh /

CMD ["/start.sh"]
