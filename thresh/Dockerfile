# Setup storm and the threshold engine
FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# This playbook requires https for apt
RUN apt-get install -y apt-transport-https

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r ansible_roles -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

CMD ["/setup/start_thresh.sh"]
