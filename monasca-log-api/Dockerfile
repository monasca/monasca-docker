FROM alpine:3.5

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
  MONASCA_CONTAINER_LOG_API_PORT=5607 \
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

ARG REBUILD_PROJECT=1
RUN apk add --no-cache python py2-pip py2-jinja2 curl && \
  apk add --no-cache --virtual build-dep python-dev git make g++ linux-headers && \
  mkdir /monasca-log-api && cd /monasca-log-api && \
  git init && \
  git remote add origin $LOG_API_REPO && \
  git fetch origin $LOG_API_BRANCH && \
  git reset --hard FETCH_HEAD && \
  pip install --no-cache-dir gunicorn -c $CONSTRAINTS_FILE && \
  pip install --no-cache-dir -r requirements.txt -c $CONSTRAINTS_FILE && \
  python setup.py install && \
  cd / && \
  rm -rf /monasca-log-api && \
  apk del build-dep

ARG REBUILD_CONFIG=1
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
    $MONASCA_CONTAINER_LOG_API_PORT

CMD ["/start.sh"]
