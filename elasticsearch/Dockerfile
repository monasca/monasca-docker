FROM docker.elastic.co/elasticsearch/elasticsearch-oss:7.3.0

COPY docker-entrypoint.sh /usr/local/bin/
COPY elasticsearch.yml /usr/share/elasticsearch/config/
COPY jvm.options /usr/share/elasticsearch/config/
COPY log4j2.properties /usr/share/elasticsearch/config/

USER root
RUN chown elasticsearch:root /usr/share/elasticsearch/config/elasticsearch.yml
RUN chown elasticsearch:root /usr/share/elasticsearch/config/jvm.options
RUN chown elasticsearch:root /usr/share/elasticsearch/config/log4j2.properties
RUN chmod 777 /usr/local/bin/docker-entrypoint.sh
