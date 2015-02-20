#!/bin/bash
echo "The keystone default admin token is 'ADMIN', admin/admin is user/pass. The monasca users still need to be setup."
keystone-all --config-file /etc/keystone/keystone.conf &
python /usr/share/openstack-dashboard/manage.py compress  # This seems to be needed after startup
/etc/init.d/apache2 start
nova-api
