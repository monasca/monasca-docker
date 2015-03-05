FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

# Setup start script and Ansible code
COPY . /setup
WORKDIR /setup

# Pull down the roles, startup keystone and run Ansible
RUN ansible-galaxy install -r requirements.yml -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

# Turn off syslog
RUN echo "log_to_syslog: no" >> /etc/monasca/agent/agent.conf

CMD /etc/init.d/monasca-agent start && tail -f /var/log/monasca/agent/collector.log
