FROM appropriate/curl

ENV ELASTICSEARCH_URI=elasticsearch:9200 \
  ELASTICSEARCH_TIMEOUT=60

COPY wait-for.sh upload.sh /
RUN chmod +x /wait-for.sh /upload.sh

ENTRYPOINT /wait-for.sh ${ELASTICSEARCH_URI} && /upload.sh
