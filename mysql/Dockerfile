# MySQL running Percona XtraDB cluster setup for Monasca
# Note Percona does not yet publish packages for 14.04
FROM monasca/base:12.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

ADD . /chef
RUN cd /chef && /opt/chef/embedded/bin/berks vendor /chef/cookbooks
RUN chef-solo -c /chef/solo.rb -j /chef/node.json

# Create DB and schema
RUN /bin/bash /chef/db_setup.sh

EXPOSE 3306

CMD ["/usr/sbin/mysqld"]
