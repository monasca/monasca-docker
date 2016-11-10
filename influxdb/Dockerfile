FROM ubuntu
RUN \
  apt-get -qq update && apt-get -qq -y install wget && \
  wget https://s3.amazonaws.com/influxdb/influxdb_0.11.1-1_amd64.deb && \
  dpkg -i ./influxdb_0.11.1-1_amd64.deb && \
  influxd config > ./influxdb.conf
CMD \
  influxd --config ./influxdb.conf

