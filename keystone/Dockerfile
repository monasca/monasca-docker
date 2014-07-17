# OpenStack Keystone with the mini-mon user
FROM jameslabocki/keystone
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

RUN /usr/bin/keystone-manage db_sync

ADD ./mini-mon-create.py /root/mini-mon-create.py
RUN /usr/bin/keystone-all & sleep 5 && python /root/mini-mon-create.py

CMD /usr/bin/keystone-all
