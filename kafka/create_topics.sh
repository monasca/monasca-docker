# Start up kafka, make topics and the put kafka back into the foreground

set -m
/opt/kafka/bin/kafka-server-start.sh /etc/kafka/server.properties &

# This playbook will create the topics
cd /setup
ansible-playbook -i hosts topics.yml -c local --tags kafka_topics

fg
