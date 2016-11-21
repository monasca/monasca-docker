Monasca Kubernetes Configuration
================================

This demonstrates a simple Monasca deployment on Kubernetes. Persistent storage
is handled by GlusterFS.

Creating GlusterFS Volumes
--------------------------

Several services are configured to use GlusterFS to store persistent data. These
config files assume that all needed volumes exist already, and if they don't
exist or aren't otherwise accessible, pods will get stuck in the
`ContainerCreating` state.

The following script can be used to run all of the necessary GlusterFS volumes
easily (note, only appropriate for testing configurations):

```bash
#!/bin/bash
VOLUME=$1
for node in 10.243.82.132 10.243.82.133 10.243.82.134 10.243.82.135; do
    ssh -t ubuntu@${node} sudo mkdir /gluster/brick1/$VOLUME -p;
done

ssh -t ubuntu@10.243.82.132 sudo gluster volume create $VOLUME replica 2 \
        10.243.82.132:/gluster/brick1/$VOLUME \
        10.243.82.133:/gluster/brick1/$VOLUME \
        10.243.82.134:/gluster/brick1/$VOLUME \
        10.243.82.135:/gluster/brick1/$VOLUME

ssh -t ubuntu@10.243.82.132 sudo gluster volume start $VOLUME
```

Adjust the addresses of nodes as needed, our GlusterFS cluster has four nodes
configured identically. Ideally, you should have passwordless SSH key
authentication and sudo access.

In any case, volumes with the following names should be available before
continuing further:

 * `monitoring-mysql`
 * `monitoring-influx`
 * `monitoring-kafka`
 * `monitoring-zookeeper`
 * `monitoring-zookeeper-log`
 * `monitoring-storm`

If no persistent storage is desired, the volume definitions for each of the
above can be replaced with `emptyDir: {}`, though any data stored will be lost
if the pods restart for any reason.

Deploying
---------

First, create the namespace and GlusterFS endpoints:

    kubectl create -f namespace.yml
    kubectl create -f glusterfs.yml

Next, deploy the base services. These can be started in any order and don't
depend on any other services to exist:

    kubectl create -f influx/
    kubectl create -f keystone/
    kubectl create -f mysql/
    kubectl create -f zookeeper/

Once all of the above have started successfully, the next batch can be brought
up:

    kubectl create -f kafka/
    kubectl create -f storm/

Next, monasca can be started:

    kubectl create -f monasca/

Lastly, if desired, grafana can be added:

    kubectl create -f grafana/
