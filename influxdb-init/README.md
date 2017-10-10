# Influx Init

# Variables
INFLUXDB_DEFAULT_RETENTION - determines how long the data should be stored before it is dropped (default for all series created on the database) https://docs.influxdata.com/influxdb/v1.1/query_language/database_management/#retention-policy-management
Acceptable values are https://docs.influxdata.com/influxdb/v1.1/query_language/spec/#durations and 'INF' for infinite (Default: INF)

INFLUXDB_SHARD_DURATION - determines the size of data shards. An entire shard is dropped once all of the data it contains is out of the retention period.
Default values are explained in https://docs.influxdata.com/influxdb/v1.1/query_language/database_management/#retention-policy-management and acceptable values in https://docs.influxdata.com/influxdb/v1.1/query_language/spec/#durations
