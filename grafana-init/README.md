grafana-init Dockerfile
=======================

This image runs a script to initialize a Grafana instance with a set of default
resources, like a datasource and JSON dashboards. For more information on the
Monasca project, see [the wiki][1].

Sources: [grafana-init][2] &middot; [Dockerfile][3] &middot; [monasca-docker][4]

Tags
----

Images in this repository are tagged as follows:

 * `master`: refers to the latest stable point release

Usage
-----

This image requires a running Grafana instance. The [`monasca/grafana`][5] image
is recommended for use with Monasca, but any recent Grafana server should work
(albeit with some minor modifications).

To use with defaults, run:

    docker run --link grafana monasca/grafana-init:latest

The image will connect to a Grafana server at the default address
(`http://grafana:3000/`), create a Monasca datasource, and import several
default dashboards.

Note that this script will not run successfully on a Grafana instance that has
already been initialized.

Configuration
-------------

| Variable           | Default                | Description                     |
|--------------------|------------------------|---------------------------------|
| `LOG_LEVEL`        | `INFO`                 | Logging level, e.g. `DEBUG`     |
| `GRAFANA_URL`      | `http://grafana:3000`  | Location of Grafana server      |
| `DATASOURCE_TYPE`  | `monasca`              | Agent Keystone user domain      |
| `GRAFANA_ADMIN_USERNAME`  | `admin`         | Agent Keystone admin username   |
| `GRAFANA_ADMIN_PASSWORD`  | `password`      | Agent Keystone admin username   |
| `DATASOURCE_URL`   | `http://monasca:8070/` | Agent Keystone project name     |
| `DATASOURCE_ACCESS_MODE` | `proxy`          | Grafana access mode string      |
| `DATASOURCE_AUTH`  | `Keystone`             | Grafana authentication option (`Keystone`, `Horizon`, `Token`) |
| `DATASOURCE_AUTH_TOKEN` | ``                | Keystone token for authentication (for use when `DATASOURCE_AUTH` is set to `Token`) |
| `DASHBOARDS_DIR`   | `/dashboards.d`        | Directory to scan for .json dashboards |

Note that the only datasource type supported at the moment is `monasca`. Other
datasources should be simple to implement as needed by adding logic to
`create_datasource_payload()` in [`grafana.py`][6].

### Grafana users

`GRAFANA_ADMIN_USERNAME` and `GRAFANA_ADMIN_PASSWORD`

Grafan admin user is need for uploading dashboards.


### Custom Dashboards

This image comes with a default set of Monasca-specific dashboards, but these
can be overridden. To do so, mount a directory containing `.json` files to
`/dashboards.d` (path configurable via `DASHBOARDS_DIR`).

The directory will be scanned and each `.json` file will be imported. Files are
sorted before importing, so filenames can be prefixed, e.g. `01-first.json`,
`99-last.json`, to help ensure proper ordering in the Grafana UI,


[1]: https://wiki.openstack.org/wiki/Monasca
[2]: https://github.com/monasca/monasca-docker/blob/master/grafana-init/
[3]: https://github.com/monasca/monasca-docker/blob/master/grafana-init/Dockerfile
[4]: https://github.com/monasca/monasca-docker/
[5]: https://hub.docker.com/r/monasca/grafana/
[6]: https://github.com/monasca/monasca-docker/blob/master/grafana-init/grafana.py
