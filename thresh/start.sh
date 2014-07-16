set -m  # mon-thresh will exit when done so I need the ability to bring another process to the foreground
# Start storm
/opt/storm/apache-storm-0.9.1-incubating/bin/nimbus-control start &
/opt/storm/apache-storm-0.9.1-incubating/bin/supervisor-control start &

# Start the threshold engine
sleep 60  # Takes a moment for storm to be up
/opt/storm/current/bin/storm jar /opt/mon/mon-thresh.jar com.hpcloud.mon.ThresholdingEngine /etc/mon/mon-thresh-config.yml thresh-cluster

fg
