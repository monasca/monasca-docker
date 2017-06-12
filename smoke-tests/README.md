smoke-tests Dockerfile
=====================

This image runs smoke tests against a running instance of Monasca. It checks
the health and functionality of the install. It accomplishes this by running
through a series of small tests that ensure each component of Monasca is healthy.

These include:
* Measurements are flowing through the system
* Creation of an alarm-definition, notification-method and metric
* Triggering of an Alarm and receipt of a webhook notification
* Cleanup of Alarms, Alarm Definition and Notification 

Sources: [smoke-tests][1] &middot; [Dockerfile][2] &middot; [monasca-docker][3]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.0.0`
 * `1.0.0`, `1.0`, `1`: standard semver tags

Usage
-----

This image requires a running instance of Monasca with access to Keystone
and the Monasca API.

The job is intended to be run only once like so, and requires no persistent
storage:

    docker run --rm=true monasca/smoke-tests:latest

If needed, connection parameters can be provided via environment variables as
described below. 

Configuration
-------------

| Variable                 | Default                      | Description                      |
|--------------------------|------------------------------|----------------------------------|
| `OS_PASSWORD`            | `password`                   | Password for Keystone User       |
| `OS_DOMAIN_NAME`         | `Default`                    | User Project Domain Name         |
| `OS_AUTH_URL`            | `http://keystone:35357/v3/`  | Keystone URL                     |
| `OS_TENANT_NAME`         | `mini-mon`                   | User Project Name                |
| `OS_USERNAME`            | `mini-mon`                   | Keystone User Name               |
| `MONASCA_URL`            | `http://monasca-api:8070`    | Monasca API URL                  |

[1]: https://github.com/hpcloud-mon/monasca-docker/blob/master/smoke-tests/
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/smoke-tests/Dockerfile
[3]: https://github.com/hpcloud-mon/monasca-docker/
