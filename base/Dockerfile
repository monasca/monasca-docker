# Base Ubuntu 14.04 image with Ansible

FROM ubuntu:14.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

RUN apt-get -yqq update && apt-get -y dist-upgrade
COPY . /setup

# Setup Ansible
RUN apt-get install -y python-pip python-dev
RUN pip install ansible
