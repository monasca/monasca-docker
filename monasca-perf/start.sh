#!/bin/sh

set -e

mkdir -p /etc/monasca/agent/
cat > /etc/monasca/agent/agent.yaml <<EOF
Api:
  username: $KEYSTONE_USERNAME
  password: $KEYSTONE_PASSWORD
  keystone_url: $KEYSTONE_URL
  project_name: $KEYSTONE_PROJECT
  url: $MONASCA_URL
EOF

exec "$@"
