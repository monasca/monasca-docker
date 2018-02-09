monasca/grafana Dockerfile
==========================

This image contains Grafana built with Keystone support and the Monasca data
source. For more information on the Monasca project, see [the wiki][1].

Sources: [monasca/grafana][2] &middot; [monasca-docker][3] &middot; [Dockerfile][4]

Tags
----

The images in this repository follow a few tagging conventions:

 * `latest`: refers to the latest snapshot build of the [source repository][2]
 * `4.1.0-pre1-1.0.0`: a.k.a. `[grafana version]-[image version]`. In this case
   the image revision `1.0.0` has been built from a snapshot of grafana
   `4.1.0-pre1`

Usage
-----

Grafana does not require any configuration to run normally:

    docker run -p 3000:3000 -it monasca/grafana:latest

To make use of the Monasca datasource in Monasca's [docker-compose][5]
environment, log in using a valid keystone user and password (by default,
`mini-mon` and `password`). Create a new data source with the following
properties:

 * Type: Monasca
 * Url: http://monasca:8070/
 * Access: proxy
 * Token: leave empty
 * Keystone auth: enabled / checked

Note that in the [Kubernetes environment][6], the URL should instead be
`http://monasca-api:8070/`.

The dashboard for monasca-ui, which is opened by clicking on "Graph Metric"
of the 'Alarm' tab, is available. You can use this dashboard outside of monasca-ui
with the following link.
`http://your-grafana-url:3000/dashboard/script/drilldown.js`
Specify the metric name with the key "metric" and dimensions as additional
parameters if necessary as below.
`http://your-grafana-url:3000/dashboard/script/drilldown.js?metric=sample&dim1=val1`

Configuration
-------------

|         Variable         |     Default     |         Description         |
|--------------------------|-----------------|-----------------------------|
| `GRAFANA_ADMIN_USER`     | `grafana-admin` | Grafana admin user name     |
| `GRAFANA_ADMIN_PASSWORD` | `admin`         | Grafana admin user password |

Grafana can be configured using [environment variables][7], though a
configuration file can also be mounted into the image at
`/etc/grafana/grafana.ini`. Plugins should be placed in
`/var/lib/grafana/plugins`.

[1]: https://wiki.openstack.org/wiki/Monasca
[2]: https://github.com/monasca/grafana
[3]: https://github.com/hpcloud-mon/monasca-docker/
[4]: https://github.com/hpcloud-mon/monasca-docker/blob/master/grafana/Dockerfile
[5]: https://github.com/hpcloud-mon/monasca-docker/blob/master/README.md
[6]: https://github.com/hpcloud-mon/monasca-docker/tree/master/k8s
[7]: http://docs.grafana.org/installation/configuration/#using-environment-variables
