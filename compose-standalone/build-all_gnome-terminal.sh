#!/bin/bash

cd "$(dirname "$0")"
source gnome-terminal_helper.sh

docker-compose ${FILE_LIST} config --quiet || exit 1

FILE_LIST="--file docker-compose.yml --file compose-init.yml"
SERVICE_LIST="$(docker-compose ${FILE_LIST} config --services)"

echo -e "Services:\n${SERVICE_LIST}"

echo
do_compose "pull" "${FILE_LIST}" "$(docker-compose ${FILE_LIST} config --services)"

echo "Press any key when all of images are already pulled..."
read -n1

echo
do_compose "build" "${FILE_LIST}" "$(docker-compose ${FILE_LIST} config --services)"
