#!/usr/bin/env bash

kubectl create -f namespace.yml
kubectl create -f gluster-storage-class.yml

kubectl create configmap --from-file influx/influxdb.conf influxdb-1.0.0.conf -n monitoring
kubectl create -f influx/

kubectl create -f keystone/

kubectl create -f mysql/

kubectl create -f zookeeper/
kubectl create -f kafka/

kubectl create -f storm/
kubectl create -f monasca/
kubectl create -f monasca-python/
kubectl create -f grafana/
