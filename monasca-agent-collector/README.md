monasca-agent-collector Dockerfile
========================

This image contains a containerized version of the Monasca agent collector. For
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

Note that features in this Dockerfile, particularly relating to Docker and
Kubernetes monitoring, require plugins that have not yet been officially
released or merged. Until this changes, only `master` images may be available.

Usage
-----

The agent collector requires at least a reachable [monasca-forwarder][5]. Access
to additional services, like the Kubernetes API, is also necessary if they are to
be monitored.

In environments resembling the official [docker-compose][3] or [Kubernetes][6]
environments, the image does not require additional configuration parameters and
can be minimally run like so:

    docker run -it monasca/agent-collector:latest

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
| `FORWARDER_URL`             | `http://localhost:17123` | Monasca Agent Collector URL |
| `AUTORESTART`               | `false`          | Auto Restart Monasca Agent Collector |
| `COLLECTOR_RESTART_INTERVAL`| `24`             | Interval in hours to restart Monasca Agent Collector |

Note that additional variables can be specified as well, see the
[config template][8] for a definitive list.

Note that the auto restart feature can be enabled if the agent collector has unchecked
memory growth. The proper restart behavior must be enabled in docker or kubernetes if
this feature is turned on.

### Docker Plugin

This plugin is enabled when `DOCKER=true`. It has the following options:

 * `DOCKER_ROOT`: The mounted host rootfs volume. Default: `/host`
 * `DOCKER_SOCKET`: The mounted Docker socket. Default: `/var/run/docker.sock`

This plugin monitors Docker containers directly. It should only be used in a
bare Docker environment (i.e. not Kubernetes), and requires two mounted volumes
from the host:

 * Host `/` mounted to `/host` (path configurable with `DOCKER_ROOT`)
 * Host `/var/run/docker.sock` mounted to `/var/run/docker.sock` (path
   configurable with `DOCKER_SOCKET`)

### Kubernetes Plugin

This plugin is enabled when `KUBERNETES=true`. It has the following options:

 * `KUBERNETES_TIMEOUT`: The K8s API connection timeout. Default: `3`
 * `KUBERNETES_NAMESPACE_ANNOTATIONS`: If set, will grab annotations from
   namespaces to include as dimensions for metrics that are under that
   namespace. Should be passed in as 'annotation1,annotation2,annotation3'.
   Default: unset
 * `KUBERNETES_MINIMUM_WHITELIST`: Sets whitelist on kubernetes plugin for
   the following metrics pod.cpu.total_time_sec, pod.mem.cache_bytes,
   pod.mem.swap_bytes, pod.mem.used_bytes, pod.mem.working_set_bytes. This
   will alleviate the amount of load on Monasca.
   Default: unset

The Kubernetes plugin is intended to be run as a DaemonSet on each Kubernetes
node. In order for API endpoints to be detected correctly, `AGENT_POD_NAME` and
`AGENT_POD_NAMESPACE` must be set using the [Downward API][7] as described
above.

### Kubernetes API Plugin

This plugin is enabled when `KUBERNETES_API=true`. It has the following options:

 * `KUBERNETES_API_HOST`: If set, manually sets the location of the Kubernetes
   API host. Default: unset
 * `KUBERNETES_API_PORT`: If set, manually sets the port for of the Kubernetes
   API host. Only used if `KUBERNETES_API_HOST` is also set. Default: 8080
 * `KUBERNETES_API_CUSTOM_LABELS`: If set, provides a list of Kubernetes label
   keys to include as dimensions from gathered metrics. Labels should be comma
   separated strings, such as `label1,label2,label3`. The `app` label is always
   included regardless of this value. Default: unset
 * `KUBERNETES_NAMESPACE_ANNOTATIONS`: If set, will grab annotations from
   namespaces to include as dimensions for metrics that are under that
   namespace. Should be passed in as 'annotation1,annotation2,annotation3'.
   Default: unset
 * `REPORT_PERSISTENT_STORAGE`: If set, will gather bound pvc per a storage
   class. Will be reported by namespace and cluster wide. Default: true
 * `STORAGE_PARAMETERS_DIMENSIONS`: If set and report_persistent_storage is
   set, will grab storage class parameters as dimensions when reporting
   persistent storage. Should be passed in as 'parameter1,parameter2". Default:
   unset

The Kubernetes API plugin is intended to be run as a standalone deployment and
will collect cluster-level metrics.

### Prometheus Plugin

This plugin is enabled when `PROMETHEUS=true`. It has the following options:

 * `PROMETHEUS_TIMEOUT`: The connection timeout. Default: `3`
 * `PROMETHEUS_ENDPOINTS`: A list of endpoints to scrape. If unset,
   they will be determined automatically via the Kubernetes API. See below for
   syntax. Default: unset
 * `PROMETHEUS_DETECT_METHOD`: When endpoints are determined automatically,
   this specifies the resource type to scan, one of: `pod`, `service`.
   Default: `pod`
 * `PROMETHEUS_KUBERNETES_LABELS`: When endpoints are determined automatically,
   this comma-separated list of labels will be included as dimensions (by name).
   Default: `app`

