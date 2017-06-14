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

    docker run -it monasca/agent:latest

However, without any plugins enabled (the default config), the agent will not
collect any metrics. This agent container supports a number of "monitoring
scenarios" that can be enabled via environment variables passed at container
startup:

 * Docker container monitoring: On a plain Docker host, collects standard
   system-level metrics about each running container (e.g. cpu, memory, etc).
   Requires `DOCKER=true`.
 * Kubernetes container monitoring: Collects container metrics for a particular
   node from cAdvisor. Intended to be run on each node as a `DaemonSet`.
   Requires `KUBERNETES=true`.
 * Kubernetes API monitoring: Collects metrics about a Kubernetes cluster,
   including health status, node disk/memory pressure, capacities, etc.
   Requires `KUBERNETES_API=true`.
 * cAdvisor monitoring: collects host metrics from a cAdvisor instance, such as
   the instance embedded in the Kubernetes API server. Requires `CADVISOR=true`.
 * Prometheus monitoring: Scrapes metrics from applications exposing Prometheus
   endpoints. In Kubernetes environments, these can be detected automatically
   when run alongside the Kubernetes plugin. Requires `PROMETHEUS=true`.

Note that when running in a Kubernetes environment, additional variables must be
set via the [Downward API][7]:

 * `AGENT_POD_NAME`: set `fieldRef` to `fieldPath: metadata.name`
 * `AGENT_POD_NAMESPACE`: set `fieldRef` to `fieldPath: metadata.namespace`

When monitoring parts of a Kubernetes environment externally, additional
variables must be set instead, see below for details.

Configuration
-------------

| Variable                 | Default          | Description                         |
|--------------------------|------------------|-------------------------------------|
| `LOG_LEVEL`              | `WARN`           | Python logging level                |
| `OS_AUTH_URL`            | `http://keystone:35357/v3/` | Versioned Keystone URL   |
| `OS_USERNAME`            | `monasca-agent`  | Agent Keystone username             |
| `OS_PASSWORD`            | `password`       | Agent Keystone password             |
| `OS_USER_DOMAIN_NAME`    | `Default`        | Agent Keystone user domain          |
| `OS_PROJECT_NAME`        | `mini-mon`       | Agent Keystone project name         |
| `OS_PROJECT_DOMAIN_NAME` | `Default`        | Agent Keystone project domain       |
| `MONASCA_URL`            | `http://monasca:8070/v2.0` | Versioned Monasca API URL |
| `HOSTNAME_FROM_KUBERNETES` | `false` | If true, determine node hostname from Kubernetes  |
| 'NON_LOCAL_TRAFFIC'        | `false` | If true, collector listens on all addresses |

Note that additional variables can be specified as well, see the
[config template][8] for a definitive list.


Building
--------

[dbuild][9] can be used with the build.yml file to build and push the
container.

To build the container from scratch using just docker commands, run:

    docker build -t youruser/agent-forwarder:latest .

A few build argument can be set:

 * `AGENT_USER`: the user to run the agent as. The same user must be specified
   as the user specified when the agent-base image was built.
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
