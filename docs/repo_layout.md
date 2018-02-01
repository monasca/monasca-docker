# Repository Layout

 * `monasca-api-python/`: Dockerfile for monasca-api (python version)
 * `monasca-persister-python/`: Dockerfile for monasca-persister (python
   version)
 * `monasca-notification/`: Dockerfile for the notification engine
 * `monasca-agent/`: Dockerfile for Monasca Agent

There are also several run-once init containers used to bootstrap a new
Monasca installation:
 * `grafana-init/`: pre-loads Grafana with a Monasca datasource and several
   default dashboard
 * `influxdb-init/`: creates influxdb users and databases
 * `monasca-thresh/`: job to submit the monasca-thresh Storm topology
 * `mysql-init/`: initializes MySQL users, databases, and schemas

A number of custom dependency containers are also here:

 * `grafana/`: Dockerfile for Grafana with Keystone auth and Monasca plugins
 * `keystone/`: Dockerfile for dev keystone
 * `kafka/`: Dockerfile for k8s-compatible Kafka
 * `storm/`: Dockerfile for Storm container
