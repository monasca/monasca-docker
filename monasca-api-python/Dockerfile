FROM python:2.7

RUN pip install gunicorn
RUN pip install monasca-api
RUN pip install influxdb

RUN mkdir /etc/monasca
COPY api-config.conf /etc/monasca/
COPY api-logging.conf /etc/monasca
COPY api-config.ini /config/

VOLUME ["/config"]

ENTRYPOINT ["gunicorn", "--capture-output", "-n", "monasca-api", "-k", "eventlet", "--worker-connections=2000", "--backlog=1000", "--paste", "/config/api-config.ini", "-w", "9"]
