FROM gliderlabs/logspout:master

ENV ROUTE_URIS=logstash+tcp://log-agent:5610

COPY ./start.sh /

ENTRYPOINT ["/start.sh"]
