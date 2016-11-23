from alpine:latest

arg MONASCA_PERF_REPO=https://github.com/hpcloud-mon/monasca-perf
arg MONASCA_PERF_REF=master

env KEYSTONE_USERNAME=monasca-agent \
    KEYSTONE_PASSWORD=password \
    KEYSTONE_PROJECT=mini-mon \
    KEYSTONE_URL=http://keystone:5000 \
    MONASCA_URL=http://monasca:8070/

run apk update && \
    apk add python py-yaml py-setuptools git && \
    apk add --virtual build-dep python-dev py-pip build-base linux-headers && \
    pip install python-monascaclient && \
    apk del build-dep

run git clone $MONASCA_PERF_REPO monasca-perf && \
    cd monasca-perf && \
    git reset --hard $MONASCA_PERF_REF

run apk del git
add start.sh /start.sh
workdir monasca-perf/scale_perf
entrypoint ["/start.sh"]
cmd ["python", "agent_simulator.py"]
