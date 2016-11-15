FROM python:2.7

RUN pip install monasca-notification

COPY notification.yaml /config/

VOLUME ["config"]

ENTRYPOINT ["monasca-notification", "/config/notification.yaml"]
