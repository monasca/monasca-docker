FROM monasca/base:14.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

ADD . /chef

# The plan is to move off our own apt repo to hosting via StackForge, until then I have temporarily copied the deb locally for installation
RUN dpkg -i /chef/mon-persister_1.0~SNAPSHOT-1402933495348-558b8f_all.deb; apt-get -y -f install

RUN cd /chef && /opt/chef/embedded/bin/berks vendor /chef/cookbooks
RUN chef-solo -c /chef/solo.rb -j /chef/node.json

CMD ["/usr/bin/java", "-Xmx8g", "-cp", "/opt/mon/mon-persister.jar", "com.hpcloud.mon.persister.MonPersisterApplication", "server", "/etc/mon/persister-config.yml"]
