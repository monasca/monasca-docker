FROM monasca/openstack
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup
RUN chmod 755 /setup/demo-start.sh

# Some of the galaxy roles need git to download things, virtualenv is needed for our install
RUN apt-get update
RUN apt-get install -y git python-virtualenv

# Remove systemd as Ansible tries to use it if it exists
RUN apt-get remove -y systemd

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r requirements.yml -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

EXPOSE 80 5000 8080

CMD ["/setup/demo-start.sh"]
