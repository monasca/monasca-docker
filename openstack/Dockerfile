# OpenStack Services for use with Monasca
FROM monasca/base:15.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# Install openstack components
RUN apt-get install -y keystone sqlite

# Setup start script
RUN chmod 755 /setup/start.sh

# Pull down the roles, startup keystone and run Ansible
RUN ansible-galaxy install -r requirements.yml -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

EXPOSE 80 5000 35357

CMD ["/setup/start.sh"]
