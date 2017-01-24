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

This image currently does not accept any environment variables or CLI arguments,
though a configuration can be provided as described below. Running the persister
with default settings should be simple, assuming the required services are
accessible:

```bash
docker run -it monasca/persister:latest
```

Configuration
-------------

Several environment variables can be used to configure the Python persister:
 * `DEBUG`: if `true`, enables `DEBUG`-level logging, default: `false`
 * `VERBOSE`: if `true` and `DEBUG=false`, use `INFO`-level logging (otherwise
   `WARN`), default: `true`
 * `ZOOKEEPER_URI`: the host and port for zookeeper, default: `zookeeper:2181`
 * `KAFKA_URI`: the host and port for kafka, default: `kafka:9092`
 * `INFLUX_HOST`: the host for influxdb, default: `influxdb`
 * `INFLUX_PORT`: the port for influxdb, default: `8086`
 * `INFLUX_USER`: the influx username, default: `mon_persister`
 * `INFLUX_PASSWORD`: the influx password, default: `password`
 * `INFLUX_DB`: the influx database name, default: `mon`

If additional values need to be overridden, the a new jinja2 template can be
provided by mounting a replacement at
`/etc/monasca-persister/persister.conf.j2`. If jinja2 formatting is not desired,
the environment variable `CONFIG_TEMPLATE` can be set to `false`.

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
[6]: https://github.com/openstack/monasca-api/
[7]: https://kubernetes.io/docs/user-guide/downward-api/
[8]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-persister-python/persister.conf.j2
