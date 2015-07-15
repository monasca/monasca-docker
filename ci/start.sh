#!/bin/sh

# Call the parent image entry point
/usr/local/bin/jenkins.sh &

# Wait for Jenkins to come up
sleep 60

# Setup the bootstrap job and trigger
jenkins-jobs --conf /etc/jenkins_jobs/jenkins_jobs.ini update /setup/update_jobs.yaml
curl http://localhost:8080/git/notifyCommit?url="https://github.com/hpcloud-mon/monasca-ci"

# Wait on Jenkins
wait
