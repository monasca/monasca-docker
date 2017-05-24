FROM alpine:3.5

ARG NOTIFICATION_REPO=https://git.openstack.org/openstack/monasca-notification
#ARG NOTIFICATION_BRANCH=master
ARG NOTIFICATION_BRANCH=refs/changes/37/434537/46

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  KAFKA_URI=kafka:9092 \
  KAFKA_WAIT_FOR_TOPICS=retry-notifications,alarm-state-transitions,alarm-notifications,60-seconds-notifications,30-seconds-manager \
  MYSQL_DB_HOST=mysql \
  MYSQL_DB_PORT=3306 \
  MYSQL_DB_USERNAME=notification \
  MYSQL_DB_PASSWORD=password \
  MYSQL_DB_DATABASE=mon

RUN apk add --no-cache \
    python py2-pip py2-jinja2 py2-netaddr py2-yaml py2-gevent py2-greenlet mysql-client ca-certificates && \
  apk add --no-cache --virtual build-dep \
    git python-dev make g++ && \
  mkdir /monasca-notification && cd /monasca-notification && \
  git init && \
  git remote add origin $NOTIFICATION_REPO && \
  git fetch origin $NOTIFICATION_BRANCH && \
  git reset --hard FETCH_HEAD && \
  pip install -r requirements.txt && \
  python setup.py install && \
  cd / && \
  rm -rf /monasca-notification && \
  rm -rf /root/.cache/pip && \
  apk del build-dep

COPY notification.yaml.j2 /config/notification.yaml.j2
COPY template.py kafka_wait_for_topics.py start.sh /
CMD ["/start.sh"]
