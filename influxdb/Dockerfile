# InfluxDB setup for Monasca
FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r ansible_roles -p ./roles
# It is important to limit the tags here as monasca-schema could run mysql/kafka schema if not limited by tags.
RUN ansible-playbook -i hosts site.yml -c local --tags influxdb,influxdb_schema

EXPOSE 8083
EXPOSE 8086
EXPOSE 8084

CMD ["/usr/bin/influxdb", "-config=/opt/influxdb/shared/config.toml"]
