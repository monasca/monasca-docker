FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# This playbook requires https for apt
RUN apt-get install -y apt-transport-https

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r ansible_roles -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

EXPOSE 8080

CMD ["/usr/bin/java", "-Xmx8g", "-cp", "/opt/monasca/monasca-api.jar", "monasca.api.MonApiApplication", "server", "/etc/monasca/api-config.yml"]
