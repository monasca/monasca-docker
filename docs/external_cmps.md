# External components

By default, plain ```docker-compose up```, assuming both pipelines are included,
will start containers for following services:

* MySQL
* Keystone
* ElasticSearch
* Zookeeper
* Kafka

However, each of them is treated, at the same time as the
dependency for *Monasca*, hence can be externalized with the help
of appropriate *environmental variables*.

The following guide presents how to achieve that.

## Using external OpenStack Keystone

By default `monasca-docker` uses Keystone stored in separate
container. But if you want to use an external Keystone you need to
overwrite some environment variables in specific containers.

Remove the `keystone` image initialization and all references to this
image from `depends_on`, from other services, from
`docker-compose.yml` and `log-pipeline.yml` files.

Example configuration taking into account usage of Keystone
aliases instead of ports when overwriting environment variables:

#### `docker-compose.yml`

In `agent-forwarder` and `agent-collector`:
```yaml
environment:
  OS_AUTH_URL: http://192.168.10.6/identity/v3
  OS_USERNAME: monasca-agent
  OS_PASSWORD: password
  OS_PROJECT_NAME: mini-mon
```

In `alarms`:
```yaml
environment:
  OS_AUTH_URL: http://192.168.10.6/identity/v3
  OS_USERNAME: mini-mon
  OS_PASSWORD: password
  OS_PROJECT_NAME: mini-mon
```

In `monasca`:
```yaml
environment:
  KEYSTONE_IDENTITY_URI: http://192.168.10.6/identity
  KEYSTONE_AUTH_URI: http://192.168.10.6/identity
  KEYSTONE_ADMIN_USER: admin
  KEYSTONE_ADMIN_PASSWORD: secretadmin
```

In `grafana`:
```yaml
environment:
  GF_AUTH_KEYSTONE_AUTH_URL: http://192.168.10.6/identity
```

#### `log-pipeline.yml`

In `kibana`:
```yaml
environment:
  KEYSTONE_URI: 192.168.10.6/identity
```

In `log-api`:
```yaml
environment:
  KEYSTONE_AUTH_URI: http://192.168.10.6/identity
  KEYSTONE_IDENTITY_URI: http://192.168.10.6/identity
  KEYSTONE_ADMIN_USER: admin
  KEYSTONE_ADMIN_PASSWORD: secretadmin
```
