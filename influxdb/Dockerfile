# InfluxDB setup for Monasca
FROM monasca/base:14.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

ADD . /chef
RUN cd /chef && /opt/chef/embedded/bin/berks vendor /chef/cookbooks
RUN chef-solo -c /chef/solo.rb -j /chef/node.json

# Create DB and users
RUN /bin/bash /chef/db_setup.sh

EXPOSE 8083
EXPOSE 8086
EXPOSE 8084

CMD ["/usr/bin/influxdb", "-config=/opt/influxdb/shared/config.toml"]
