#!/bin/bash
echo "The keystone default admin token is 'ADMIN', admin/admin/admin is user/pass/project. The monasca users still need to be setup."
keystone-all --config-file /etc/keystone/keystone.conf &
/etc/init.d/apache2 start

# The pip installed deps used by the ui conflict some with glance, skip them.
export PYTHONPATH=/usr/lib/python2.7:/usr/lib/python2.7/plat-x86_64-linux-gnu:/usr/lib/python2.7/lib-tk:/usr/lib/python2.7/lib-old:/usr/lib/python2.7/lib-dynload:/usr/lib/python2.7/dist-packages
glance-api &
cinder-api &
nova-api
