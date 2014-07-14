set -m
/opt/kafka/bin/kafka-server-start.sh /etc/kafka/server.properties &
/opt/kafka/bin/kafka-create-topic.sh --zookeeper zookeeper:2181 --replica 1 --partition 4 --topic metrics
/opt/kafka/bin/kafka-create-topic.sh --zookeeper zookeeper:2181 --replica 1 --partition 4 --topic events
/opt/kafka/bin/kafka-create-topic.sh --zookeeper zookeeper:2181 --replica 1 --partition 4 --topic alarm-state-transitions
/opt/kafka/bin/kafka-create-topic.sh --zookeeper zookeeper:2181 --replica 1 --partition 4 --topic alarm-notifications
fg
