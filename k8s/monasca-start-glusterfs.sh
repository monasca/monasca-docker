#!/usr/bin/env bash

kubectl create -f namespace.yml
kubectl create -f gluster-storage-class.yml
kubectl create configmap --from-file influx/influxdb.conf influxdb-1.0.0.conf -n monitoring
kubectl create -f influx/
kubectl create -f keystone/
kubectl create configmap --from-file mysql/mon_mysql.sql mon.mysql -n monitoring
kubectl create -f mysql/
kubectl create -f zookeeper/
kubectl create -f kafka/
kubectl create configmap --from-file storm/storm.yaml monasca-thresh-config -n monitoring
kubectl create -f storm/storm-nimbus.yml
kubectl create -f storm/storm-supervisor.yml
kubectl create -f storm/storm-services.yml
kubectl create -f monasca/
kubectl create -f monasca-python/
kubectl create -f grafana/
