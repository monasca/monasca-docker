monasca-api Dockerfile
======================

This image contains a containerized version of the Monasca API.

There are two implementations of the monasca-api:

 * python (tagged `-python` or empty) - [Dockerfile][1]
 * java (tagged `-java`) - [Dockerfile][2]

Currently the `python` images are recommended. For more information on the
Monasca project, see [the wiki][3].

Source repositories: [monasca-api][4] &middot; [monasca-docker][5]

Tags
----

The images in this repository follow a few tagging conventions:

 * `latest`: refers to the latest stable Python point release, e.g.
   `1.5.0-python`
 * `latest-python`, `latest-java`: as above, but specifically referring to the
   latest stable Python or Java point release, e.g. `1.5.0`
 * `1.5.0`, `1.5`, `1`: standard semver tags, based on git tags in the
   [official repository][4]
 * `1.5.0-python`, `1.5-python`, `1-python`: as above, but specifically
   referring to python-based images
 * `mitaka`, `newton`, etc: named versions following OpenStack release names
   built from the tip of the `stable/RELEASENAME` branches in the repository
 * `mitaka-python`, `newton-python`: as above, but specifically Python-based
   images
 * `master`, `master-DATESTAMP`: unstable builds from the master branch, not
   intended for general use

Note that unless otherwise specified, images will be Python-based. All
Java-based images will be tagged as such, and likely will not support the
configuration options described below.

Usage
-----

To run, the API needs to connect to working instances of Kafka, Influx, and
MySQL. For metrics to be processed, one or more [monasca-persister][6] instances
should be running as well. Alarming and alarm management management additionally
require an instance of storm and [monasca-thresh][7] as well as
[monasca-notification][8].

In environments resembling the [official Kubernetes environment][9] the image
does not require additional configuration parameters, and can be run like so:

```bash
docker run -p 8070:8070 -it monasca/api:latest
```

NOTE: due to recent config file changes, this Docker container only supports API
versions greater than 1.5.0. That is to say, as of this writing, there are no
formal API releases supported by this Dockerfile. As such, the `latest` and
`latest-python` tags will point to the latest `master` image until the next
`monasca-api` release is published.

Configuration
-------------

A number of environment variables can be passed to the container:

