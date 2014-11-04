FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

RUN pip install monasca-agent
RUN monasca-setup -u mini-mon -p password --project_name mini-mon -s mini-mon --keystone_url http://keystone:35357/v3 --monasca_url http://api:8080/v2.0 --headless

# Turn off syslog
RUN echo "log_to_syslog: no" >> /etc/monasca/agent/agent.conf

CMD /etc/init.d/monasca-agent start && tail -f /var/log/monasca/agent/collector.log
