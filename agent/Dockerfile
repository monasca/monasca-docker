FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

# Setup start script and Ansible code
COPY . /setup
WORKDIR /setup

# This role needs git
RUN apt-get update
RUN apt-get install -y git

# Pull down the roles, startup keystone and run Ansible
RUN ansible-galaxy install -r requirements.yml -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

# Turn off syslog
RUN echo "log_to_syslog: no" >> /etc/monasca/agent/agent.conf

# This container will set up some simple default keystone users and alarm definitions before running
CMD ansible-playbook -i /setup/hosts /setup/monasca-keystone.yml -c local && /etc/init.d/monasca-agent start && tail -f /var/log/monasca/agent/collector.log
