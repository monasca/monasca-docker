from ubuntu:16.04

env SIGIL_VERSION 0.4.0
env SIGIL_SHA256 c503bc15fba88d08fe7ba350fc02e61c4757d13f349f56cf5b7977f8139d5843
env SIGIL_URL https://github.com/gliderlabs/sigil/releases/download/v${SIGIL_VERSION}/sigil_${SIGIL_VERSION}_Linux_x86_64.tgz

run apt-get update && \
    apt-get install -y curl python-openstackclient keystone supervisor uwsgi uwsgi-plugin-python && \
    curl -sSLO $SIGIL_URL && \
    echo "${SIGIL_SHA256} sigil_${SIGIL_VERSION}_Linux_x86_64.tgz" | sha256sum -c - && \
    tar -xzf sigil_${SIGIL_VERSION}_Linux_x86_64.tgz -C /usr/local/bin && \
    rm sigil_${SIGIL_VERSION}_Linux_x86_64.tgz

expose 5000 35357

copy supervisord.conf /etc/supervisor/conf.d/supervisord.conf
copy keystone-bootstrap.sh /keystone-bootstrap.sh

#cmd /run.sh
cmd /usr/bin/supervisord

healthcheck --interval=10s --timeout=5s \
  CMD curl -f http://localhost:5000/v3 2> /dev/null || exit 1; \
  curl -f http://localhost:35357/v3 2> /dev/null || exit 1;
