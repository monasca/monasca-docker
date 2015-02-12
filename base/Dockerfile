# Base Ubuntu 15.04 image with Ansible

FROM ubuntu:15.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

RUN apt-get -yqq update && apt-get -y dist-upgrade
COPY . /setup


# Setup Ansible
RUN apt-get install -y python-pip python-dev

# For some reason the 15.04 version of pip is installing everything as a user package, override that
RUN mv /usr/bin/pip /usr/bin/pip.orig
RUN echo '#!/bin/bash\nif [ $1 == "install" ]; then\n\tshift\n\t/usr/bin/pip.orig install --system $@\nelse\n\t/usr/bin/pip.orig $@\nfi' > /usr/bin/pip
RUN chmod +x /usr/bin/pip

RUN pip install ansible
