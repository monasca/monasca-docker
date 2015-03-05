FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r requirements.yml -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

EXPOSE 9092

# Requires Zookeeper to run
CMD ["/bin/bash", "/setup/create_topics.sh"]
