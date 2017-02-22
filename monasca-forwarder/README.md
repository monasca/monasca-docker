monasca-forwarder Dockerfile
===============================

This image has a containerized version of the Monasca Forwarder Engine which is not
an official part of the Monasca projects. For more information on the Monasca project,
see [the wiki][1].

Sources: middot; [monasca-docker][3] &middot; [Dockerfile][4]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.7.0`
 * `1.0.0`, `1.0`, `1`: standard semver tags based on git tags in the
   [official repository][2].
 * `newton`, `ocata`, etc: named versions following OpenStack release names
   built from the tip of `stable/RELEASENAME` branches in the repository
 * `master`, `master-DATESTAMP`: unstable testing builds from the master branch,
   these may have features or enhancements not available in stable releases, but
   are not production-ready.

Note that features in this Dockerfile, particularly relating to running in
Docker and Kubernetes environments, require code that has not yet been made
available in a tagged release. Until this changes, only `master` images may be
available and `latest` may point to `master` images.

Usage
-----

The forwarder requires configured instances of Kafka,
Zookeeper, and the remote [monasca-api][5]. In environments resembling the official
[docker-compose][3] or [Kubernetes][6] environments, this image still requires 
configuration, see below for required variables.

    docker run monasca/forwarder:latest

Configuration
-------------

| Variable                | Default          | Description                                        |
|-------------------------|------------------|----------------------------------------------------|
| `DEBUG`                 | `false`          | If `true`, enable debug logging                    |
| `VERBOSE`               | `true`           | If `true`, enable info logging                     |
| `KAFKA_URL`             | `kafka:9092`     | If `true`, disable remote root login               |
| `KAFKA_WAIT_FOR_TOPICS` | `metrics`        | Comma-separated list of topic names to check       |
| `KAFKA_WAIT_RETRIES`    | `24`             | # of tries to verify Kafka availability            |
| `KAFKA_WAIT_DELAY`      | `5`              | # seconds between retry attempts                   |
| `ZOOKEEPER_URL`         | `zookeeper:2181` | Zookeeper URL                                      |
| `MONASCA_PROJECT_ID`    | unset            | Required: Project id to be used for authentication |
| `METRIC_PROJECT_ID`     | unset            | Optional remote project id for storing metrics     |
| `MONASCA_ROLE`          | `monasca-agent`  | Role to be used for authentication                 |
| `REMOTE_API_URL`        | unset            | Required URL of the remote Monasca API             |
| `USE_INSECURE`          | `false`          | If true, do not validate ssl hostname              |
| `METRICS_TO_FORWARD`    | unset            | Required: yaml description of metrics to forward   |


[1]: https://wiki.openstack.org/wiki/Monasca
[2]: https://github.hpe.com/openstack/monasca-forwarder/
[3]: https://github.com/hpcloud-mon/monasca-docker/
[4]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-forwarder/Dockerfile
[5]: https://hub.docker.com/r/monasca/api/
[6]: https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/
[7]: https://v2.developer.pagerduty.com/docs/events-api
