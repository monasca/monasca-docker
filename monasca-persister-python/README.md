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

The default configuration file refers to the following services:
 * `zookeeper` at `zookeeper:2181`
 * `kafka` at `kafka:9092`
 * `influxdb` at `influxdb`, port `8086`

If these default values are not appropriate for your environment, they can be
overridden by mounting a corrected config file to
`/etc/monasca-persister/persister.conf`.

Roadmap
-------

Future revisions of this image should support environment configuration for the
recommended configuration (e.g. standard kafka -> persister -> influx), in
particular hostnames and ports for the external services as well as logging
levels.

[1]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-persister-python/Dockerfile
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-persister-java/Dockerfile
[3]: https://wiki.openstack.org/wiki/Monasca
[4]: https://github.com/openstack/monasca-persister/
[5]: https://github.com/hpcloud-mon/monasca-docker/
[6]: https://github.com/openstack/monasca-api/
