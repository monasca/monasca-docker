# Setup storm and the threshold engine
FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r requirements.yml -p ./roles
# Ansilbe will fail on the last step, starting monasca-thresh. This is because storm is not running which can't run without zookeeper.
RUN ansible-playbook -i hosts site.yml -c local; echo "Monasca Thresh is expected to fail to start with initial install, all prior steps should succeed"

CMD ["/setup/start_thresh.sh"]
