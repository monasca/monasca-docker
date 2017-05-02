monasca/job-cleanup Dockerfile
==============================

This image is intended to clean up old Kubernetes jobs during a Kubernetes
upgrade to avoid potential naming conflicts. For more information on the Monasca
project, see [the wiki][1].

When run as a job, it will:
 * Remove any completed pods with `app` and `component` labels that match its
   own pod
 * Remove any completed jobs with matching `app` and `component` labels
 * Remove itself

Sources: [job-cleanup][2] &middot; [Dockerfile][3] &middot; [monasca-docker][4]

Tags
----

 * `latest`: refers to the latest stable point release, e.g. `1.0.1`
 * `1.0.0`, `1.0`, `1`: standard semver tags

Usage
-----

If you've deployed Monasca using [Helm][5] and wish to upgrade, you'll need to
remove old jobs to avoid naming conflicts. Normally this container should be
spawned automatically as a Helm hook, but you could run it manually like so:

    kubectl run cleanup \
      --namespace monitoring \
      --image=monasca/job-cleanup:latest \
      --labels='app=my-release-name-monasca,component=cleanup' \
      --restart=OnFailure \
      --attach

Note that this example assumes Monasca has been deployed to the `monitoring`
namespace and the other pods have `app=my-release-name-monasca` labels. The
`component=cleanup` label is used to differentiate the selector from other
labeled pods with the same `app` label.

Configuration
-------------

There are 3 options that can be specified at runtime:
 * `USE_KUBE_CONFIG`: if set, load cluster connection info from a kubeconfig
   file (e.g. `~/.kube/config` or `$KUBECONFIG`). When unset (default) this info
   is loaded from `/var/run/secrets/kubernetes.io/serviceaccount/`
 * `NAMESPACE`: the namespace to search for jobs to clean up
 * `POD_NAME`: the name of a pod to use as a label reference (it should share
   an `app` label with the jobs that should be cleaned up)

If not specified, these parameters will be auto-detected based on the current
pod. Note that specifying either `NAMESPACE` or `POD_NAME` will prevent
self-deletion. While this is sometimes appropriate (e.g. just running cleanup
manually from a dev machine), it's recommended to let it auto-detect and
self-delete when run as a Kubernetes job.

[1]: https://wiki.openstack.org/wiki/Monasca
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/job-cleanup/
[3]: https://github.com/hpcloud-mon/monasca-docker/blob/master/job-cleanup/Dockerfile
[4]: https://github.com/monasca/monasca-docker
[5]: https://github.com/monasca/monasca-helm
