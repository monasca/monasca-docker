#!/bin/bash

GC_LOG_ENABLED=${GC_LOG_ENABLED:-"False"}
if [ "$GC_LOG_ENABLED" != "true" ]; then
  # This turns off the GC logging in /kafka/bin/kafka-server-start.sh
  # It is a hack, but I could not find another way to do it
  sed "-i.sv" -e "s/-loggc//" /kafka/bin/kafka-server-start.sh
fi

if [ -z "$KAFKA_HEAP_OPTS" ]; then
    max_heap=$(python /heap.py $KAFKA_MAX_HEAP_MB)
    KAFKA_HEAP_OPTS="-Xmx${max_heap} -Xms${max_heap}"
    export KAFKA_HEAP_OPTS
fi

parallel ::: /start.sh /create_topics.py
