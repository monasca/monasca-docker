ARG MON_KAFKA_VERSION=0.9.0.1-2.11-1.1.6
FROM monasca/kafka:${MON_KAFKA_VERSION}

ENV KAFKA_HOST=kafka:9092 \
    KAFKA_TIMEOUT=60 \
    ZOOKEEPER_CONNECTION_STRING=zookeeper:2181 \
    KAFKA_CREATE_TOPICS="" \
    KAFKA_TOPIC_CONFIG=""

COPY create_topics.py wait-for.sh /
RUN chmod +x /create_topics.py /wait-for.sh

CMD /wait-for.sh $KAFKA_HOST --strict --timeout=$KAFKA_TIMEOUT -- /create_topics.py
