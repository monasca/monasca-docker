FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r ansible_roles -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

EXPOSE 2181

CMD ["/setup/zk_start.sh"]
