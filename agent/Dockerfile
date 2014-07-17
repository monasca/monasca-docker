FROM monasca/base:14.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

# Run the mon-agent and tmux so it is easy to attach and later run smoke tests

RUN apt-get update
RUN apt-get install -y python-pip python-dev tmux
RUN pip install mon-agent
RUN mon-setup -u mini-mon -p password --project_name mini-mon -s mini-mon --keystone_url http://keystone:35357/v3 --mon_url http://api:8080/v2.0 --headless

# Turn off syslog
RUN echo "log_to_syslog: no" >> /etc/mon-agent/agent.conf

ADD tests /tests
ADD .tmux.conf /.tmux.conf

# It must have a tty (-t) for this to work
CMD tmux
