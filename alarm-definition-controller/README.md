Alarm Definition Controller Dockerfile
=====================

This image is used for running the Monasca Alarm Definition Controller in Kubernetes.
The use is for having a Monasca Alarm Definition Kubernetes Third Party Resource that
allows users to create/modify/delete alarm definitions via creating Kubernetes Resources.

This alleviates the need for users of Monasca to tie into our alarm init container or have
to tie into a centralized location of all alarm definitions. They control and configure
the alarm definitions relevant to what they are working on.

Sources: [alarm-definition-controller][1] &middot; [Dockerfile][2] &middot; [Helm Implementation][3]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.0.0`
 * `1.0.0`, `1.0`, `1`: standard semver tags

Usage
-----

This image can only be run in a Kubernetes Environment. It can be brought up via [Monasca-Helm][4].

Once running in Kubernetes you can create Alarm Definitions by creating a Kubernetes resource.

[1]: https://github.com/monasca/alarm-definition-controller
[2]: https://github.com/monasca/monasca-docker/blob/master/alarm-definition-controller/Dockerfile
[3]: https://github.com/monasca/monasca-helm/blob/master/monasca/templates/alarm-definition-controller-deployment.yaml
[4]: https://github.com/monasca/monasca-helm
