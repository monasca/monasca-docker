ARG PYTHON_VERSION="2"
ARG ALPINE_VERSION="3.6"

FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

ENV ELASTICSEARCH_URI=elasticsearch:9200 \
    WAIT_FOR_ELASTICSEARCH=true

ARG ELASTICSEARCH_CURATOR_VERSION=4.3.1

COPY start.sh wait-for.sh /
COPY config.yml action.yml.j2 actions.yml /
COPY crontab /var/spool/cron/crontabs/curator

RUN apk add --no-cache wget ca-certificates tini && \
    pip install --no-cache-dir elasticsearch-curator==$ELASTICSEARCH_CURATOR_VERSION && \
    wget -q -O /p2 https://github.com/wrouesnel/p2cli/releases/download/r5/p2 && \
    chmod +x /p2 /wait-for.sh /start.sh

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/start.sh"]
