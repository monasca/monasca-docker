#!/usr/bin/env bash

kubectl create -f namespace.yml

kubectl create configmap --from-file influx/influxdb.conf influxdb-1.0.0.conf -n monitoring
kubectl create -f non_persistent_storage_k8s/influx/
kubectl create -f influx/influxdb-init-job.yml

kubectl create -f keystone/

kubectl create configmap --from-file mysql/mon_mysql.sql mon.mysql -n monitoring
kubectl create -f non_persistent_storage_k8s/mysql/
kubectl create -f mysql/mysql-service.yml

kubectl create -f non_persistent_storage_k8s/zookeeper/
kubectl create -f non_persistent_storage_k8s/kafka/

kubectl create -f storm/storm-config.yml
kubectl create -f storm/storm-services.yml
kubectl create -f storm/storm-supervisor.yml
kubectl create -f non_persistent_storage_k8s/storm/storm-nimbus.yml

kubectl create -f monasca-python/
kubectl create -f monasca/
kubectl create -f grafana/
