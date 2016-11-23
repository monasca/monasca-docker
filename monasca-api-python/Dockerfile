FROM python:2.7

ENV MONASCA_API_REPO=https://github.com/openstack/monasca-api.git
ENV MONASCA_API_BRANCH=master

RUN mkdir /source
WORKDIR /source
RUN git clone $MONASCA_API_REPO -b $MONASCA_API_BRANCH

WORKDIR monasca-api
RUN pip install gunicorn influxdb; pip install -r requirements.txt; python setup.py install

COPY api-* /etc/monasca/

ENTRYPOINT ["gunicorn", "--capture-output", "-n", "monasca-api", "-k", "eventlet", "--worker-connections=2000", "--backlog=1000", "--paste", "/etc/monasca/api-config.ini", "-w", "9"]
