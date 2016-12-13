# Monasca Kubernetes Configuration #

This demonstrates a simple Monasca deployment on Kubernetes.

If desired it can be deployed using persistent storage via GlusterFS.

## Creating GlusterFS Volumes ##

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

## Deploying with GlusterFS ##

Run the bash script `monasca-start-glusterfs.sh`.

## Deploying without Persistent Storage ##

Run the bash script `monasca-start.sh`.

## Know Issues and Workarounds (if applicable)

#### Invalid Java Implementations
 
The Java implementation for the API and Persister do not work with the version of influxdb. Use only the python implementations at this time.

#### Mon influxdb database has to be manually created

The Influxdb deployment does not create the mon database.

After running the deployment steps you must exec into the influxdb pod and create the database:

```bash
kubectl exec -it {{ influx_pod_name }} -n monitoring bash
influx -execute "create database mon"
```

## Running Monasca within Kubernetes on a Macbook ##

Kubernetes can be set up easily on a macbook via [Kube-cluster](https://github.com/TheNewNormal/kube-cluster-osx)

Once you follow the steps to get a Kubernetes cluster up you can follow the steps from the section above - Deploying without Persisten Storage.

#### Keystone issue and workaround

In the kube-cluster environment the keystone pod has issues connecting to itself to set up the keystone users and groups.

The workaround is to exec into the pod and manually run the configuration script until it succeeds without throwing a ConnectFailure Exception.

```bash
kubectl exec -it {{ keystone_pod_name }} -n monitoring bash
./keystone-bootstrap.sh
```

## Future Work
* Replace configuration files and bash scripts for deploying with [Helm](https://github.com/kubernetes/helm)