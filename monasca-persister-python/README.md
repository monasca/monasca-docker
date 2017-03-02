monasca-persister Dockerfile
============================

This image contains a containerized version of the Monasca persister.

There are two implementations of the monasca-persister:

 * python (tagged `-python` or empty) - [Dockerfile][1]
 * java (tagged `-java`) - [Dockerfile][2]

Currently the `python` images are recommended. For more information on the
Monasca project, see [the wiki][3].

Source repositories: [monasca-persister][4] &middot; [monasca-docker][5]

Tags
----

The images in this repository follow a few tagging conventions:

 * `latest`: refers to the latest stable Python point release, e.g.
   `1.3.0-python`
 * `latest-python`, `latest-java`: as above, but specifically referring to the
   latest stable Python or Java point release, e.g. `1.3.0`
 * `1.3.0`, `1.3`, `1`: standard semver tags, based on git tags in the
   [official repository][4]
 * `1.3.0-python`, `1.3-python`, `1-python`: as above, but specifically
   referring to python-based images
 * `mitaka`, `newton`, etc: named versions following OpenStack release names
   built from the tip of the `stable/RELEASENAME` branches in the repository
 * `mitaka-python`, `newton-python`: as above, but specifically Python-based
   images
 * `master`, `master-DATESTAMP`: unstable builds from the master branch, not
   intended for general use

Note that unless otherwise specified, images will be Python-based. All
Java-based images will be tagged as such.

Usage
-----

To run, the persister needs to connect to a working Zookeeper and Kafka as well
as a database. To do anything of use, one or more [monasca-api][6] instances
should output to the Kafka topic as well.

In environments resembling the [official Kubernetes environment][7] the image
does not require additional configuration parameters, and can be run like so:

```bash
docker run -it monasca/persister:latest
```

Configuration
-------------

| Variable          | Default          | Description                      |
|-------------------|------------------|----------------------------------|
| `DEBUG`           | `false`          | If `true`, enable debug logging  |
| `VERBOSE`         | `true`           | If `true`, enable info logging   |
| `ZOOKEEPER_URI`   | `zookeeper:2181` | The host and port for zookeeper  |
| `KAFKA_URI`       | `kafka:9092`     | The host and port for kafka      |
| `KAFKA_WAIT_FOR_TOPICS` | `alarm-state-transitions,metrics` | Topics to wait on at startup |
| `INFLUX_HOST`     | `influxdb`       | The host for influxdb            |
| `INFLUX_PORT`     | `8086`           | The port for influxdb            |
| `INFLUX_USER`     | `mon_persister`  | The influx username              |
| `INFLUX_PASSWORD` | `password`       | The influx password              |
| `INFLUX_DB`       | `mon`            | The influx database name         |

If additional values need to be overridden, a new config file or jinja2 template
can be provided by mounting a replacement at
`/etc/monasca-persister/persister.conf.j2`. If jinja2 formatting is not desired,
the environment variable `CONFIG_TEMPLATE` can be set to `false`. Note that the
jinja2 template should still be overwritten (rather than the target file without
the `.j2` suffix) as it will be copied at runtime.

The config file source is available [in the repository][8]. If necessary, the
generated config file can be viewed at runtime by running:

```bash
docker exec -it some_container_id cat /etc/monasca-persister/persister.conf
```

[1]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-persister-python/Dockerfile
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-persister-java/Dockerfile
[3]: https://wiki.openstack.org/wiki/Monasca
[4]: https://github.com/openstack/monasca-persister/
[5]: https://github.com/hpcloud-mon/monasca-docker/
[6]: https://hub.docker.com/r/monasca/api/
[7]: https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/
[8]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-persister-python/persister.conf.j2
