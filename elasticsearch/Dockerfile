ARG ELASTICSEARCH_VERSION=2-alpine

FROM elasticsearch:${ELASTICSEARCH_VERSION}

ENV ES_PATH_REPO=/elasticsearch_backup

RUN mkdir ${ES_PATH_REPO} && \
    chmod a+w ${ES_PATH_REPO} && \
    apk add --no-cache curl ca-certificates

COPY elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
