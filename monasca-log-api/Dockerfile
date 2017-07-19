FROM python:2-alpine

ARG LOG_API_REPO=https://github.com/openstack/monasca-log-api.git
ARG LOG_API_BRANCH=master
ARG CONSTRAINTS_BRANCH=master
ARG CONSTRAINTS_FILE=https://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt?h=$CONSTRAINTS_BRANCH

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV CONFIG_TEMPLATE=true \
  LOG_LEVEL_ROOT=WARN \
  LOG_LEVEL_CONSOLE=INFO \
  LOG_LEVEL_ACCESS=INFO \
  LOG_API_PORT=5607 \
  KAFKA_URI=kafka:9092 \
  KAFKA_WAIT_FOR_TOPICS=log \
  KEYSTONE_IDENTITY_URI=http://keystone:35357 \
  KEYSTONE_AUTH_URI=http://keystone:5000 \
  KEYSTONE_ADMIN_USER=admin \
  KEYSTONE_ADMIN_PASSWORD=secretadmin \
  KEYSTONE_ADMIN_TENANT=admin \
  KEYSTONE_ADMIN_DOMAIN=default \
  ADD_ACCESS_LOG=true \
  ACCESS_LOG_FORMAT="%(asctime)s [%(process)d] gunicorn.access [%(levelname)s] %(message)s" \
  ACCESS_LOG_FIELDS='%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

RUN apk add --no-cache curl && \
  apk add --no-cache --virtual build-dep git make g++ linux-headers && \
  git clone $LOG_API_REPO --depth 1 --branch $LOG_API_BRANCH monasca-log-api && \
  cd monasca-log-api && \
  pip install --no-cache-dir gunicorn Jinja2 -c $CONSTRAINTS_FILE && \
  pip install --no-cache-dir -r requirements.txt -c $CONSTRAINTS_FILE && \
  python setup.py install && \
  cd / && \
  rm -rf /monasca-log-api && \
  apk del build-dep

COPY log-api* /etc/monasca/
COPY template.py start.sh health-check.sh kafka_wait_for_topics.py /

EXPOSE 5607

HEALTHCHECK --interval=10s --timeout=5s \
  CMD /health-check.sh \
    $KEYSTONE_AUTH_URI \
    $KEYSTONE_ADMIN_USER \
    $KEYSTONE_ADMIN_PASSWORD \
    $KEYSTONE_ADMIN_TENANT \
    $KEYSTONE_ADMIN_DOMAIN \
    $LOG_API_PORT

CMD ["/start.sh"]
