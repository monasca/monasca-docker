Monasca Kubernetes Configuration
================================

This demonstrates a simple Monasca deployment on Kubernetes. The default
deployment configuration does not use persistent storage and would be suitable
for development use in e.g. [minikube][1] or [kube-clister][2].

The deployment scripts in this repository will make use of a configured
`kubectl` and will start all Monasca components in the `monitoring` namespace.
The deployment includes the following:
 * A full Monasca pipeline: API, persister, threshold and notification engines
 * All required backend services: zookeeper, kafka, influx, storm, mysql
 * Agents on each node monitoring all k8s resources, annotated Prometheus
   endpoints, and host nodes
 * Keystone with demo accounts
 * Grafana with pre-configured with Keystone login, a Monasca datasource, and
   some general-purpose dashboards

Deployment
----------

### Without persistent storage

To use, run:

    ./monasca-start.sh

### With persistent storage (GlusterFS)

To make use of persistent storage, your target cluster must support persistent
volume claims. With GlusterFS, this means [heketi][3] should be available as per
the instructions in [gluster-kubernetes][4]. Other backends should be supported
but may require modifications to the `storage-class` annotations in
the `**/*-pvc.yml` claim templates.

To use, run:

    ./monasca-start-glusterfs.sh

Know Issues and Workarounds
---------------------------

### Invalid Java Implementations

The Java implementation for the API and persister do not work with the version
of InfluxDB. Use only the Python implementations at this time.

### Persister crashes when first deployed

The persister may crash several times when first deployed. This is likely due to
the Kafka topic having no elected leader. The leader election process takes
roughly 60 seconds

## Running Monasca within Kubernetes on a MacBook

Kubernetes can be set up easily on a MacBook via [kube-cluster][2]

Once you follow the steps to get a Kubernetes cluster up you can follow the
steps from the section above - Deploying without Persistent Storage.

## Future Work

 * Replace configuration files and bash scripts for deploying with [Helm][5].
   See progress toward this goal in [monasca-helm][6].

[1]: https://github.com/kubernetes/minikube
[2]: https://github.com/TheNewNormal/kube-cluster-osx
[3]: https://github.com/heketi/heketi
[4]: https://github.com/gluster/gluster-kubernetes
[5]: https://github.com/kubernetes/helm
[6]: https://github.com/hpcloud-mon/monasca-helm
