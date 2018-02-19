#!/bin/ash
# shellcheck shell=dash

STAY_ALIVE_ON_FAILURE=${STAY_ALIVE_ON_FAILURE:-"false"}

echo "Starting influxdb watcher..."
EXEC="exec"
if [ "$STAY_ALIVE_ON_FAILURE" = "true" ]; then
      EXEC=""
fi
$EXEC /influxdb-watcher
RESULT=$?

# Keep the container alive for debugging or actions like resolving a full disk. This
# sleep will only be reached if STAY_ALIVE_ON_FAILURE is true
sleep 7200
exit $RESULT
