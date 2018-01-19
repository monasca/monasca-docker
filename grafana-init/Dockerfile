from alpine:3.5

env LOG_LEVEL=INFO \
  GRAFANA_URL=http://grafana:3000 \
  GRAFANA_ADMIN_USERNAME=admin \
  GRAFANA_ADMIN_PASSWORD=password \
  DATASOURCE_TYPE=monasca \
  DATASOURCE_URL=http://monasca:8070/ \
  DATASOURCE_ACCESS_MODE=proxy \
  DASHBOARDS_DIR=/dashboards.d

run apk add --no-cache python py2-requests
copy grafana.py /grafana.py
copy dashboards.d/ /dashboards.d/
cmd ["python", "/grafana.py"]
