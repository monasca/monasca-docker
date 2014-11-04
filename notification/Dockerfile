FROM monasca/base:14.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r ansible_roles -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

CMD ["/setup/monasca-notification.sh"]
