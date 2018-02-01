ARG MON_CLIENT_VERSION
FROM monasca/client:${MON_CLIENT_VERSION}

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

ENV MONASCA_WAIT_FOR_API=true \
    KEYSTONE_DEFAULTS_ENABLED=true \
    MONASCA_API_URL="http://monasca:8070/v2.0"

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY definitions.yml.j2 /config/definitions.yml.j2
COPY monasca_alarm_definition.py template.py start.sh /

CMD ["/start.sh"]
