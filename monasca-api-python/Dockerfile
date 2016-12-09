FROM python:2.7

ARG API_REPO=https://github.com/openstack/monasca-api.git
ARG API_BRANCH=master

RUN git clone $API_REPO -b $API_BRANCH --depth 1

WORKDIR /monasca-api
RUN pip install gunicorn influxdb; pip install -r requirements.txt; python setup.py install

COPY api-* /etc/monasca/

ENTRYPOINT ["gunicorn", "--capture-output", "-n", "monasca-api", "-k", "eventlet", "--worker-connections=2000", "--backlog=1000", "--paste", "/etc/monasca/api-config.ini", "-w", "9"]
