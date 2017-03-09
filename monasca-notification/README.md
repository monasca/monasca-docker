monasca-notification Dockerfile
===============================

This image has a containerized version of the Monasca Notification Engine. For
more information on the Monasca project, see [the wiki][1].

Sources: [monasca-notification][2] &middot; [monasca-docker][3] &middot; [Dockerfile][4]

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

The notification engine requires configured instances of MySQL, Kafka,
Zookeeper, and the [monasca-api][5]. In environments resembling the official
[docker-compose][3] or [Kubernetes][6] environments, this image requires little
to no configuration and can be minimally run like so:

    docker run monasca/notification:latest

However, without any notification plugins enabled (the default config), the
engine will not be particularly useful. See below for instructions on enabling
and configuring plugins.

Configuration
-------------

| Variable             | Default        | Description                              |
|----------------------|----------------|------------------------------------------|
| `MYSQL_DB_HOST`      | `mysql`        | MySQL hostname                           |
| `MYSQL_DB_PORT`      | `3306`         | MySQL port                               |
| `MYSQL_DB_USERNAME`  | `notification` | MySQL username                           |
| `MYSQL_DB_PASSWORD`  | `password`     | MySQL password                           |
| `MYSQL_DB_DATABASE`  | `mon`          | MySQL database name                      |
| `MYSQL_WAIT_RETRIES` | `24`           | # of tries to verify MySQL availability  |
| `MYSQL_WAIT_DELAY`   | `5`            | # seconds between retry attempts         |
| `KAFKA_URI`          | `kafka:9092`   | If `true`, disable remote root login     |
| `KAFKA_WAIT_FOR_TOPICS` | defaults    | Comma-separated list of topic names to check |
| `KAFKA_WAIT_RETRIES` | `24`           | # of tries to verify Kafka availability  |
| `KAFKA_WAIT_DELAY`   | `5`            | # seconds between retry attempts         |
| `ZOOKEEPER_URL`      | `zookeeper:2181` | Zookeeper URL                          |
| `ALARM_PROCESSORS`   | `2`            | # of alarm processing threads            |
| `NOTIFICATION_PROCESSORS` | `2`       | # of notification processing threads     |
| `RETRY_INTERVAL`     | `30`           | Retry interval in seconds                |
| `RETRY_MAX_ATTEMPTS` | `5`            | Max number of notification retries       |
| `LOG_LEVEL`          | `WARN`         | Python logging level, e.g. `DEBUG`, `INFO`, `WARN` |
| `STATSD_HOST`        | unset          | Monasca StatsD host for internal metrics |
| `STATSD_PORT`        | unset          | Monasca StatsD port for internal metrics |
| `NF_PLUGINS`         | unset          | See below                                |

Notification Plugins
--------------------

A list of notification plugins can be provided by setting `NF_PLUGINS` to a
comma-separated list of plugin names, e.g. `email,webhook,hipchat`.

### Email

Name: `email`

This plugin sends email notifications when an alarm is triggered.

Options:
 * `NF_EMAIL_SERVER`: SMTP server address, required, unset by default
 * `NF_EMAIL_PORT`: SMTP server port, default: `25`
 * `NF_EMAIL_USER`: SMTP username, optional, unset by default
 * `NF_EMAIL_PASSWORD`, SMTP password, required only if `NF_EMAIL_USER` is set
 * `NF_EMAIL_FROM_ADDR`: "from" field for emails sent, e.g.
   `"Name" <name@example.com>`

### Webhook

Name: `webhook`

This plugin calls a webhook when an alarm is triggered. Specific parameters,
like the URL to load, are part of the notification rather than the notification
plugin.

Options:
 * `NF_WEBHOOK_TIMEOUT`: timeout in seconds, default: `5`

### PagerDuty

Name: `pagerduty`

Creates a [PagerDuty event][7] for the given alarm.

Options:
 * `NF_PAGERDUTY_TIMEOUT`: timeout in seconds, default: `5`
 * `NF_PAGERDUTY_URL`: PagerDuty [Event API][7] endpoint, defaults to official
   URL

### HipChat

Name: `hipchat`

Notifies via a HipChat message to some room. Authentication and destination
details are configured with the notification.

Options:
 * `NF_HIPCHAT_TIMEOUT`: timeout in seconds, default: `5`
 * `NF_HIPCHAT_SSL_CERTS`: path to SSL certs, default: system certs
 * `NF_HIPCHAT_INSECURE`: if `true`, don't verify SSL
 * `NF_HIPCHAT_PROXY`: if set, use the given HTTP(S) proxy server to send
   notifications

### Slack

Name: `slack`

Notifies via a Slack message.

Options:
* `NF_SLACK_TIMEOUT`: timeout in seconds, default: `5`
* `NF_SLACK_CERTS`: path to SSL certs, default: system certs
* `NF_SLACK_INSECURE`: if `true`, don't verify SSL
* `NF_SLACK_PROXY`: if set, use the given HTTP(S) proxy server to send
  notifications


[1]: https://wiki.openstack.org/wiki/Monasca
[2]: https://github.com/openstack/monasca-notification/
[3]: https://github.com/hpcloud-mon/monasca-docker/
[4]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-notification/Dockerfile
[5]: https://hub.docker.com/r/monasca/api/
[6]: https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/
[7]: https://v2.developer.pagerduty.com/docs/events-api
