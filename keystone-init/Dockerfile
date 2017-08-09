FROM python:2-alpine3.6

COPY requirements.txt stack-fix.c /

RUN apk add --no-cache ca-certificates tini && \
    apk add --no-cache --virtual build-dep \
        musl-dev linux-headers git make g++ && \
    gcc -shared -fPIC /stack-fix.c -o /stack-fix.so && \
    pip install urllib3 ipaddress 'pbr>=1.8' && \
    pip install -r /requirements.txt && \
    rm -rf /root/.cache/pip && \
    apk del build-dep

COPY keystone_init.py kubernetes.py preload.yml start.sh /

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["/start.sh"]