| Variable                  | Default       | Description                      |
|---------------------------|---------------|----------------------------------|
| `LOG_LEVEL_ROOT`          | `WARN`        | The level of the root logger     |
| `LOG_LEVEL_CONSOLE`       | `INFO`        | Minimum level for console output |
| `LOG_LEVEL_ACCESS`        | `INFO`        | Minimum level for access output  |
| `MONASCA_CONTAINER_API_PORT` | `8070`        | The API's HTTP port           |
| `KAFKA_URI`               | `kafka:9092`  | The host and port for kafka      |
| `KAFKA_WAIT_FOR_TOPICS`   | `alarm-state-transitions,metrics` | Topics to wait on at startup |
| `KAFKA_WAIT_RETRIES`      | `24`          | # of kafka wait attempts         |
| `KAFKA_WAIT_DELAY`        | `5`           | seconds to wait between attempts |
| `INFLUX_HOST`             | `influxdb`    | The host for influxdb            |
| `INFLUX_PORT`             | `8086`        | The port for influxdb            |
| `INFLUX_USER`             | `mon_api`     | The influx username              |
| `INFLUX_PASSWORD`         | `password`    | The influx password              |
| `INFLUX_DB`               | `mon`         | The influx database name         |
| `MYSQL_HOST`              | `mysql`       | Alarm DB connection string       |
| `MYSQL_USER`              | `monapi`      | MySQL DB username                |
| `MYSQL_PASSWORD`          | `password`    | MySQL DB password                |
| `MYSQL_DB`                | `mon`         | MySQL database name              |
| `MYSQL_WAIT_RETRIES`      | `24`          | # of MySQL connection attempts   |
| `MYSQL_WAIT_DELAY`        | `5`           | seconds to wait between attempts |
| `API_MYSQL_DISABLED`      | unset         | if 'true' do not use a mysql database. Only metric API will work |
| `KEYSTONE_IDENTITY_URI`   | `http://keystone:35357` | Keystone identity address |
| `KEYSTONE_AUTH_URI`       | `http://keystone:5000`  | Keystone auth address     |
| `KEYSTONE_ADMIN_USER`     | `admin`       | Keystone admin account user      |
| `KEYSTONE_ADMIN_PASSWORD` | `secretadmin` | Keystone admin account password  |
| `KEYSTONE_ADMIN_TENANT`   | `admin`       | Keystone admin account tenant    |
| `KEYSTONE_INSECURE`       | `false`       | Allow insecure Keystone connection |
| `KEYSTONE_REGION_NAME`    | undefined     | Keystone admin account region    |
| `GUNICORN_WORKERS`        | `9`           | number of API worker processes   |
| `GUNICORN_WORKER_CLASS`   | `gevent`      | async worker class               |
| `GUNICORN_WORKER_CONNECTIONS` | `2000`    | no. connections for async worker |
| `GUNICORN_BACKLOG`        | `1000`        | gunicorn backlog size            |
| `AUTHORIZED_ROLES`           | `user, domainuser, domainadmin, monasca-user` | Roles for admin Users |
| `AGENT_AUTHORIZED_ROLES`     | `monasca-agent` | Roles for metric write only users |
| `READ_ONLY_AUTHORIZED_ROLES` | `monasca-read-only-user` | Roles for read only users    |
| `DELEGATE_AUTHORIZED_ROLES`  | `admin`       | Roles allow to read/write cross tenant ID |
| `ADD_ACCESS_LOG`  | `true`       | if true, produce an access log on stderr |
| `ACCESS_LOG_FORMAT`  | `%(asctime)s [%(process)d] gunicorn.access [%(levelname)s] %(message)s` | Log format for access log |
| `ACCESS_LOG_FIELDS`  | `%(h)s %(l)s %(u)s %(t)s %(r)s %(s)s %(b)s "%(f)s" "%(a)s" %(L)s` | Access log fields |

If additional values need to be overridden, new config files or jinja2 templates
can be provided by mounting a replacement on top of the original template:

 * `/etc/monasca/api-config.conf.j2`
 * `/etc/monasca/api-config.ini.j2`
 * `/etc/monasca/api-logging.conf.j2`

If jinja2 formatting is not desired, the environment variable `CONFIG_TEMPLATE`
can be set to `false`. Note that the jinja2 template should still be overwritten
(rather than the target file without the `.j2` suffix) as it will be copied at
runtime.

The config file sources are available [in the repository][10]. If necessary, the
generated config files can be viewed at runtime by running:

```bash
docker exec -it some_container_id cat /etc/monasca/api-config.conf
docker exec -it some_container_id cat /etc/monasca/api-config.ini
docker exec -it some_container_id cat /etc/monasca/api-logging.conf
```

Troubleshooting
-------------

Container status can be checked by the following command (example):
```bash
docker ps --filter 'name=monasca' --format '{{.Names}}\t{{.Image}}\t{{.Status}}'
```

Result of health check can be get by the following command:
```bash
docker inspect --format '{{json .State.Health}}' monasca | python -m json.tool
```
Health check `ExitCode`s:
 * 1: Keystone authentication error
 * 2: Monasca API error
 

[1]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-api-python/Dockerfile
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-api-java/Dockerfile
[3]: https://wiki.openstack.org/wiki/Monasca
[4]: https://github.com/openstack/monasca-api/
[5]: https://github.com/hpcloud-mon/monasca-docker/
[6]: https://hub.docker.com/r/monasca/persister/
[7]: https://hub.docker.com/r/monasca/thresh/
[8]: https://hub.docker.com/r/monasca/notification/
[9]: https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/
[10]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-api-python/
