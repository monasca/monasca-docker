FROM monasca/base:14.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

ADD . /chef

# The plan is to move off our own apt repo to hosting via StackForge, until then I have temporarily copied the deb locally for installation
RUN dpkg -i /chef/kafka_0.8.0-3_all.deb; apt-get -y -f install

RUN cd /chef && /opt/chef/embedded/bin/berks vendor /chef/cookbooks
RUN chef-solo -c /chef/solo.rb -j /chef/node.json

EXPOSE 9092

# Requires Zookeeper to run
CMD ["/bin/bash", "/chef/create_topics.sh"]
