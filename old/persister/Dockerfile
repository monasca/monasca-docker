FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

RUN apt-get update
RUN apt-get install -y openjdk-7-jre-headless

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r requirements.yml -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

CMD ["/usr/bin/java", "-Dfile.encoding=UTF-8", "-Xmx8g", "-cp", "/opt/monasca/monasca-persister.jar:/opt/monasca/vertica/vertica_jdbc.jar", "monasca.persister.PersisterApplication", "server", "/etc/monasca/persister-config.yml"]
