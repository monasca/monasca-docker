Keystone
========

This is a keystone image that supports a basic, **ephemeral** keystone
deployment suitable for testing purposes. The backing database is not intended
to be persisted, and a set of user-specified users and projects can be provided
to be inserted into the database at each startup.

By default, SQLite will be used as the backend storage as per the configuration
in the Ubuntu package. For best results, MySQL is recommended - see below for
instructions to configure the image for this.

 * [Repository](https://github.com/hpcloud-mon/monasca-docker/blob/master/keystone/)
 * [Dockerfile](https://github.com/hpcloud-mon/monasca-docker/blob/master/keystone/Dockerfile)
 * [Kubernetes example](https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/keystone/)

Configuration
-------------
A number of environment variables can be provided:

 * `PRELOAD_YAML_PATH`: the path from which a `preload.yml` should be loaded.
   Default: `/preload.yml`
 * `KEYSTONE_USERNAME`: the keystone boostrap username. Default: `admin`
 * `KEYSTONE_PASSWORD`: the keystone bootstrap password. Default: `s3cr3t`
 * `KEYSTONE_PROJECT`: the keystone bootstrap project name. Default: `admin`
 * `KEYSTONE_ROLE`: the keystone bootstrap role. Default: `admin`
 * `KEYSTONE_SERVICE`: the keystone bootstrap service. Default: `keystone`
 * `KEYSTONE_REGION`: the keystone bootstrap region. Default: `RegionOne`
 * `KEYSTONE_HOST`: the host for the default keystone endpoints. If not
   specified, endpoint-specific variables for admin, public, and internal URLs
   are used (see below).
 * `KEYSTONE_ADMIN_URL`: the keystone admin URL. Default:
   `http://localhost:35357`
 * `KEYSTONE_PUBLIC_URL`: the keystone public URL. Default:
   `http://localhost:5000`
 * `KEYSTONE_INTERNAL_URL`: the keystone internal URL. Default:
   `http://localhost:5000`
 * `KEYSTONE_DATABASE_BACKEND`: if `mysql`, connect to a MySQL database;
   otherwise, use default SQLite.
 * `KEYSTONE_MYSQL_HOST`: the MySQL hostname. Default: `keystone-mysql`
 * `KEYSTONE_MYSQL_TCP_PORT`: the MySQL port. Default: `3306`
 * `KEYSTONE_MYSQL_USER`: the MySQL username. Default: `keystone`
 * `KEYSTONE_MYSQL_PASSWORD`: the MySQL password. Default: `keystone`
 * `KEYSTONE_MYSQL_DATABASE`: the MySQL dastasbase name. Default: `keystone`

Minimally, for testing purposes where SQLite is acceptable, no environment
variables are needed. For use in a Kubernetes environment with MySQL storage,
`KEYSTONE_HOST` and `KEYSTONE_DATABASE_BACKEND` are needed, as well as any
authentication variables. See [the k8s example](https://github.com/hpcloud-mon/monasca-docker/tree/master/k8s/keystone)
for more details.

Minimal MySQL Setup
-------------------
To quickly deploy on plain docker, run:

    docker run --name keystone-mysql \
         -e MYSQL_USER=keystone \
         -e MYSQL_PASSWORD=keystone \
         -e MYSQL_DATABASE=keystone \
         -e MYSQL_RANDOM_ROOT_PASSWORD=true \
         -it mysql

    docker run --name keystone \
         --link keystone-mysql \
         -e KEYSTONE_DATABASE_BACKEND=mysql \
         -it timothyb89/keystone:0.0.5 bash

See [the k8s example](https://github.com/hpcloud-mon/monasca-docker/tree/master/k8s/keystone)
for an example with Kubernetes.

Horizontal scaling is supported, but note that the initial bootstrap needs to
be completed first. This will occur automatically on the first run, after which
more instances can be started and stopped as desired. Note that SQLite storage
**should not be used** when loadbalancing multiple Keystone containers, and will
yield bizarre results when trying to authenticate. Use MySQL instead!

Preloading
----------
A `/preload.yml` can be provided to initialize keystone users and projects at
startup.

An appropriate preload file for Monasca looks like this (equivalent to the
DevStack configuration with slight adaptations for Kubernetes usage):

```yaml
users:
  - username: mini-mon
    password: password
    project: mini-mon
    role: monasca-user

  - username: monasca-agent
    password: password
    project: mini-mon
    role: monasca-agent

  - username: mini-mon
    password: password
    project: mini-mon
    role: admin

  - username: admin
    password: secretadmin
    project: admin
    role: monasca-user

  - username: demo
    password: secretadmin
    project: demo
    role: monasca-user

  - username: monasca-read-only-user
    password: password
    project: mini-mon
    role: monasca-read-only-user

endpoints:
  - name: monasca
    description: Monasca monitoring service
    type: monitoring
    region: RegionOne
    url: http://monasca:8070/v2.0
    interfaces: ['public', 'internal', 'admin']
```

This file will be read on first start by the
[preload script](https://github.com/hpcloud-mon/monasca-docker/blob/master/keystone/preload.py)
and will populate Keystone with the configured users, projects, and endpoints.
