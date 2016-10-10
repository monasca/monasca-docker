# OpenStack Services for use with Monasca
FROM monasca/base:15.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

RUN apt-get update
RUN apt-get install -y sudo

# Setup start script and Ansible code
COPY . /setup
WORKDIR /setup
RUN chmod 755 /setup/start.sh

# Pull down the roles, startup keystone and run Ansible
RUN ansible-galaxy install -r requirements.yml -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

RUN apt-get clean

EXPOSE 80 5000 35357

CMD ["/setup/start.sh"]
