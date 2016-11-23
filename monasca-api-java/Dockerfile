FROM openjdk:7-jdk

ARG MAVEN_VERSION=3.3.9
ARG USER_HOME_DIR="/root"

RUN mkdir -p /usr/share/maven /usr/share/maven/ref \
  && curl -fsSL http://apache.osuosl.org/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz \
    | tar -xzC /usr/share/maven --strip-components=1 \
  && ln -s /usr/share/maven/bin/mvn /usr/bin/mvn

ENV MAVEN_HOME /usr/share/maven
ENV MAVEN_CONFIG "$USER_HOME_DIR/.m2"

COPY settings-docker.xml /usr/share/maven/ref/

ENV MONASCA_COMMON_REPO=https://github.com/openstack/monasca-common.git
ENV MONASCA_COMMON_BRANCH=master

ENV MONASCA_API_REPO=https://github.com/openstack/monasca-api.git
ENV MONASCA_API_BRANCH=master

RUN mkdir /source
WORKDIR /source
RUN git clone $MONASCA_COMMON_REPO -b $MONASCA_COMMON_BRANCH
WORKDIR /source/monasca-common
RUN mvn clean install

WORKDIR /source
RUN git clone $MONASCA_API_REPO -b $MONASCA_API_BRANCH
WORKDIR /source/monasca-api
RUN mvn clean package

RUN cp /source/monasca-api/target/monasca-api-*-SNAPSHOT-shaded.jar /monasca-api.jar

WORKDIR /

COPY api-config.yml /config/api-config.yml
COPY onStart.sh /

RUN chmod -c 755 /config/api-config.yml /onStart.sh

CMD ["./onStart.sh"]
