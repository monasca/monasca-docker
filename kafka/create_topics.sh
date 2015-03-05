# Start up kafka, make topics and the put kafka back into the foreground
# Since the container requires zookeeper I can't make the topics on image create

set -m
/opt/kafka/bin/kafka-server-start.sh /etc/kafka/server.properties &

# This playbook will create the topics
cd /setup
ansible-playbook -i hosts topics.yml -c local

fg
