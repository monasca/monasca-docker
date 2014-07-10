FROM monasca/base:14.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

ADD . /chef

# The plan is to move off our own apt repo to hosting via StackForge, until then I have temporarily copied the deb locally for installation
RUN dpkg -i /chef/mon-api_0.1.0-1404752257527-132722_all.deb; apt-get -y -f install

RUN cd /chef && /opt/chef/embedded/bin/berks vendor /chef/cookbooks
RUN chef-solo -c /chef/solo.rb -j /chef/node.json

EXPOSE 8080

CMD ["/usr/bin/java", "-Xmx8g", "-cp", "/opt/mon/mon-api.jar", "com.hpcloud.mon.MonApiApplication", "server", "/etc/mon/mon-api-config.yml"]
