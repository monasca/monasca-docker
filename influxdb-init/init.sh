#!/bin/sh

set -x

INFLUXDB_URL=${INFLUXDB_URL:-"http://influxdb:8086"}
MONASCA_DATABASE=${MONASCA_DATABASE:-"mon"}
API_USERNAME=${API_USERNAME:-"mon_api"}
API_PASSWORD=${API_PASSWORD:-"password "}
PERSISTER_USERNAME=${PERSISTER_USERNAME:-"mon_persister"}
PERSISTER_PASSWORD=${PERSISTER_PASSWORD:-"password "}
INFLUXDB_DEFAULT_RETENTION=${INFLUXDB_DEFAULT_RETENTION:-"30d"}
INFLUXDB_SHARD_DURATION=${INFLUXDB_SHARD_DURATION:-"1h"}

attempts=10
delay=5s

echo "Waiting for influx to become available..."
success=1
for i in $(seq 1 $attempts); do
  http get "${INFLUXDB_URL}/ping"
  if [ $? -eq 0 ]; then
    success=0
    break
  else
    echo "Failed to ping ${INFLUXDB_URL}, attempt $i of $attempts..."
    sleep
  fi

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
post "CREATE DATABASE \"${MONASCA_DATABASE}\" WITH RETENTION ${INFLUXDB_DEFAULT_RETENTION} SHARD DURATION ${INFLUXDB_SHARD_DURATION} NAME \"default_mon\""

echo "Adding ${API_USERNAME} user..."
post "CREATE USER \"${API_USERNAME}\" WITH PASSWORD '${API_PASSWORD}'"
post "GRANT ALL ON \"mon\" to \"${API_USERNAME}\""

echo "Adding ${PERSISTER_USERNAME} user..."
post "CREATE USER \"${PERSISTER_USERNAME}\" WITH PASSWORD '${PERSISTER_PASSWORD}'"
post "GRANT ALL ON \"mon\" to \"${PERSISTER_USERNAME}\""

echo "InfluxDB init finished."
