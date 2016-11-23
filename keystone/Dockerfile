from ubuntu:16.04

run apt-get update && \
    apt-get install -y \
        curl python-openstackclient keystone supervisor \
        uwsgi uwsgi-plugin-python mysql-client-5.7

expose 5000 35357

copy supervisord.conf /etc/supervisor/conf.d/supervisord.conf
copy keystone-bootstrap.sh /keystone-bootstrap.sh
copy preload.py /preload.py

cmd /usr/bin/supervisord

healthcheck --interval=10s --timeout=5s \
  CMD curl -f http://localhost:5000/v3 2> /dev/null || exit 1; \
  curl -f http://localhost:35357/v3 2> /dev/null || exit 1;
