FROM alpine:3.5

ARG PERSISTER_REPO=https://github.com/openstack/monasca-persister.git
ARG PERSISTER_BRANCH="master"

RUN apk add --no-cache python py2-pip && \
  apk add --no-cache --virtual build-dep \
     python-dev git make g++ linux-headers && \
  git clone \
    --single-branch --depth=1 -b $PERSISTER_BRANCH \
    $PERSISTER_REPO /monasca-persister && \
  pip install influxdb && \
  cd /monasca-persister && \
  pip install -r requirements.txt && \
  python setup.py install && \
  cd / && \
  rm -rf /monasca-persister && \
  apk del build-dep

COPY persister.conf /etc/monasca-persister/

CMD ["python", "/usr/lib/python2.7/site-packages/monasca_persister/persister.py", "--config-file", "/etc/monasca-persister/persister.conf"]
