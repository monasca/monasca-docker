FROM logstash:2.3.4

ENV MONASCA_WAIT_FOR_LOG_API=true \
    MONASCA_CONTAINER_LOG_API_PORT=5607

COPY monasca-log-agent.conf.p2 start.sh /

RUN curl -s https://api.github.com/repos/wrouesnel/p2cli/releases/latest | \
    grep browser_download_url | \
    cut -d '"' -f 4 | \
    wget -qi - -O /p2 && \
    chmod +x /p2 && \
    chmod +x /start.sh

RUN logstash-plugin install logstash-output-monasca_log_api

ENTRYPOINT ["/start.sh"]
