#!/bin/bash
/etc/init.d/apache2 start
keystone-all --config-file /etc/keystone/keystone.conf
echo "The keystone default admin token is 'ADMIN', the monasca users still need to be setup."
