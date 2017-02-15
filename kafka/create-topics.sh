#!/bin/bash

# See also:
# https://github.com/wurstmeister/kafka-docker/blob/master/create-topics.sh
# https://github.com/wurstmeister/kafka-docker/blob/master/LICENSE

if [[ -z "$START_TIMEOUT" ]]; then
    START_TIMEOUT=600
fi

start_timeout_exceeded=false
count=0
step=10
while netstat -lnt | awk '$4 ~ /:'$KAFKA_LISTEN_PORT'$/ {exit 1}'; do
    echo "waiting for kafka to be ready"
    sleep $step;
    count=$(expr $count + $step)
    if [ $count -gt $START_TIMEOUT ]; then
        start_timeout_exceeded=true
        break
    fi
done

if $start_timeout_exceeded; then
    echo "Not able to auto-create topic (waited for $START_TIMEOUT sec)"
    exit 1
fi

if [[ -n $KAFKA_CREATE_TOPICS ]]; then
    IFS=','; for topicToCreate in $KAFKA_CREATE_TOPICS; do
        echo "creating topics: $topicToCreate"
        IFS=':' read -a topicConfig <<< "$topicToCreate"
        JMX_PORT='' /kafka/bin/kafka-topics.sh \
            --create \
            --zookeeper $ZOOKEEPER_CONNECTION_STRING \
            --replication-factor ${topicConfig[2]} \
            --partition ${topicConfig[1]} \
            --topic "${topicConfig[0]}"
    done
fi
