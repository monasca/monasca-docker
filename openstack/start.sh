#!/bin/bash
keystone-manage --config-file=/etc/keystone/keystone.conf db_sync
keystone-all --config-file /etc/keystone/keystone.conf
/etc/init.d/apache2 start
echo "The monasca api is configured to be at the hostname api, use container linking to set this."
