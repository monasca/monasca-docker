FROM ncsmm/spark:v1

RUN set -x && \
    apk add --no-cache --virtual build-dep \
     python-dev git make g++ linux-headers py2-pip
RUN set -x && \
    mkdir -p /var/log/monasca/transform && \
    mkdir -p /opt/monasca/transform/lib && \
    mkdir -p /var/run/monasca/transform


RUN set -x && \
    git clone https://github.com/openstack/monasca-transform.git /opt/monasca-transform
# the following four lines are to get Flint's pod specs into place
RUN set -x && \
    cd /opt/monasca-transform && \
    git fetch https://git.openstack.org/openstack/monasca-transform refs/changes/08/426008/8 && \
    git checkout FETCH_HEAD
RUN set -x && \
    git config --global user.name "Marvin" && \
    git config --global user.email "david.c.kennedy@hpe.com" && \
    cd /opt/monasca-transform && \
    git rebase master && \
    git branch docker_branch
RUN set -x && \
    cd /opt/monasca-transform && \
    git fetch https://git.openstack.org/openstack/monasca-transform refs/changes/93/427193/4 && \
    git checkout FETCH_HEAD
RUN set -x && \
    cd /opt/monasca-transform && \
    git rebase docker_branch
RUN set -x && \
    /opt/monasca-transform/scripts/create_zip.sh && \
    cp -f /opt/monasca-transform/scripts/monasca-transform.zip /opt/monasca/transform/lib/. && \
    touch /var/log/monasca/transform/monasca-transform.log && \
    pip install -e /opt/monasca-transform

RUN set -x && \
    apk del git py2-pip

COPY driver.py /opt/monasca/transform/lib/.
COPY service_runner.py /opt/monasca/transform/lib/.

RUN set -x && \
    ln -s /etc/config/monasca-transform.conf /etc/monasca-transform.conf && \
    ln -sf /opt/spark/current/bin/spark-submit /usr/bin/spark-submit && \
    ln -sf /opt/spark/current/bin/spark-class /usr/bin/spark-class && \
    ln -sf /opt/spark/current/bin/spark-shell /usr/bin/spark-shell && \
    ln -sf /opt/spark/current/bin/spark-sql /usr/bin/spark-sql

ENTRYPOINT ["python", "/opt/monasca/transform/lib/service_runner.py"]


