#!/bin/bash
echo "The keystone default admin token is 'ADMIN', admin/admin/admin is user/pass/project. The monasca users still need to be setup."
keystone-all --config-file /etc/keystone/keystone.conf &
/etc/init.d/apache2 start
nova-api
