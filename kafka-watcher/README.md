kafka-watcher
==========

**kafka-watcher** is responsible for watching the health of Kafka.

Tags
----

Images in this repository are tagged as follows:

* `0.0.1` - standard [SemVer][1]
* `latest`: the latest version recommended to use with other Monasca
  components.


Usage
-----

**kafka-watcher** requires a running instance of [Kafka][2]. It can be launched using
command similar to this ```docker run -d -p 9092:9092 -l zookeeper monasca/kafka```.
**kafka-watcher** will wait for Kafka to become accessible before monitoring its state.

Configuration
-------------

Several parameters can be specified using environment variables. See
https://github.com/craigbr/monasca-watchers for more details.

[1]: http://semver.org/
[2]: https://github.com/monasca/monasca-docker/tree/master/kafka
