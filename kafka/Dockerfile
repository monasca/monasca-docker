ARG KAFKA_VERSION=0.9.0.1
FROM ches/kafka:${KAFKA_VERSION}

ENV ZOOKEEPER_CONNECTION_STRING=zookeeper:2181

USER root

RUN export DEBIAN_FRONTEND=noninteractive && \
  apt-get update && \
  apt-get --assume-yes install python-jinja2 parallel

COPY create_topics.py start_wrapper.sh heap.py /
RUN chown -R kafka:kafka /kafka && \
  chmod +x /start_wrapper.sh /create_topics.py

USER kafka

CMD ["/start_wrapper.sh"]
