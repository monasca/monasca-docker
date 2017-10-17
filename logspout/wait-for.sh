#!/bin/sh

: "${RETRIES:=5}"
: "${SLEEP_LENGTH:=2}"

wait_for() {
  echo "Waiting for $1 to listen on $2..."

  for i in $(seq $RETRIES)
  do
    nc -z "$1" "$2" && return
    echo "$1 not yet ready (attempt $i of $RETRIES)"
    sleep "$SLEEP_LENGTH"
  done
  echo "$1 failed to become ready, exiting..."
  exit 1
}

for var in "$@"
do
  host=${var%:*}
  port=${var#*:}
  wait_for "$host" "$port"
done
