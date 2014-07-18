# OpenStack Keystone with the mini-mon user
FROM monasca/base:14.04
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

RUN apt-get update
RUN apt-get install -y keystone sqlite

ADD ./mini-mon-create.py /root/mini-mon-create.py
ADD ./start.sh /start.sh
RUN chmod 755 /start.sh
RUN /start.sh & sleep 5 && python /root/mini-mon-create.py

EXPOSE 5000 35357

CMD /start.sh
