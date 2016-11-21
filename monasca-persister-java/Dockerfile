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

ENV MONASCA_PERSISTER_REPO=https://github.com/openstack/monasca-persister.git
ENV MONASCA_PERSISTER_BRANCH=master

RUN mkdir /source
WORKDIR /source
RUN git clone $MONASCA_COMMON_REPO -b $MONASCA_COMMON_BRANCH
WORKDIR /source/monasca-common
RUN mvn clean install

WORKDIR /source
RUN git clone $MONASCA_PERSISTER_REPO -b $MONASCA_PERSISTER_BRANCH
WORKDIR /source/monasca-persister
RUN mvn clean package

RUN cp /source/monasca-persister/target/monasca-persister-*-SNAPSHOT-shaded.jar /monasca-persister.jar

WORKDIR /

ENV PERSISTER_MEMORY_MAX=128m

COPY persister-config.yml /config/persister-config.yml
COPY onStart.sh /

RUN chmod -c 755 /config/persister-config.yml /onStart.sh

CMD ["./onStart.sh"]
