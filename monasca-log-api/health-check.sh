#!/bin/sh

# Default values for executing it manually on the host
MONASCA_CONTAINER_LOG_API_PORT=${1:-5607}

curl --include --silent --show-error --output - \
    http://localhost:"${MONASCA_CONTAINER_LOG_API_PORT}"/healthcheck 2>&1 | \
    awk '
        BEGIN {status_code="0"; body=""; output=""}
        $1 ~ /^HTTP\// {status_line=$0; status_code=$2}
        $1 ~ /^\{/ {body=$0}
        {output=output $0 "\n"}
        END {
            if(status_code=="200") {
                print status_line;
                print body;
            } else {
                print output;
                exit 2;
            }
        }'

exit $?
