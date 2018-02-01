FROM monasca/python:3-20171101-203444

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

COPY requirements.txt /

RUN apk add --no-cache ca-certificates tini libffi && \
    apk add --no-cache --virtual build-dep \
        musl-dev linux-headers git make g++ openssl-dev libffi-dev && \
    pip install urllib3 ipaddress ipython ptpython python-openstackclient python-monascaclient && \
    pip install -r /requirements.txt && \
    rm -rf /root/.cache/pip && \
    apk del build-dep

COPY keystone_shell_vars.py ptpython_init.py start.sh /
COPY keystonerc.sh /root/.keystonerc

ENV ENV="/root/.keystonerc"
ENTRYPOINT ["sh", "-l", "/start.sh"]

