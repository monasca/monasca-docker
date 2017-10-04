# Pipelines

**monasca-docker** is home for two pipelines, one for processing **metrics** and the other one
for processing **logs**. Each pipeline requires a set of services to be complete.

## Metric pipeline

**Metrics** pipeline requires the following services to be launched or available
(providing they are hosted externally):

* `agent-forwarder` - launches [monasca-agent-forwarder][1]
* `agent-collector` - launches [monasca-agent-collector][2]
* `zookeeper` - launches [Zookeeper][3]
* `influxdb` - launches [InfluxDB][4]
* `kafka` - launches [Kafka][5]
* `thresh` - launches [monasca-thresh][6]
* `monasca-sidecar` - launches [monasca-sidecar][7]
* `monasca-persister`- launches [monasca-persister][8]
* `monasca` - launches [monasca-api][9]
* `mysql` - launches [MySQL][10]
* `keystone` - launches [Keystone][11]
* `memcached` - launches [memcache][12]
* `monasca-notification` - launches [monasca-notification][13]
* `grafana` - launches [Grafana][14]
* `cadvisor` - launched [cadvisor][15]

Some of the services require initialization prior to launching, hence the following
are available:

* [mysql-init][16] for `mysql`
* [kafka-init][17] for `kafka`
* [influxdb-init][18] for `influxdb`
* [grafana-init][19] for `grafana`

There is also:

* `alarms` - that can be used to pre-create some [alarm-definitions][20] and
  [notification-methods][21].

## Log pipeline

**Logs** pipeline requires the following services to be launched or available
(providing they are hosted externally):

* `log-metrics` - launches [monasca-log-metrics][23]
* `log-api` - launches [monasca-log-api][24]
* `log-persister` - launches [monasca-log-persister][25]
* `kibana` - launches [Kibana][26]
* `log-transformer` - launches [monasca-log-transformer][27]
* `elasticsearch` - launches [ElasticSearch][28]

Some of the services require initialization prior to launching, hence the following
are available:

* [elasticsearch-init][22] for `elasticsearch`
* [kafka-log-init][17] for `kafka`

## Dependencies

The majority of services that are part of **monasca-docker** require one
or more additional services. The way to find out what dependencies a service has, is to open
[docker-compose.yml](../docker-compose.yml) or [log-pipeline.yml](../log-pipeline.yml)
(depends on the service) and check if its definition contains ```depends_on```.
For example:

[Kafka][5] from [docker-compose.yml](../docker-compose.yml) definition is:

```yml
kafka:
  image: monasca/kafka:${MON_KAFKA_VERSION}
  depends_on:
    - zookeeper
```

It ```depends_on``` on [Zookeeper][3]. That means that either:

* [Zookeeper][3] needs to be launched with ```docker-compose```
* [Zookeeper][3] should be provided externally and referenced with
   ```ZOOKEEPER_CONNECTION_STRING``` environmental variable

    If the components are hosted externally, you should remove depends_on.
    Otherwise docker-compose will try to launch the required
    services.

[1]: ../monasca-agent-collector/README.md
[2]: ../monasca-agent-forwarder/README.md
[3]: https://hub.docker.com/_/zookeeper/
[4]: https://hub.docker.com/_/influxdb/
[5]: ../kafka/README.md
[6]:../monasca-thresh/README.md
[7]: https://github.com/timothyb89/monasca-sidecar
[8]: ../monasca-persister-python/README.md
[9]: ../monasca-api-python/README.md
[10]: https://hub.docker.com/_/mysql/
[11]: ../keystone/README.md
[12]: https://hub.docker.com/_/memcached/
[13]: ../monasca-notification/README.md
[14]: ../grafana/README.md
[15]: https://hub.docker.com/r/google/cadvisor/
[16]: ../mysql-init/README.md
[17]: ../kafka-init/README.md
[18]: ../influxdb-init/README.md
[19]: ../grafana-init/README.md
[20]: https://github.com/openstack/monasca-api/blob/master/docs/monasca-api-spec.md#alarm-definitions-and-alarms
[21]: https://github.com/openstack/monasca-api/blob/master/docs/monasca-api-spec.md#notification-methods
[22]: ../elasticsearch-init/README.md
[23]: ../monasca-log-metrics/README.md
[24]: ../monasca-log-api/README.md
[25]: ../monasca-log-persister/README.md
[26]: ../kibana/README.md
[27]: ../monasca-log-transformer/README.md
[28]: https://hub.docker.com/_/elasticsearch/
