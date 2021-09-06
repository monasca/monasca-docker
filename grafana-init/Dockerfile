from alpine:3.13

env LOG_LEVEL=INFO \
  GRAFANA_URL=http://grafana:3000 \
  DATASOURCE_TYPE=monasca \
  DATASOURCE_URL=http://monasca:8070/ \
  DATASOURCE_ACCESS_MODE=proxy \
  DATASOURCE_AUTH=Keystone \
  DASHBOARDS_DIR=/dashboards.d

run apk add --no-cache python3 py3-requests
copy grafana.py /grafana.py
copy dashboards.d/ /dashboards.d/
cmd ["python3", "/grafana.py"]
