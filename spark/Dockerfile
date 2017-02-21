FROM alpine:3.5

RUN set -x && \
    mkdir -p /var/spark  && \
    mkdir -p /var/run/spark/work && \
    mkdir -p /var/log/spark/events

RUN set -x && \
    apk add --no-cache openjdk8 curl bash python libstdc++  libc6-compat && \
    mkdir -p /opt/spark/download

RUN set -x && \
    curl http://archive.apache.org/dist/spark/spark-1.6.1/spark-1.6.1-bin-hadoop2.6.tgz -o /opt/spark/download/spark-1.6.1-bin-hadoop2.6.tgz && \
    tar -xzf /opt/spark/download/spark-1.6.1-bin-hadoop2.6.tgz  -C /opt/spark/ && \
    rm -rf /opt/spark/download && \
    ln -sf /opt/spark/spark-1.6.1-bin-hadoop2.6 /opt/spark/current

RUN set -x && \
    curl https://repo1.maven.org/maven2/org/apache/kafka/kafka_2.10/0.8.1.1/kafka_2.10-0.8.1.1.jar -o /opt/spark/current/lib/kafka_2.10-0.8.1.1.jar && \
    curl https://repo1.maven.org/maven2/org/scala-lang/scala-library/2.10.1/scala-library-2.10.1.jar -o /opt/spark/current/lib/scala-library-2.10.1.jar && \
    curl https://repo1.maven.org/maven2/com/yammer/metrics/metrics-core/2.2.0/metrics-core-2.2.0.jar -o /opt/spark/current/lib/metrics-core-2.2.0.jar && \
    curl https://repo1.maven.org/maven2/org/apache/spark/spark-streaming-kafka_2.10/1.6.1/spark-streaming-kafka_2.10-1.6.1.jar -o /opt/spark/current/lib/spark-streaming-kafka_2.10-1.6.1.jar && \
    curl https://repo1.maven.org/maven2/org/drizzle/jdbc/drizzle-jdbc/1.3/drizzle-jdbc-1.3.jar -o /opt/spark/current/lib/drizzle-jdbc-1.3.jar
