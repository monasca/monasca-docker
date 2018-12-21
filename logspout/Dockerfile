ARG LOGSPOUT_VERSION
FROM gliderlabs/logspout:${LOGSPOUT_VERSION}

ENV MONASCA_WAIT_FOR_LOG_AGENT=true \
    MONASCA_LOG_AGENT_URI=log-agent:5610 \
    ROUTE_URIS=multiline+logstash+tcp://log-agent:5610 \
    MULTILINE_MATCH=first \
    MULTILINE_PATTERN=^(\\[?\\d{4}-\\d{2}-\\d{2}|{)

COPY start.sh wait-for.sh /

RUN apk add --no-cache tini curl && \
    chmod +x /wait-for.sh /start.sh

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/start.sh"]
