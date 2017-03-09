#! bin/bash
cat /config/storm.yaml | sed \
  -e "s|{{NIMBUS_ADVERTISED_HOST}}|${NIMBUS_ADVERTISED_HOST}|g" \
> /config/storm.yaml
storm jar /monasca-thresh.jar monasca.thresh.ThresholdingEngine /config/thresh-config.yml thresh-cluster
