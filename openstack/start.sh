#!/bin/bash
keystone-manage --config-file=/etc/keystone/keystone.conf db_sync
/etc/init.d/apache2 start
keystone-all --config-file /etc/keystone/keystone.conf
echo "The monasca api is configured to be at the hostname api, use container linking or --add-host to set this."
