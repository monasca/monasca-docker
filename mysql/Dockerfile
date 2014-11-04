# MySQL running Percona XtraDB cluster setup for Monasca
FROM monasca/base
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

COPY . /setup
WORKDIR /setup

# Pull down the roles and run Ansible
RUN ansible-galaxy install -r ansible_roles -p ./roles
# It is important to limit the tags here as monasca-schema could run influxd/kafka schema if not limited by tags.
RUN ansible-playbook -i hosts site.yml -c local --tags mysql,mysql_schema

EXPOSE 3306

CMD ["/usr/sbin/mysqld"]
