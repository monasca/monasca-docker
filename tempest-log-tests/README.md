tempest-log-tests Dockerfile
============================

This image contains a container that can be used to run the Tempest Monasca
Tests.

Tags
----

The images in this repository follow a few tagging conventions:

 * `latest`: refers to the latest tempest-log-tests container

Usage
-----

To run, this container needs to connect to a working Keystone and Monasca API.
It can be run using following command:

```bash
docker run monasca/tempest-log-tests
```

Configuration
-------------

| Variable                  | Default                 | Description                                        |
|-------------------------- |-------------------------|----------------------------------------------------|
| `MONASCA_WAIT_FOR_LOG_API`    |                     | If true, ensure Monasca API is available           |
| `MONASCA_LOG_API_WAIT_RETRIES`| `24`                | Retries for Monasca API available checks           |
| `MONASCA_LOG_API_WAIT_DELAY`  | `5`                 | Sleep time between Monasca API retries             |
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
