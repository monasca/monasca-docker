monasca-statsd Dockerfile
========================

This image contains a containerized version of the Monasca statsd. For
more information on the Monasca project, see [the wiki][1]. It is based on the
agent-base image also built in monasca-docker.

Sources: [monasca-statsd][2] &middot; [monasca-docker][3] &middot; [Dockerfile][4]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.6.0`
 * `1.6.0`, `1.6`, `1`: standard semver tags, based on git tags in the
   [official repository][2].
 * `mitaka`, `newton`, etc: named versions following OpenStack release names
   built from the tip of `stable/RELEASENAME` branches in the repository
 * `master`, `master-DATESTAMP`: unstable testing builds from the master branch,
   these may have features or enhancements not available in stable releases, but
   are not production-ready.

Usage
-----

In environments resembling the official [docker-compose][3] or [Kubernetes][4]
environments, the image does not require additional configuration parameters and
can be minimally run like so:

    docker run -it monasca/statsd:latest

Configuration
-------------

| Variable            | Default                  | Description                                     |
|---------------------|--------------------------|-------------------------------------------------|
| `FORWARDER_URL`     | `http://localhost:17123` | The agent forwarder url address                 |
| `NON_LOCAL_TRAFFIC` | `true`                   | If true, statsd daemon listens on all addresses |
| `STATSD_PORT`       | `8125`                   | The port to listen for client connections       |
| `LOG_LEVEL`         | `WARN`                   | Python logging level                            |

Building
--------

[dbuild][5] can be used with the build.yml file to build and push the
container.

To build the container from scratch using just docker commands, run:

    docker build -t youruser/agent-statsd:latest .

A few build argument can be set:

 * `REBULID`: a simple method to invalidate the Docker image cache. Set to
   `--build-arg REBUILD="$(date)"` to force a full image rebuild.
 * `HTTP_PROXY` and `HTTPS_PROXY` should be set as needed for your environment

If you'd like to build this image against an uncommitted working tree, consider
using [git-sync][6] to mirror your local tree to a temporary git repository.

[1]: https://wiki.openstack.org/wiki/Monasca
[2]: https://github.com/openstack/monasca-statsd
[3]: https://github.com/monasca/monasca-docker/
[4]: https://github.com/monasca/monasca-docker/blob/master/k8s/
[5]: https://github.com/timothyb89/dbuild
[6]: https://github.com/timothyb89/git-sync
