# InfluxDB setup for Monasca
FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# This role needs git
RUN apt-get update
RUN apt-get install -y git

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r requirements.yml -p ./roles
RUN ansible-playbook -i hosts site.yml -c local

EXPOSE 8083
EXPOSE 8086
EXPOSE 8084

CMD ["/usr/bin/influxdb", "-config=/opt/influxdb/shared/config.toml"]
