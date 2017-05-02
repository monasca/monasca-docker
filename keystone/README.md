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
 * `KEYSTONE_MYSQL_CONNECT_RETRIES`: number of connection attempts to make
   before proceding with initialization. Default: `24`
 * `KEYSTONE_MYSQL_CONNECT_RETRY_DELAY`: number of seconds to wait after a
   failed connection attempt before retrying. Default: `5`
 * `KUBERNETES_RESOLVE_PUBLIC_ENDPOINTS`: if set to `true` in a Kubernetes
   environment, query the Kubernetes API to automatically resolve the `public`
   and `admin` endpoints for Keystone and `preload.yml` interfaces (see below).
   Services must have a defined `NodePort` or Ingress controller or the
   bootstrapping process will fail!
 * `KEYSTONE_SERVICE_NAME`: the keystone Kubernetes service name, required when
   `KUBERNETES_RESOLVE_PUBLIC_ENDPOINTS` is set. This service must have a
   working NodePort or ingress controller!

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

### Public URLs in Kubernetes

If you are running Keystone and Monasca in a Kubernetes environment, it won't
be accessible outside the Kubernetes cluster even with the endpoints properly
exposed using NodePorts or otherwise. This is caused by Keystone's service
catalog returning URLs (for itself included) that are not accessible outside
the cluster.

As a workaround, this container can query the Kubernetes API when bootstrapping
and preloading to set the `public` and `admin` endpoints based on a configured
Service.

To enable this:
 * Create a Service using a NodePort for Keystone
 * Set `KUBERNETES_RESOLVE_PUBLIC_ENDPOINTS=true` in the pod's environment
 * Set `KEYSTONE_SERVICE_NAME` to the name of the keystone service

When starting the container, check the log output when the container is
bootstrapping. If all goes well, you should see output like so:

```
Creating bootstrap credentials...
2017-04-06 17:49:08.855 58 WARNING keystone.assignment.core [-] Deprecated: Use of the identity driver config to automatically configure the same assignment driver has been deprecated, in the "O" release, the assignment driver will need to be expicitly configured if different than the default (SQL).
2017-04-06 17:49:09.281 58 INFO keystone.cmd.cli [-] Created domain default
2017-04-06 17:49:09.346 58 INFO keystone.cmd.cli [req-3d6a822f-7433-4311-b96d-0c7ef8647178 - - - - -] Created project admin
2017-04-06 17:49:09.375 58 INFO keystone.cmd.cli [req-3d6a822f-7433-4311-b96d-0c7ef8647178 - - - - -] Created user admin
2017-04-06 17:49:09.379 58 INFO keystone.cmd.cli [req-3d6a822f-7433-4311-b96d-0c7ef8647178 - - - - -] Created Role admin
2017-04-06 17:49:09.391 58 INFO keystone.cmd.cli [req-3d6a822f-7433-4311-b96d-0c7ef8647178 - - - - -] Granted admin on admin to user admin.
2017-04-06 17:49:09.398 58 INFO keystone.cmd.cli [req-3d6a822f-7433-4311-b96d-0c7ef8647178 - - - - -] Created Region RegionOne
2017-04-06 17:49:09.442 58 INFO keystone.cmd.cli [req-3d6a822f-7433-4311-b96d-0c7ef8647178 - - - - -] Created admin endpoint http://192.168.99.100:30353
2017-04-06 17:49:09.453 58 INFO keystone.cmd.cli [req-3d6a822f-7433-4311-b96d-0c7ef8647178 - - - - -] Created internal endpoint http://172.17.0.5:5000
2017-04-06 17:49:09.463 58 INFO keystone.cmd.cli [req-3d6a822f-7433-4311-b96d-0c7ef8647178 - - - - -] Created public endpoint http://192.168.99.100:30500
```

The above is from a minikube environment running
[monasca-helm](https://github.com/hpcloud-mon/monasca-helm) with Keystone
NodePorts mapping ports 5000 -> 30500 and 35357 -> 30353. The IP address is
the address of minikube's VirtualBox VM and is accessible from the host.
Running `openstack endpoint list` on the host with appropriate environment
variables set now works and shows accessible public endpoints.

Note that this same functionality can be applied to services in `preload.yml` as
well. First, take an interfaces block:

```
interfaces: ['public', 'internal', 'admin']
```

And expand it out, adding `resolve: true` to endpoints that should be accessible
from outside the cluster:

```
interfaces:
  - name: internal
    url: http://service-name:1234/v2.0
  - name: public
    url: http://service-name:1234/v2.0
    resolve: true
  - name: admin
    url: http://service-name:1234/v2.0
    resolve: true
```

When preloading services with `resolve: true` will be looked up via the k8s API
and the external IP and port will be added to the Keystone catalog rather than
the listed internal DNS names. Otherr components of the URL will be preserved,
only the host and port are replaced.
