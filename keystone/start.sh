#!/bin/bash
keystone-manage --config-file=/etc/keystone/keystone.conf db_sync
keystone-all --config-file /etc/keystone/keystone.conf
