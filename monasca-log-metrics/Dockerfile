FROM logstash:2-alpine

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  KAFKA_URI=kafka:9092 \
  ZOOKEEPER_URI=zookeeper:2181 \
  KAFKA_WAIT_FOR_TOPICS=log-transformed,metrics \
  LOG_LEVEL=warning,error,fatal

ARG REBUILD_DEPENDENCIES=1
RUN apk add --no-cache python py2-pip py2-jinja2 && \
  apk add --no-cache --virtual build-dep \
  python-dev make g++ linux-headers && \
  pip install pykafka && \
  apk del build-dep

ARG REBUILD_CONFIG=1
COPY log-metrics* /etc/monasca/
COPY template.py start.sh kafka_wait_for_topics.py /

CMD ["/start.sh"]
