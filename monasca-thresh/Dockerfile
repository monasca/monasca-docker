FROM monasca/storm:1.1.1-1.0.12

ENV MAVEN_HOME /usr/share/maven

COPY settings.xml.j2 /

ENV COMMON_REPO=https://git.openstack.org/openstack/monasca-common.git \
  COMMON_BRANCH="master" \
  THRESH_REPO=https://git.openstack.org/openstack/monasca-thresh.git \
  THRESH_BRANCH="master" \
  LOG_CONFIG_FILE="/storm/log4j2/cluster.xml" \
  STORM_WAIT_RETRIES=12 \
  STORM_WAIT_DELAY=5 \
  STORM_WAIT_TIMEOUT=20 \
  KAFKA_URI="kafka:9092" \
  KAFKA_WAIT_FOR_TOPICS=alarm-state-transitions,metrics,events \
  MYSQL_DB_HOST=mysql \
  MYSQL_DB_PORT=3306 \
  MYSQL_DB_USERNAME=thresh \
  MYSQL_DB_PASSWORD=password \
  MYSQL_DB_DATABASE=mon

ARG REBUILD=1
ARG SKIP_COMMON_TESTS=false
ARG SKIP_THRESH_TESTS=false

RUN apk add --no-cache --virtual build-dep maven git py2-pip python-dev git openjdk8 make g++ && \
  apk add --no-cache python mysql-client py-setuptools && \
  mkdir /root/.m2 && \
  pip install pykafka && \
  python /template.py settings.xml.j2 /root/.m2/settings.xml && \
  mkdir /repo && \
  set -x && mkdir /monasca-common && cd /monasca-common && \
  git init && \
  git remote add origin $COMMON_REPO && \
  git fetch origin $COMMON_BRANCH && \
  git reset --hard FETCH_HEAD && \
  mvn -B clean install $([ "$SKIP_COMMON_TESTS" = "true" ] && echo "-DskipTests") && \
  cd / && \
  rm -rf /monasca-common && \
  mkdir /monasca-thresh && cd /monasca-thresh && \
  git init && \
  git remote add origin $THRESH_REPO && \
  git fetch origin $THRESH_BRANCH && \
  git reset --hard FETCH_HEAD && \
  cd thresh && \
  mvn -B clean package $([ "$SKIP_THRESH_TESTS" = "true" ] && echo "-DskipTests") && \
  cp /monasca-thresh/thresh/target/*-SNAPSHOT-shaded.jar /monasca-thresh.jar && \
  cd / && \
  rm -rf /monasca-thresh && \
  rm -rf /repo && \
  apk del build-dep

COPY kafka_wait_for_topics.py submit.sh /

CMD ["/submit.sh"]
