ARG MON_AGENT_BASE_VERSION
FROM monasca/agent-base:${MON_AGENT_BASE_VERSION}

# To force a rebuild, pass --build-arg REBUILD="$(DATE)" when
# running `docker build`
ARG REBUILD=1

COPY start.sh agent.yaml.j2 /

CMD ["/start.sh"]
