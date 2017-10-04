monasca-alarms Dockerfile
============================

This image contains a container that can be used to create Monasca
Notifications and Alarm Definitions.

Tags
----

The images in this repository follow a few tagging conventions:

 * `latest`: refers to the latest definitions container

Usage
-----

To run, the python creation script needs to connect to a working Monasca API.

In environments resembling the [official Kubernetes environment][1] the image
does not require additional configuration parameters, and can be run like so:

```bash
docker run -it monasca/alarms:latest
```

Configuration
-------------

| Variable                    | Default                      | Description                      |
|-----------------------------|------------------------------|----------------------------------|
| `MONASCA_WAIT_FOR_API`      | `true`                       | Ensure Monasca API is available  |
| `KEYSTONE_DEFAULTS_ENABLED` | `true`                       | Sets all OS defaults                |
| `OS_PASSWORD`               | `password`                   | Password for Keystone User       |
| `OS_PROJECT_DOMAIN_NAME`    | `Default`                    | User Project Domain Name         |
| `OS_AUTH_URL`               | `http://keystone:35357/v3/`  | Keystone URL                     |
| `OS_PROJECT_NAME`           | `mini-mon`                   | User Project Name                |
| `OS_USERNAME`               | `mini-mon`                   | Keystone User Name               |
| `OS_USER_DOMAIN_NAME`       | `Default`                    | Keystone User Domain Name        |

The yaml file describing the Notifications and Alarm Definitions is available
[in the repository][2].

[1]: https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/monasca-alarms/definitions.yml
