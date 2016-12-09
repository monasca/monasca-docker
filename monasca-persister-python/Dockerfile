FROM python:2.7

ARG PERSISTER_REPO=https://github.com/openstack/monasca-persister.git
ARG PERSISTER_BRANCH=master

RUN git clone $PERSISTER_REPO -b $PERSISTER_BRANCH

WORKDIR /monasca-persister
RUN pip install influxdb; pip install -r requirements.txt; python setup.py install

COPY persister.conf /etc/monasca-persister/

CMD ["python", "/usr/local/lib/python2.7/site-packages/monasca_persister/persister.py", "--config-file", "/etc/monasca-persister/persister.conf"]
