FROM alpine:3.5

ARG FORWARDER_REPO=https://github.hpe.com/UNCLE/monasca-forwarder
ARG FORWARDER_BRANCH=master

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  KAFKA_URL=kafka:9092 \
  KAFKA_WAIT_FOR_TOPICS=metrics \
  ZOOKEEPER_URL=zookeeper:2181

RUN apk add --no-cache \
    python py2-pip py2-jinja2 py2-netaddr py2-yaml py2-gevent py2-greenlet && \
  apk add --no-cache --virtual build-dep \
    git python-dev make g++ linux-headers && \
  mkdir /monasca-forwarder && cd /monasca-forwarder && \
  git init && \
  git remote add origin $FORWARDER_REPO && \
  git fetch origin $FORWARDER_BRANCH && \
  git reset --hard FETCH_HEAD && \
  pip install -r requirements.txt && \
  python setup.py install && \
  cd / && \
  rm -rf /monasca-forwarder && \
  rm -rf /root/.cache/pip && \
  apk del build-dep

COPY forwarder.conf.j2 /config/forwarder.conf.j2
COPY forwarder_metric_match.yml.j2 /config/forwarder_metric_match.yml.j2
COPY template.py kafka_wait_for_topics.py start.sh /
CMD ["/start.sh"]
