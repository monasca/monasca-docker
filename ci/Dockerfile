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
RUN apt-get install -y docker.io maven python-dev python-pip
RUN pip install -U pip
RUN pip install ansible docker-py==1.1.0
RUN apt-get clean

# Install JJB
RUN git clone https://git.openstack.org/openstack-infra/jenkins-job-builder ./jenkins-job-builder
RUN pip install -r ./jenkins-job-builder/requirements.txt
COPY jenkins_jobs.ini /etc/jenkins_jobs/jenkins_jobs.ini
WORKDIR /setup/jenkins-job-builder
RUN python ./setup.py install
WORKDIR /setup

## From the parent image
#ENTRYPOINT ["/usr/local/bin/jenkins.sh"]
