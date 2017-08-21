monasca-log-api
===============

This image contains containerized version of Monasca Log API.
For more details about monasca-log-api, please visit:

* [monasca-log-api's documentation][1]
* [monasca-log-api's API reference][2]
* [monasca-log-api's repository][3]

Tags
----

The images in this repository follow a few tagging conventions:

* `latest`: refers to the latest stable Python point release, e.g.
  `2.2.1`
* `2.2.1`, `2.2`, `2`: standard semver tags, based on git tags in the
  [official repository][3]
* `ocata`: named versions following OpenStack release names
  built from the tip of the `stable/RELEASENAME` branches in the repository
* `master`, `master-DATESTAMP`: unstable builds from the master branch, not
intended for general use

Usage
-----

In order to run monasca-log-api container, [Kafka][4] needs to be available.
Once it is, **monasca-log-api** can be launched using
```docker run -p 5607:5607 -l kafka monasca/log-api:latest``` .

Configuration
-------------

A number of environment variables can be passed to the container:

| Variable                         | Default      | Description                       |
|--------------------------------  |--------------|-----------------------------------|
| `LOG_LEVEL_ROOT`                 | `WARN`       | The level of the root logger      |
| `LOG_LEVEL_CONSOLE`              | `INFO`       | Minimum level for console output  |
| `LOG_LEVEL_ACCESS`               | `INFO`       | Minimum level for access output   |
| `MONASCA_CONTAINER_LOG_API_PORT` | `5607`       | The Log API's HTTP port           |
| `KAFKA_URI`                      | `kafka:9092` | The host and port for kafka       |
| `KAFKA_WAIT_FOR_TOPICS`          | `log`        | Topics to wait on at startup      |
| `KAFKA_WAIT_RETRIES`             | `24`         | # of kafka wait attempts          |
| `KAFKA_WAIT_DELAY`               | `5`          | seconds to wait between attempts  |
| `KEYSTONE_IDENTITY_URI`          | `http://keystone:35357` | Keystone identity address |
| `KEYSTONE_AUTH_URI`              | `http://keystone:5000`  | Keystone auth address  |
| `KEYSTONE_ADMIN_USER`            | `admin`       | Keystone admin account user      |
| `KEYSTONE_ADMIN_PASSWORD`        | `secretadmin` | Keystone admin account password  |
| `KEYSTONE_ADMIN_TENANT`          | `admin`       | Keystone admin account tenant    |
| `KEYSTONE_ADMIN_DOMAIN`          | `default`     | Keystone admin domain            |
| `MEMCACHED_URI`                  | `memcached:11211` | A list of URIs pointing at memcached |
| `AUTHORIZED_ROLES`               | `admin, domainuser, domainadmin, monasca-user`   | Roles for admin Users |
| `AGENT_AUTHORIZED_ROLES`         | `monasca-agent` | Roles for metric write only users |
| `GUNICORN_WORKERS`               | `9`           | number of API worker processes   |
| `GUNICORN_WORKER_CLASS`          | `gevent`      | async worker class               |
| `GUNICORN_WORKER_CONNECTIONS`    | `2000`        | no. connections for async worker |
| `GUNICORN_BACKLOG`               | `1000`        | gunicorn backlog size            |
| `GUNICORN_TIMEOUT`               | `1000`        | gunicorn timeout                 |
| `ADD_ACCESS_LOG`                 | `true`        | if true, produce an access log on stderr |
| `ACCESS_LOG_FORMAT` | `%(asctime)s [%(process)d] gunicorn.access [%(levelname)s] %(message)s` | Log format for access log |
| `ACCESS_LOG_FIELDS` | `%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s "%(f)s" "%(a)s" %(L)s` | Access log fields |

If additional values need to be overridden, new config files or jinja2 templates
can be provided by mounting a replacement on top of the original template:

 * `/etc/monasca/log-api.conf.j2`
 * `/etc/monasca/log-api-paste.ini.j2`
 * `/etc/monasca/log-api-logging.conf.j2`

If jinja2 formatting is not desired, the environment variable `CONFIG_TEMPLATE`
can be set to `false`. Note that the jinja2 template should still be overwritten
(rather than the target file without the `.j2` suffix) as it will be copied at
runtime.

The config file sources are available [in the repository][5]. If necessary, the
generated config files can be viewed at runtime by running:

```bash
docker exec -it some_container_id cat /etc/monasca/log-api.conf
docker exec -it some_container_id cat /etc/monasca/log-api-paste.ini
docker exec -it some_container_id cat /etc/monasca/log-api-logging.conf
```

Troubleshooting
-------------

Container status can be checked by the following command (example):
```bash
docker ps --filter 'name=log-api' --format '{{.Names}}\t{{.Image}}\t{{.Status}}'
```

Result of health check can be get by the following command:
```bash
docker inspect --format '{{json .State.Health}}' log-api | python -m json.tool
```

Health check `ExitCode`s:
 * 1: Monasca API error

[1]: https://docs.openstack.org/monasca-log-api/latest/
[2]: https://developer.openstack.org/api-ref/monitoring-log-api/
[3]: https://githubm/openstack/monasca-log-api
[4]: https://github.com/monasca/monasca-docker/tree/master/kafka
[5]: https://github.com/monasca/monasca-docker/blob/master/monasca-log-api/
