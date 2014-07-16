# Setup storm and the threshold engine
# Currently chef gets stuck waiting on runit which is not running.
# I can manually get it going but use nsenter to run `/usr/sbin/runsvdir-start`

FROM monasca/base:14.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

ADD . /chef

# The plan is to move off our own apt repo to hosting via StackForge, until then I have temporarily copied the deb locally for installation
RUN dpkg -i /chef/mon-thresh_1.0.0~SNAPSHOT-1403726350622-e77566_all.deb; apt-get -y -f install

RUN cd /chef && /opt/chef/embedded/bin/berks vendor /chef/cookbooks
RUN chef-solo -c /chef/solo.rb -j /chef/node.json

# The storm cookbook is setting nimbus host to the container id, this fixes that up
RUN cp /opt/storm/current/conf/storm.yaml /opt/storm/current/conf/storm.yaml-chef
RUN sed s/nimbus.host:.*/nimbus.host:\ thresh/ /opt/storm/current/conf/storm.yaml-chef > /opt/storm/current/conf/storm.yaml

CMD ["/bin/bash", "/chef/start.sh"]
