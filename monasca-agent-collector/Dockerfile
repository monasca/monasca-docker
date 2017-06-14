FROM monasca/agent-base:master-20170614-225502

ARG AGENT_USER="mon-agent"

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when running
# `docker build`
ARG REBUILD=1

COPY start.sh /
COPY templates/ /templates

USER $AGENT_USER

CMD ["/start.sh"]
