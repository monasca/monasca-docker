FROM jenkins
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

WORKDIR /setup
USER root

# Setup Monasca Jenkins plugins
COPY plugins.txt plugins.txt
RUN /usr/local/bin/plugins.sh ./plugins.txt

# Install dependencies
RUN echo "deb http://http.debian.net/debian jessie-backports main" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y docker.io maven python-dev python-pip sshpass  # sshpass is only needed for password based ssh access from Ansible.
RUN pip install -U pip
RUN pip install ansible docker-py==1.1.0 ansible-lint
RUN apt-get clean

# Install JJB
COPY jenkins_jobs.ini /etc/jenkins_jobs/jenkins_jobs.ini
RUN git clone https://git.openstack.org/openstack-infra/jenkins-job-builder ./jenkins-job-builder
WORKDIR /setup/jenkins-job-builder
RUN git checkout 1.2.0
RUN pip install -r ./requirements.txt
RUN python ./setup.py install
WORKDIR /setup

# Add in the Groovy Hooks for Jenkins, https://wiki.jenkins-ci.org/display/JENKINS/Groovy+Hook+Script
COPY init.groovy.d /var/jenkins_home/init.groovy.d/

# Add in the startup script and bootstrap job
COPY start.sh start.sh
COPY update_jobs.yaml update_jobs.yaml

## From the parent image
ENTRYPOINT ["/setup/start.sh"]
