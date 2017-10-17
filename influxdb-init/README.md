# Influx Init

## Variables
INFLUXDB_DEFAULT_RETENTION - determines how long the data should be stored
before it is dropped, see [retention policies][1] for more detail.
Acceptable values are [durations][2] and `INF` for infinite (Default: `INF`)

INFLUXDB_SHARD_DURATION - determines the size of data shards. An entire shard
is dropped once all of the data it contains is out of the retention period.
Default values are explained in [retention policies][1] and acceptable values
are [durations][2]

[1]: https://docs.influxdata.com/influxdb/v1.3/query_language/database_management/#retention-policy-management
[2]: https://docs.influxdata.com/influxdb/v1.3/query_language/spec/#durations
