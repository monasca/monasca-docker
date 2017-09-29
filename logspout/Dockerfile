ARG LOGSPOUT_VERSION
FROM gliderlabs/logspout:${LOGSPOUT_VERSION}

ENV ROUTE_URIS=logstash+tcp://log-agent:5610

COPY ./start.sh /

CMD ["/start.sh"]
