#!/usr/bin/env bash

kubectl create -f namespace.yml
kubectl create -f non_persistent_storage_k8s/influx/
kubectl create -f keystone/
kubectl create configmap --from-file mysql/mon_mysql.sql mon.mysql -n monitoring
kubectl create -f non_persistent_storage_k8s/mysql/
kubectl create -f mysql/mysql-service.yml
kubectl create -f non_persistent_storage_k8s/zookeeper/
kubectl create -f non_persistent_storage_k8s/kafka/
kubectl create -f storm/
kubectl create -f monasca-python/
kubectl create -f monasca/
kubectl create -f grafana/
