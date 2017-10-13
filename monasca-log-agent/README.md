Monasca Log Agent
=================

This image use [Logstash][1] with [Logstash-output-monasca_log_api plugin][2]
that provide functionality to send all logs to [Monasca Log API][4].

Tags
----

Images in this repository are tagged as follows:

* `0.0.1`: standard [SemVer][3].
* `master`, `master-DATESTAMP`: unstable testing builds from the master branch,
  these may have features or enhancements not available in stable releases,
  but are not production-ready.

Usage
-----

Monasca Log Agent requires running instance of [Monasca Log API][4]
and Keystone.

When started Logstash will be listening on port configured with
`LOGSTASH_INPUT_PORT` variable (default to `5610`). It will accept all logs
send to this port in format specified in `LOGSTASH_INPUT_CODEC` (default
to `json`) coming on both TCP and UDP protocols.

To enable debug output from Logstash set `DEBUG` environment variable
to `True`.

This container is designed to work together with [Logspout][mon-logspout]
container that will connect to all running containers on machine
and proxy all they logs from `STDOUT` and `STDERR` to this container.

To add service dimension to any running container you need to initialize
it with `LOGSTASH_FIELDS` environment variable containing `kye=value`
pair of `service` as key and service name as value e.g.: `"service=mysql"`.

Configuration
-------------

|         Variable         |           Default           |                       Description                       |
|--------------------------|-----------------------------|---------------------------------------------------------|
| `MONASCA_LOG_API_URL`    | `http://log-api:5607/v3.0`  | Versioned Monasca Log API URL                           |
| `OS_AUTH_URL`            | `http://keystone:35357/v3/` | Versioned Keystone URL                                  |
| `OS_USERNAME`            | `monasca-agent`             | Agent Keystone username                                 |
| `OS_PASSWORD`            | `password`                  | Agent Keystone password                                 |
| `OS_USER_DOMAIN_NAME`    | `Default`                   | Agent Keystone user domain                              |
| `OS_PROJECT_NAME`        | `mini-mon`                  | Agent Keystone project name                             |
| `OS_PROJECT_DOMAIN_NAME` | `Default`                   | Agent Keystone project domain                           |
| `LOGSTASH_INPUT_PORT`    | `5610`                      | Logstash listen on this port (tcp and udp) for new logs |
| `LOGSTASH_INPUT_CODEC`   | `json`                      | Logstash expect logs in this format                     |

[1]: https://www.elastic.co/products/logstash
[2]: https://github.com/logstash-plugins/logstash-output-monasca_log_api
[3]: http://semver.org/
[4]: https://github.com/monasca/monasca-docker/tree/master/monasca-log-api
[mon-logspout]: https://github.com/monasca/monasca-docker/tree/master/logspout
