#!/bin/bash

cd "$(dirname "$0")"
source gnome-terminal_helper.sh

docker-compose ${FILE_LIST} config --quiet || exit 1

FILE_LIST="--file docker-compose.yml"
SERVICE_LIST="$(docker-compose ${FILE_LIST} config --services)"

echo -e "Services:\n${SERVICE_LIST}"

echo
do_compose "up" "${FILE_LIST}" "$(docker-compose ${FILE_LIST} config --services)"
