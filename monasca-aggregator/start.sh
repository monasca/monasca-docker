#!/bin/sh

python /template.py /config/config.yaml.j2 config.yaml

# works around a recent Kubernetes issue where subpath mounts are broken
# we need to mount the aggregation specifications configmap into its own
# directory rather than using subpath mounts
specs_input=${AGGREGATION_SPECIFICATIONS:-"/specs/aggregation-specifications.yaml"}
if [ -e "$specs_input" ]; then
  echo "copying $specs_input to /"
  cp "$specs_input" /aggregation-specifications.yaml
fi

/monasca-aggregator
