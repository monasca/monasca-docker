monasca-agent-forwarder Dockerfile
========================

This image contains a containerized version of the Monasca agent forwarder. For
more information on the Monasca project, see [the wiki][1]. It is based on the
agent-base image also built in monasca-docker.

Sources: [monasca-agent][2] &middot; [monasca-docker][3] &middot; [Dockerfile][4]

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

The agent forwarder requires a reachable [Monasca API][5] server.

In environments resembling the official [docker-compose][3] or [Kubernetes][6]
environments, the image does not require additional configuration parameters and
can be minimally run like so:

    docker run -it monasca/agent-forwarder:latest

Configuration
-------------

| Variable                    | Default          | Description                         |
|-----------------------------|------------------|-------------------------------------|
| `LOG_LEVEL`                 | `WARN`           | Python logging level                |
| `KEYSTONE_DEFAULTS_ENABLED` | `true`           | Sets all OS defaults                |
| `OS_AUTH_URL`               | `http://keystone:35357/v3/` | Versioned Keystone URL   |
| `OS_USERNAME`               | `monasca-agent`  | Agent Keystone username             |
| `OS_PASSWORD`               | `password`       | Agent Keystone password             |
| `OS_USER_DOMAIN_NAME`       | `Default`        | Agent Keystone user domain          |
| `OS_PROJECT_NAME`           | `mini-mon`       | Agent Keystone project name         |
| `OS_PROJECT_DOMAIN_NAME`    | `Default`        | Agent Keystone project domain       |
| `MONASCA_URL`               | `http://monasca:8070/v2.0` | Versioned Monasca API URL |
| `HOSTNAME_FROM_KUBERNETES`  | `false` | If true, determine node hostname from Kubernetes  |
| `NON_LOCAL_TRAFFIC`         | `false` | If true, forwarder listens on all addresses |

Note that additional variables can be specified as well, see the
[config template][8] for a definitive list.


Building
--------

[dbuild][9] can be used with the build.yml file to build and push the
container.

To build the container from scratch using just docker commands, run:

    docker build -t youruser/agent-forwarder:latest .

A few build argument can be set:

 * `REBULID`: a simple method to invalidate the Docker image cache. Set to
   `--build-arg REBUILD="$(date)"` to force a full image rebuild.
 * `HTTP_PROXY` and `HTTPS_PROXY` should be set as needed for your environment

If you'd like to build this image against an uncommitted working tree, consider
using [git-sync][10] to mirror your local tree to a temporary git repository.

[1]: https://wiki.openstack.org/wiki/Monasca
[2]: https://github.com/openstack/monasca-agent
[3]: https://github.com/hpcloud-mon/monasca-docker/
[4]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-agent/Dockerfile
[5]: https://hub.docker.com/r/monasca/api/
[6]: https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/
[7]: https://kubernetes.io/docs/user-guide/downward-api/
[8]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-agent/agent.yaml.j2
[9]: https://github.com/timothyb89/dbuild
[10]: https://github.com/timothyb89/git-sync
