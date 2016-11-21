FROM python:2.7

ENV MONASCA_NOTIFICATION_REPO=https://github.com/openstack/monasca-notification.git
ENV MONASCA_NOTIFICATION_BRANCH=master

RUN git clone $MONASCA_NOTIFICATION_REPO -b $MONASCA_NOTIFICATION_BRANCH
WORKDIR /monasca-notification
RUN pip install -r requirements.txt; python setup.py install

COPY notification.yaml /config/

ENTRYPOINT ["monasca-notification", "/config/notification.yaml"]
