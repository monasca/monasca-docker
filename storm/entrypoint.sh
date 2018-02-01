#!/bin/ash
# shellcheck shell=dash

if [ -n "$DEBUG" ]; then
  set -x
fi

CONFIG_TEMPLATES="/templates"
CONFIG_DEST="/storm/conf"
LOG_TEMPLATES="/logging"
LOG_DEST="/storm/log4j2"

ZOOKEEPER_WAIT=${ZOOKEEPER_WAIT:-"true"}
ZOOKEEPER_WAIT_TIMEOUT=${ZOOKEEPER_WAIT_TIMEOUT:-"3"}
ZOOKEEPER_WAIT_DELAY=${ZOOKEEPER_WAIT_DELAY:-"10"}
ZOOKEEPER_WAIT_RETRIES=${ZOOKEEPER_WAIT_RETRIES:-"20"}

SUPERVISOR_STACK_SIZE=${SUPERVISOR_STACK_SIZE:-"1024k"}
WORKER_STACK_SIZE=${WORKER_STACK_SIZE:-"1024k"}
NIMBUS_STACK_SIZE=${NIMBUS_STACK_SIZE:-"1024k"}
UI_STACK_SIZE=${UI_STACK_SIZE:-"1024k"}

if [ -n "$ZOOKEEPER_SERVERS" ]; then
  if [ -z "$STORM_ZOOKEEPER_SERVERS" ]; then
    export STORM_ZOOKEEPER_SERVERS="$ZOOKEEPER_SERVERS"
  fi

  if [ -z "$TRANSACTIONAL_ZOOKEEPER_SERVERS" ]; then
    export TRANSACTIONAL_ZOOKEEPER_SERVERS="$ZOOKEEPER_SERVERS"
  fi
fi

if [ -n "$ZOOKEEPER_PORT" ]; then
  if [ -z "$STORM_ZOOKEEPER_PORT" ]; then
    export STORM_ZOOKEEPER_PORT="$ZOOKEEPER_PORT"
  fi

  if [ -z "$TRANSACTIONAL_ZOOKEEPER_PORT" ]; then
    export TRANSACTIONAL_ZOOKEEPER_PORT="$ZOOKEEPER_PORT"
  fi
fi

first_zk=$(echo "$STORM_ZOOKEEPER_SERVERS" | cut -d, -f1)

# wait for zookeeper to become available
if [ "$ZOOKEEPER_WAIT" = "true" ]; then
  success="false"
  for i in $(seq "$ZOOKEEPER_WAIT_RETRIES"); do
    if ok=$(echo ruok | nc "$first_zk" "$STORM_ZOOKEEPER_PORT" -w "$ZOOKEEPER_WAIT_TIMEOUT") && [ "$ok" = "imok" ]; then
      success="true"
      break
    else
      echo "Connect attempt $i of $ZOOKEEPER_WAIT_RETRIES failed, retrying..."
      sleep "$ZOOKEEPER_WAIT_DELAY"
    fi
  done

  if [ "$success" != "true" ]; then
    echo "Could not connect to $first_zk after $i attempts, exiting..."
    sleep 1
    exit 1
  fi
fi

if [ -z "$STORM_LOCAL_HOSTNAME" ]; then
  # see also: http://stackoverflow.com/a/21336679
  ip=$(ip route get 8.8.8.8 | awk 'NR==1 {print $NF}')
  echo "Using autodetected IP as advertised hostname: $ip"
  export STORM_LOCAL_HOSTNAME=$ip
fi

if [ -z "$SUPERVISOR_CHILDOPTS" ]; then
  SUPERVISOR_CHILDOPTS="-XX:MaxRAM=$(python /memory.py "$SUPERVISOR_MAX_MB") -XX:+UseSerialGC -Xss$SUPERVISOR_STACK_SIZE"
  export SUPERVISOR_CHILDOPTS
fi

if [ -z "$WORKER_CHILDOPTS" ]; then
  WORKER_CHILDOPTS="-XX:MaxRAM=$(python /memory.py "$WORKER_MAX_MB") -Xss$WORKER_STACK_SIZE"
  WORKER_CHILDOPTS="$WORKER_CHILDOPTS -XX:+UseConcMarkSweepGC"
  if [ "$WORKER_REMOTE_JMX" = "true" ]; then
    WORKER_CHILDOPTS="$WORKER_CHILDOPTS -Dcom.sun.management.jmxremote"
  fi

  export WORKER_CHILDOPTS
fi

if [ -z "$NIMBUS_CHILDOPTS" ]; then
  NIMBUS_CHILDOPTS="-XX:MaxRAM=$(python /memory.py "$NIMBUS_MAX_MB") -XX:+UseSerialGC -Xss$NIMBUS_STACK_SIZE"
  export NIMBUS_CHILDOPTS
fi

if [ -z "$UI_CHILDOPTS" ]; then
  UI_CHILDOPTS="-XX:MaxRAM=$(python /memory.py "$UI_MAX_MB") -XX:+UseSerialGC -Xss$UI_STACK_SIZE"
  export UI_CHILDOPTS
fi

template_dir() {
  src_dir=$1
  dest_dir=$2

  for f in "$src_dir"/*; do
     # Skip directories, links, etc
    if [ ! -f "$f" ]; then     
      continue
    fi

    name=$(basename "$f")
    dest=$(basename "$f" .j2)
    if [ "$dest" = "$name" ]; then
      # file does not end in .j2
      cp "$f" "$dest_dir/$dest"
    else
      # file ends in .j2, apply template
      python /template.py "$f" "$dest_dir/$dest"
    fi
  done
}

template_dir "$CONFIG_TEMPLATES" "$CONFIG_DEST"
template_dir "$LOG_TEMPLATES" "$LOG_DEST"

if [ "$WORKER_LOGS_TO_STDOUT" = "true" ]; then
  for PORT in $(echo "$SUPERVISOR_SLOTS_PORTS" | sed -e "s/,/ /"); do
    LOGDIR="/storm/logs/workers-artifacts/thresh/$PORT"
    mkdir -p "$LOGDIR"
    WORKER_LOG="$LOGDIR/worker.log"
    RECREATE="true"
    if [ -e "$WORKER_LOG" ]; then
      if [ -L "$WORKER_LOG" ]; then
        RECREATE="false"
      else
        rm -f "$WORKER_LOG"
      fi
    fi
    if [ $RECREATE = "true" ]; then
      ln -s /proc/1/fd/1 "$WORKER_LOG"
    fi
  done
fi

exec "$@"