If desired, a static list of Prometheus endpoints can be provided by setting
`PROMETHEUS_ENDPOINTS`. Entries in this list should be comma-separated.
Additionally, each entry can specify a set of dimensions like so:

    http://host-a/metrics,http://host-b/metrics|prop=value&prop2=value2,http://host-c

Note that setting `PROMETHEUS_ENDPOINTS` disables autodetection.

When autodetection is enabled, this plugin will automatically scrape all
annotated Prometheus endpoints on the node the agent is running on. Ideally, it
should be run alongside the Kubernetes plugin as a DaemonSet on each node.

### cAdvisor_host Plugin

This plugin is enabled when `CADVISOR=true`. It has the following options:

 * `CADVISOR_TIMEOUT`: The connection timeout for the cAdvisor API. Default: `3`
 * `CADVISOR_URL`: If set, sets the URL at which to access cAdvisor. If unset,
   (default) the cAdvisor host will be determined automatically via the
   Kubernetes API.
 * `CADVISOR_MINIMUM_WHITELIST`: Sets whitelist on cadvisor host plugin for
   the following metrics cpu.total_time_sec, mem.cache_bytes,
   mem.swap_bytes, mem.used_bytes, mem.working_set_bytes. This
   will alleviate the amount of load on Monasca.
   Default: unset

This plugin collects host-level metrics from a running cAdvisor instance.
cAdvisor is included in `kubelet` when in Kubernetes environments and is
necessary to retrieve host-level metrics. As with the Kubernetes plugin,
`AGENT_POD_NAME` and `AGENT_POD_NAMESPACE` must be set to determine the URL
automatically.

cAdvisor can be easily run in [standard Docker environments][9] or directly on
host systems. In these cases, the URL must be manually provided via
`CADVISOR_URL`.

### Monasca-monitoring

#### Metrics pipeline
The monasca-monitoring enables plugins for HTTP endpoint check and processes.
Additionally enables plugins for detailed metrics for the following components:
Kafka, MySQL, and Zookeeper. This is enabled when MONASCA_MONITORING=true.
The components use the default configuration. A user can specify own settings
for them in docker-compose file. To customize those settings you can adjust the
configuration of the components by passing environment variables:

##### Kafka

 * `KAFKA_CONNECT_STR`: The kafka connection string. Default: `kafka:9092`

##### Zookeeper

 * `ZOOKEEPER_HOST`: The zookeeper host name.  Default: `zookeeper`
 * `ZOOKEEPER_PORT`: The port to listen for client connections. Default: `2181`

##### MySQL

 * `MYSQL_SERVER`: The MySQL server name. Default: `mysql`
 * `MYSQL_USER`, `MYSQL_PASSWORD`: These variables are used in conjunction to
 specify user and password for this user. Default: `root` and `secretmysql`
 * `MYSQL_PORT`: The port to listen for client connections. Default: `3306`

#### Logs pipeline
For logs pipeline you can enable HTTP endpoint check, process and
`Elasticsearch` plugins. This is enabled when `MONASCA_LOG_MONITORING=true`.
You can adjust the configuration of the components by passing environment
variables:

##### Elasticsearch
  * `ELASTIC_URL`: The Elasticsearch connection string. Default: `http://elasticsearch:9200`

#### Monasca-statsd
To monitor `monasca-notifcation` and `monasca-log-api` use `statsd`. Enable the
statsd monitoring by setting up `STATSD_HOST` and `STATSD_PORT` environment
variables in those projects.

### Custom Plugins

Custom plugin configuration files can be provided to the container by mounting
them to `/plugins.d/*.yaml`. If they have a `.j2` extension, they will be
processed as Jinja2 templates with access to all environment variables.

Building
--------

[dbuild][10] can be used with the build.yml file to build and push the
container.

To build the container from scratch using just docker commands, run:

    docker build -t youruser/agent-collector:latest .

A few build argument can be set:

 * `REBULID`: a simple method to invalidate the Docker image cache. Set to
   `--build-arg REBUILD="$(date)"` to force a full image rebuild.
 * `HTTP_PROXY` and `HTTPS_PROXY` should be set as needed for your environment

If you'd like to build this image against an uncommitted working tree, consider
using [git-sync][11] to mirror your local tree to a temporary git repository.

[1]: https://wiki.openstack.org/wiki/Monasca
[2]: https://github.com/openstack/monasca-agent
[3]: https://github.com/hpcloud-mon/monasca-docker/
[4]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-agent/Dockerfile
[5]: https://hub.docker.com/r/monasca/agent-forwarder/
[6]: https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/
[7]: https://kubernetes.io/docs/user-guide/downward-api/
[8]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-agent/agent.yaml.j2
[9]: https://github.com/google/cadvisor#quick-start-running-cadvisor-in-a-docker-container
[10]: https://github.com/timothyb89/dbuild
[11]: https://github.com/timothyb89/git-sync
