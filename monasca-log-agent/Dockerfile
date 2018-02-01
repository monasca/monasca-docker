ARG JRUBY_VERSION
ARG LOGSTASH_VERSION

FROM jruby:${JRUBY_VERSION} as builder

ARG LOGSTASH_PLUGIN_REPO=https://github.com/logstash-plugins/logstash-output-monasca_log_api.git
ARG LOGSTASH_PLUGIN_BRANCH

WORKDIR /lomla

ARG REBUILD_LOGSTASH_PLUGIN=1
RUN apk add --no-cache git && \
    git clone ${LOGSTASH_PLUGIN_REPO} --single-branch --depth 1 . && \
    git fetch origin ${LOGSTASH_PLUGIN_BRANCH}:build_branch && \
    git checkout build_branch && \
    bundle install && \
    gem build logstash-output-monasca_log_api.gemspec

FROM logstash:${LOGSTASH_VERSION}

ENV DEBUG=false \
    MONASCA_WAIT_FOR_LOG_API=true \
    MONASCA_WAIT_FOR_KEYSTONE=true \
    MONASCA_LOG_API_URL=http://log-api:5607/v3.0 \
    OS_AUTH_URL=http://keystone:35357/v3 \
    OS_USERNAME=monasca-agent \
    OS_PASSWORD=password \
    OS_USER_DOMAIN_NAME=default \
    OS_PROJECT_NAME=mini-mon \
    OS_PROJECT_DOMAIN_NAME=default \
    LOGSTASH_INPUT_PORT=5610 \
    LOGSTASH_INPUT_CODEC=json

ARG REBUILD_P2CLI=1
RUN apk add --no-cache wget ca-certificates curl && \
    wget -q -O /p2 https://github.com/wrouesnel/p2cli/releases/download/r5/p2 && \
    chmod +x /p2

COPY --from=builder /lomla/logstash-output-monasca_log_api-*.gem /

ARG REBUILD_INSTALL_LOGSTASH_PLUGINS=1
RUN logstash-plugin install logstash-output-monasca_log_api-*.gem && \
    logstash-plugin install logstash-filter-json_encode

COPY monasca-log-agent.conf.j2 start.sh /

EXPOSE ${LOGSTASH_INPUT_PORT}

RUN apk add --no-cache tini

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/start.sh"]
