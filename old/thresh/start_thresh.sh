#!/bin/bash

set -m  # mon-thresh will exit when done so I need the ability to bring another process to the foreground
# Start storm
/opt/storm/current/bin/storm nimbus &
/opt/storm/current/bin/storm supervisor &

# Start the threshold engine
sleep 60  # Takes a moment for storm to be up
/opt/storm/current/bin/storm jar /opt/monasca/monasca-thresh.jar monasca.thresh.ThresholdingEngine /etc/monasca/thresh-config.yml thresh-cluster

fg
