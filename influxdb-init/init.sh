#!/bin/sh

set -x

INFLUXDB_URL=${INFLUXDB_URL:-"http://influxdb:8086"}
MONASCA_DATABASE=${MONASCA_DATABASE:-"mon"}
API_USERNAME=${API_USERNAME:-"mon_api"}
API_PASSWORD=${API_PASSWORD:-"password "}
PERSISTER_USERNAME=${PERSISTER_USERNAME:-"mon_persister"}
PERSISTER_PASSWORD=${PERSISTER_PASSWORD:-"password "}
INFLUXDB_WATCHER_USERNAME=${INFLUXDB_WATCHER_USERNAME:-"influxdb_watcher"}
INFLUXDB_WATCHER_PASSWORD=${INFLUXDB_WATCHER_PASSWORD:-"password"}
INFLUXDB_DEFAULT_RETENTION=${INFLUXDB_DEFAULT_RETENTION:-"INF"}

attempts=24
delay=5s

echo "Waiting for influx to become available..."
success=1
for i in $(seq 1 $attempts); do
  if http get "${INFLUXDB_URL}/ping"; then
    success=0
    break
  fi

  echo "Failed to ping ${INFLUXDB_URL}, attempt $i of $attempts..."
  sleep $delay
done

if [ $success -ne 0 ]; then
  echo "Could not contact influx, giving up."
  exit 1
fi

post () {
  http --check-status --ignore-stdin post "${INFLUXDB_URL}/query" q=="$1"
  ret=$?

  if [ $ret -ne 0 ]; then
    echo "Database POST failed: $1"
  fi
}

echo "Creating database \"${MONASCA_DATABASE}\"..."
if [ -z "${INFLUXDB_SHARD_DURATION}" ]; then
  post "CREATE DATABASE \"${MONASCA_DATABASE}\" WITH DURATION ${INFLUXDB_DEFAULT_RETENTION} REPLICATION 1 NAME \"default_mon\""
else
  post "CREATE DATABASE \"${MONASCA_DATABASE}\" WITH DURATION ${INFLUXDB_DEFAULT_RETENTION} REPLICATION 1 SHARD DURATION ${INFLUXDB_SHARD_DURATION} NAME \"default_mon\""
fi

echo "Adding ${API_USERNAME} user..."
post "CREATE USER \"${API_USERNAME}\" WITH PASSWORD '${API_PASSWORD}'"
post "GRANT ALL ON \"mon\" to \"${API_USERNAME}\""

echo "Adding ${PERSISTER_USERNAME} user..."
post "CREATE USER \"${PERSISTER_USERNAME}\" WITH PASSWORD '${PERSISTER_PASSWORD}'"
post "GRANT ALL ON \"mon\" to \"${PERSISTER_USERNAME}\""

echo "Adding ${INFLUXDB_WATCHER_USERNAME} user..."
post "CREATE USER \"${INFLUXDB_WATCHER_USERNAME}\" WITH PASSWORD '${INFLUXDB_WATCHER_PASSWORD}'"
post "GRANT ALL ON \"mon\" to \"${INFLUXDB_WATCHER_USERNAME}\""

echo "InfluxDB init finished."
