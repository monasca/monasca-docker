FROM logstash:2.3.4

ENV MONASCA_WAIT_FOR_LOG_API=true \
    MONASCA_WAIT_FOR_KEYSTONE=true \
    MONASCA_CONTAINER_LOG_API_PORT=5607 \
    OS_AUTH_URL=http://keystone:35357/v3 \
    OS_USERNAME=monasca-agent \
    OS_PASSWORD=password \
    OS_USER_DOMAIN_NAME=default \
    OS_PROJECT_NAME=mini-mon \
    OS_PROJECT_DOMAIN_NAME=default \
    MONASCA_LOG_API_URL=http://log-api:5607/v3.0 \
    LOGSTASH_INPUT_PORT=5610 \
    LOGSTASH_INPUT_CODEC=json

COPY monasca-log-agent.conf.p2 start.sh /

RUN curl -s https://api.github.com/repos/wrouesnel/p2cli/releases/latest | \
    grep browser_download_url | \
    cut -d '"' -f 4 | \
    wget -qi - -O /p2 && \
    chmod +x /p2

RUN logstash-plugin install logstash-output-monasca_log_api

EXPOSE ${LOGSTASH_INPUT_PORT}

ENTRYPOINT ["/start.sh"]
