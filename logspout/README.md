Logspout
========

This image use [Logspout][1] with [Logspout-logstash plugin][2] that provide
functionality to send all logs to Logstash.

Logspout connect to all containers on same node, gather all their logs
from `STDOUT` and `STDERR` and proxy it to Logstash.

Tags
----

Images in this repository are tagged as follows:

* `0.0.1`: standard [SemVer][3].
* `latest`: the latest version recommended for use with other Monasca components.

Usage
-----

Logspout requires running instance of [Monasca Log Agent][4].

To add service dimension that you would be able to filter by in Kibana
you need to initialize running containers with `LOGSTASH_FIELDS` environment
variable containing `kye=value` pair of `service` key and service name
as a value e.g.: `"service=mysql"`.
Logspout will pickup this env variable and send proper data
to the Monasca Log Agent.

Multiline logging
-----------------

To handle [multiline logging][5] you need to pass a regex as a environment variable,
which matches the start of the multiline blocks e.g.:
`MULTILINE_PATTERN=^(\\[?\\d{4}-\\d{2}-\\d{2}|{)`

This example matches logs, which:

* start with a timestamp with format `YYYY-MM-DD` or `[YYYY-MM-DD`
* are json-logs

Note that in the case of a service generates logs, which don't follow any of these patterns,
the multiline bock will be chunked every period defined with `MULTILINE_FLUSH_AFTER` (default: 500 ms)

Configuration
-------------

|        Variable         |                 Default                   |             Description             |
|-------------------------|-------------------------------------------|-------------------------------------|
| `MONASCA_LOG_AGENT_URI` | `log-agent:5610`                          | Monasca Log Agent connection string |
| `ROUTE_URIS`            | `multiline+logstash+tcp://log-agent:5610` | Logstash connection string          |

Additional files
----------------

Files `build.sh` and `modules.go` are used by Logspout Dockerfile
(with `ONBUILD COPY` command) and allow us to build resulting binary
with needed plugin.

[1]: https://github.com/gliderlabs/logspout
[2]: https://github.com/looplab/logspout-logstash
[3]: http://semver.org/
[4]: https://github.com/monasca/monasca-docker/tree/master/monasca-log-agent
[5]: https://github.com/gliderlabs/logspout/#multiline-logging
