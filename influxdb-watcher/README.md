influxdb-watcher
==========

**influxdb-watcher** is responsible for watching the health of InfluxDB.

Tags
----

Images in this repository are tagged as follows:

* `0.0.2` - standard [SemVer][1]
* `latest`: the latest version recommended to use with other Monasca
  components.


Usage
-----

**influxdb-watcher** requires a running instance of [InfluxDB][2]. It can be launched using
command similar to this ```docker run -d -p 8080:8080 -l influxdb-watcher monasca/influxdb-watcher```.
**influxdb-watcher** will wait for InfluxDB to become accessible before monitoring its state.

Configuration
-------------

This parameter can be specified using environment variables:

| Variable                      | Default          | Description                           |
|-------------------------------|------------------|---------------------------------------|
| `STAY_ALIVE_ON_FAILURE`       | `false`          | If `true`, container stays alive for 2 hours after influxdb watcher exits |


Additional parameters are available. See https://github.com/monasca/monasca-watchers for more details.

[1]: http://semver.org/
[2]: https://github.com/monasca/monasca-docker/tree/master/influxdb

