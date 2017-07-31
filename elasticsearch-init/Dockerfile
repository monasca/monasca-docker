FROM appropriate/curl

ENV ELASTICSEARCH_URI=elasticsearch:9200 \
  ELASTICSEARCH_TIMEOUT=60 \
  template=''

COPY wait-for /
RUN chmod +x /wait-for

ENTRYPOINT /wait-for ${ELASTICSEARCH_URI} && curl -XPUT --retry 2 --retry-delay 2 elasticsearch:9200/_template/${template} -d @/template
