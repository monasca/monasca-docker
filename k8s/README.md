Simple Monasca Kubernetes Configuration
=======================================

This demonstrates a simple Monasca deployment on Kubernetes. Persistent storage
is handled by GlusterFS.

Creating GlusterFS Volumes
--------------------------

(Assumes an mn1-like cluster config)

On each node:

    sudo mkdir /gluster/brick1/monitoring-{kafka,zookeeper} -p

On any single node:

    sudo gluster volume create monitoring-zookeeper replica 2 \
        10.243.82.132:/gluster/brick1/monitoring-zookeeper \
        10.243.82.133:/gluster/brick1/monitoring-zookeeper \
        10.243.82.134:/gluster/brick1/monitoring-zookeeper \
        10.243.82.135:/gluster/brick1/monitoring-zookeeper

    sudo gluster volume start monitoring-zookeeper

    sudo gluster volume create monitoring-kafka replica 2 \
        10.243.82.132:/gluster/brick1/monitoring-kafka \
        10.243.82.133:/gluster/brick1/monitoring-kafka \
        10.243.82.134:/gluster/brick1/monitoring-kafka \
        10.243.82.135:/gluster/brick1/monitoring-kafka

    sudo gluster volume start monitoring-kafka

Deploying
---------

    kubectl create -f namespace.yml
    kubectl create -f zookeeper.yml
    kubectl create -f kafka.yml
    kubectl create -f keystone.yml
