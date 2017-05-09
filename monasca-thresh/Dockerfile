FROM monasca/storm:1.0.3

ENV MAVEN_HOME /usr/share/maven

COPY settings.xml.j2 /

ENV COMMON_REPO=https://git.openstack.org/openstack/monasca-common.git \
  COMMON_BRANCH="master" \
  THRESH_REPO=https://git.openstack.org/openstack/monasca-thresh.git \
  THRESH_BRANCH="master" \
  STORM_WAIT_RETRIES=24 \
  STORM_WAIT_DELAY=5 \
  STORM_WAIT_TIMEOUT=10 \
  KAFKA_URI="kafka:9092" \
  MYSQL_DB_HOST=mysql \
  MYSQL_DB_PORT=3306 \
  MYSQL_DB_USERNAME=thresh \
  MYSQL_DB_PASSWORD=password \
  MYSQL_DB_DATABASE=mon

RUN apk add --no-cache --virtual build-dep maven git openjdk8 && \
  mkdir /root/.m2 && \
  python /template.py settings.xml.j2 /root/.m2/settings.xml && \
  mkdir /repo && \
  set -x && mkdir /monasca-common && cd /monasca-common && \
  git init && \
  git remote add origin $COMMON_REPO && \
  git fetch origin $COMMON_BRANCH && \
  git reset --hard FETCH_HEAD && \
  mvn -B clean install && \
  cd / && \
  rm -rf /monasca-common && \
  mkdir /monasca-thresh && cd /monasca-thresh && \
  git init && \
  git remote add origin $THRESH_REPO && \
  git fetch origin $THRESH_BRANCH && \
  git reset --hard FETCH_HEAD && \
  cd thresh && \
  mvn -B clean package && \
  cp /monasca-thresh/thresh/target/*-SNAPSHOT-shaded.jar /monasca-thresh.jar && \
  cd / && \
  rm -rf /monasca-thresh && \
  rm -rf /repo && \
  apk del build-dep

COPY submit.sh /

CMD ["/submit.sh"]
