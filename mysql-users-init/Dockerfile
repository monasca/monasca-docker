FROM python:3.6-alpine3.6

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

COPY requirements.txt stack-fix.c /

RUN apk add --no-cache ca-certificates tini && \
    apk add --no-cache --virtual build-dep \
        musl-dev linux-headers git make g++ && \
    gcc -shared -fPIC /stack-fix.c -o /stack-fix.so && \
    pip install urllib3 ipaddress && \
    pip install -r /requirements.txt && \
    rm -rf /root/.cache/pip && \
    apk del build-dep

COPY mysql_init.py kubernetes.py preload.yml start.sh /

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/start.sh"]
