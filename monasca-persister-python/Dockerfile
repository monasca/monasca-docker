FROM python:2.7

ENV MONASCA_PERSISTER_REPO=https://github.com/openstack/monasca-persister.git
ENV MONASCA_PERSISTER_BRANCH=master

RUN mkdir /source
WORKDIR /source
RUN git clone $MONASCA_PERSISTER_REPO -b $MONASCA_PERSISTER_BRANCH

WORKDIR monasca-persister
RUN pip install influxdb; pip install -r requirements.txt
RUN python setup.py install

COPY persister.conf /config/

CMD ["python", "/usr/local/lib/python2.7/site-packages/monasca_persister/persister.py", "--config-file", "/config/persister.conf"]
