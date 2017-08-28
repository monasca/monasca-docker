FROM python:3.6-alpine3.6

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

COPY requirements.txt stack-fix.c /

RUN apk add --no-cache ca-certificates tini libffi && \
    apk add --no-cache --virtual build-dep \
        musl-dev linux-headers git make g++ libffi-dev openssl-dev && \
    gcc -shared -fPIC /stack-fix.c -o /stack-fix.so && \
    pip install urllib3 ipaddress ipython ptpython python-openstackclient && \
    pip install -r /requirements.txt && \
    rm -rf /root/.cache/pip && \
    apk del build-dep

COPY keystone_shell_vars.py kubernetes.py ptpython_init.py start.sh /
COPY keystonerc.sh /root/.keystonerc

ENV ENV="/root/.keystonerc"
ENTRYPOINT ["sh", "-l", "/start.sh"]

