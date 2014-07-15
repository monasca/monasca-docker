# Start up kafka, make topics and the put kafka back into the foreground
# This could be done in a smarter way in particular the topic creation but this works and was quick to implement

set -m
/opt/kafka/bin/kafka-server-start.sh /etc/kafka/server.properties &

`/opt/kafka/bin/kafka-list-topic.sh --zookeeper zookeeper:2181 | grep metrics`
if [ $? -ne 0 ]; then
  /opt/kafka/bin/kafka-create-topic.sh --zookeeper zookeeper:2181 --replica 1 --partition 4 --topic metrics
fi

`/opt/kafka/bin/kafka-list-topic.sh --zookeeper zookeeper:2181 | grep events`
if [ $? -ne 0 ]; then
  /opt/kafka/bin/kafka-create-topic.sh --zookeeper zookeeper:2181 --replica 1 --partition 4 --topic events
fi

`/opt/kafka/bin/kafka-list-topic.sh --zookeeper zookeeper:2181 | grep alarm-state-transitions`
if [ $? -ne 0 ]; then
  /opt/kafka/bin/kafka-create-topic.sh --zookeeper zookeeper:2181 --replica 1 --partition 4 --topic alarm-state-transitions
fi

`/opt/kafka/bin/kafka-list-topic.sh --zookeeper zookeeper:2181 | grep alarm-notifications`
if [ $? -ne 0 ]; then
  /opt/kafka/bin/kafka-create-topic.sh --zookeeper zookeeper:2181 --replica 1 --partition 4 --topic alarm-notifications
fi

fg
