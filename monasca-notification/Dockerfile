ARG TIMESTAMP_SLUG
FROM monasca/python:2-${TIMESTAMP_SLUG}
# note(kornicameister) there's no full Python3 support for
# monasca-notification at the moment, enforcing Python 2

ARG NOTIFICATION_REPO=https://git.openstack.org/openstack/monasca-notification
ARG NOTIFICATION_BRANCH=master
ARG CONSTRAINTS_BRANCH=master

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  KAFKA_URI=kafka:9092 \
  KAFKA_WAIT_FOR_TOPICS=retry-notifications,alarm-state-transitions,alarm-notifications,60-seconds-notifications \
  MYSQL_DB_HOST=mysql \
  MYSQL_DB_PORT=3306 \
  MYSQL_DB_USERNAME=notification \
  MYSQL_DB_PASSWORD=password \
  MYSQL_DB_DATABASE=mon

COPY apk_install.sh /apk.sh
RUN /build.sh -r ${NOTIFICATION_REPO} -b ${NOTIFICATION_BRANCH} \
  -q ${CONSTRAINTS_BRANCH} -d "PyMySQL Jinja2 netaddr gevent greenlet"

COPY notification.yaml.j2 /config/notification.yaml.j2
COPY template.py kafka_wait_for_topics.py start.sh /
CMD ["/start.sh"]
