tempest-tests Dockerfile
============================

This image contains a container that can be used to run the Tempest Monasca
Tests.

Tags
----

The images in this repository follow a few tagging conventions:

 * `latest`: refers to the latest tempest-tests container

Usage
-----

To run, this container needs to connect to a working Keystone and Monasca API.

To run in environments resembling the [official Kubernetes environment][1] see
the [Monasca HELM charts][2].

In order to run in docker-compose add this section to docker-compose.yaml:
```
  tempest-tests:
    image: monasca/tempest-tests:latest
    environment:
        KEYSTONE_SERVER: "keystone"
        STAY_ALIVE_ON_FAILURE: "true"
        MONASCA_WAIT_FOR_API: "true"
```

Then run this:
```bash
docker-compose up -d tempest-tests
```

To run in Kubernetes using Helm, see the monasca/monasca-helm repository. There is a chart for this
container.

Configuration
-------------

| Variable                  | Default                 | Description                                        |
|-------------------------- |-------------------------|----------------------------------------------------|
| `MONASCA_WAIT_FOR_API`    |                         | If true, ensure Monasca API is available           |
| `MONASCA_API_WAIT_RETRIES`| `24`                    | Retries for Monasca API available checks           |
| `MONASCA_API_WAIT_DELAY`  | `5`                     | Sleep time between Monasca API retries             |
| `OS_PASSWORD`             | `password`              | Password for Keystone User                         |
| `OS_PROJECT_DOMAIN_NAME`  | `Default`               | User Project Domain Name                           |
| `OS_PROJECT_NAME`         | `mini-mon`              | User Project Name                                  |
| `OS_USERNAME`             | `mini-mon`              | Keystone User Name                                 |
| `OS_TENANT_NAME`          | `mini-mon`              | Keystone User Tenant(Project) Name                 |
| `OS_DOMAIN_NAME`          | `Default`               | Keystone User Domain Name                          |
| `ALT_USERNAME`            | `mini-mon`              | Alternate User Name                                |
| `ALT_PASSWORD`            | `password`              | Alternate User Password                            |
| `AUTH_USE_SSL`            | `False`                 | Use https for keystone Auth URI                    |
| `KEYSTONE_SERVER`         | `keystone`              | Keystone Server Name                               |
| `KEYSTONE_PORT`           | `35357`                 | Keystone Server Port                               |
| `USE_DYNAMIC_CREDS`       | `True`                  | Whether to use recreate creds for tests            |
| `ADMIN_USERNAME`          | `mini-mon`              | Keystone Admin Domain Name                         |
| `ADMIN_PASSWORD`          | `password`              | Keystone Admin Domain Name                         |
| `ADMIN_DOMAIN_NAME`       | `Default`               | Keystone Admin Domain Name                         |
| `OSTESTR_REGEX`           | `monasca_tempest_tests` | Selects which tests to run                         |
| `STAY_ALIVE_ON_FAILURE`   |                         | If true, container runs 2 hours after tests fail   |


[1]: https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/
[2]: https://github.com/monasca/monasca-helm
