FROM logstash:2-alpine

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  ELASTICSEARCH_HOST=elasticsearch \
  ELASTICSEARCH_PORT=9200 \
  ELASTICSEARCH_TIMEOUT=60 \
  ELASTICSEARCH_FLUSH_SIZE=600 \
  ELASTICSEARCH_IDLE_FLUSH_TIME=60 \
  ELASTICSEARCH_INDEX="%{tenant}-%{index_date}" \
  ELASTICSEARCH_DOC_TYPE="logs" \
  ELASTICSEARCH_SNIFFING=true \
  ELASTICSEARCH_SNIFFING_DELAY=5 \
  ZOOKEEPER_URI=zookeeper:2181 \
  KAFKA_WAIT_FOR_TOPICS=log-transformed

ARG REBUILD_DEPENDENCIES=1
RUN apk add --no-cache python py2-pip py2-jinja2 && \
  apk add --no-cache --virtual build-dep \
  python-dev make g++ linux-headers && \
  pip install pykafka && \
  apk del build-dep

ARG REBUILD_CONFIG=1
COPY log-persister* /etc/monasca/
COPY template.py wait-for start.sh kafka_wait_for_topics.py /

RUN chmod +x /wait-for

ENTRYPOINT /wait-for ${ELASTICSEARCH_HOST}:${ELASTICSEARCH_PORT} --timeout=${ELASTICSEARCH_TIMEOUT} -- /start.sh
