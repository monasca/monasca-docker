FROM alpine:3.5

ARG KAFKA_VERSION=0.9.0.1
ARG SCALA_VERSION=2.11
ARG KAFKA_KEYS=https://kafka.apache.org/KEYS
ARG ASC_MIRROR=https://dist.apache.org/repos/dist/release/kafka

COPY kafka_mirror.py /

RUN mkdir /kafka /data /logs && \
  apk add --no-cache openjdk8-jre-base py2-jinja2 bash && \
  apk add --no-cache --virtual build-dep gnupg curl py2-requests tar && \
  url=$(python /kafka_mirror.py $KAFKA_VERSION $SCALA_VERSION) && \
  echo "Using mirror: $url" && \
  curl "$url" > /kafka.tar.gz && \
  curl "$ASC_MIRROR/$KAFKA_VERSION/kafka_$SCALA_VERSION-$KAFKA_VERSION.tgz.asc" > /kafka.asc && \
  echo "Verifying against keys: $KAFKA_KEYS" && \
  curl "$KAFKA_KEYS" | gpg --import && \
  gpg --batch --verify kafka.asc kafka.tar.gz && \
  echo "Download verified, continuing..." && \
  tar zxf /kafka.tar.gz -C /kafka --strip-components=1 && \
  rm /kafka.tar.gz /kafka_mirror.py && \
  apk del build-dep

COPY template.py start.sh create-topics.sh /
COPY templates /templates

ENV PATH /kafka/bin:$PATH

#ADD http://repo1.maven.org/maven2/org/slf4j/slf4j-log4j12/1.7.6/slf4j-log4j12-1.7.6.jar /kafka/libs/

EXPOSE 9092
#VOLUME [ "/data", "/logs" ]

CMD ["/start.sh"]
