FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r requirements.yml -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

EXPOSE 8080

CMD ["/usr/bin/java", "-Xmx8g", "-cp", "/opt/monasca/monasca-api.jar", "monasca.api.MonApiApplication", "server", "/etc/monasca/api-config.yml"]
