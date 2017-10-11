from ubuntu:16.04

run apt-get update && \
    apt-get install -y \
        curl python-openstackclient keystone supervisor \
        uwsgi uwsgi-plugin-python mysql-client-5.7

expose 5000 35357

copy supervisord.conf /etc/supervisor/supervisord.conf
copy start.sh preload.py k8s_get_service.py keystone-bootstrap.sh preload.yml /
copy exit-event-listener.py /usr/local/bin/exit-event-listener

cmd /start.sh

healthcheck --interval=10s --timeout=5s \
  CMD curl -f http://localhost:5000/v3 2> /dev/null || exit 1; \
  curl -f http://localhost:35357/v3 2> /dev/null || exit 1;
