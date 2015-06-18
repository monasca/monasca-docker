#!/bin/sh
# In Ansible jinja2 uses {{ so the same characters in this command make the escaping quite confusing so it is simpler to write this command
docker inspect -f '{{ .NetworkSettings.IPAddress }}' $1
