# Base Ubuntu 14.04 image with Chef and Berkshelf
#
# Largely copied from https://github.com/paulczar/docker-chef-client/blob/master/Dockerfile

FROM ubuntu:14.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

RUN apt-get -yqq update && apt-get -yqq install curl build-essential libxml2-dev libxslt-dev git autoconf
RUN curl -L https://www.opscode.com/chef/install.sh | bash > /dev/null
RUN echo "gem: --no-ri --no-rdoc" > ~/.gemrc
RUN /opt/chef/embedded/bin/gem install berkshelf > /dev/null
