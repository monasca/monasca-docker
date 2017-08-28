keystone-shell
==============

This image allows you to quickly interact with a keystone environment.

Sources: [keystone-shell][1] &middot; [Dockerfile][2] &middot; [monasca-docker][3]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.0.0`
 * `1.0.0`, `1.0`, `1`: standard semver tags

Basic Usage
-----------

This is mainly intended for use in Kubernetes environments configured using
[keystone-init][4]. To use, run:

    kubectl run keystone-shell -i -t \
        --rm=true \
        --restart Never \
        --image=monasca/keystone-shell:latest

(pass `-n <NAMESPACE>` as needed if the desired secrets are located elsewhere)

Once the container starts, press enter once to start the shell. Basic usage
information will be printed to the terminal.

There are three commands available:
 - `secret <NAME>`: load keystone `OS_` variables from secret in current 
   namespace `NAME`
 - `shell [NAME]`: start a Python shell (using ptipython, with highlighting 
   and autocomplete) with pre-connected Keystone and Kubernetes clients -
   additional usage information will be printed on startup
   - if specified, secret with `NAME` will be loaded first (as with 
     `secret NAME`) and will override existing environment variables
 - `openstack ...`: the standard openstack client 

Direct Shell
------------

You can also start a shell directly:

    kubectl run keystone-shell \
        --rm=true \
        --restart Never \
        --image=monasca/keystone-shell:latest \
        --env="OS_USERNAME=admin" \
        --env="OS_PASSWORD=secretadmin" \
        --env="OS_PROJECT_NAME=admin" \
        --env="OS_PROJECT_DOMAIN_NAME=Default" \
        --env="OS_USER_DOMAIN_NAME=Default" \
        --env="OS_AUTH_URL=http://monasca-keystone:35357/" \
        --env="KEYSTONE_SHELL=true" \
        --attach -i -t

Note the `KEYSTONE_SHELL` variable. `OS_` variables can also be provided in
lieu of a secret name (allowing the container to be run in docker rather than
Kubernetes).


Verifying Keystone Connectivity
-------------------------------

This container can be used as a one-off method to check if a Keystone instance
is available. To use, try:

    kubectl run keystone-shell \
        --rm=true \
        --restart Never \
        --image=monasca/keystone-shell:latest \
        --env="KEYSTONE_SECRET=keystone-example-user" \
        --attach
        
Note the absence of the `-i` and `-t` parameters. Note that `KEYSTONE_SECRET`
must be defined in this scenario.

If Keystone is available and the credentials work, the return code will be
zero. If Keystone is not available or the credentials are invalid, the return
code will be 1. Log information should be printed to help narrow down the
error, or at least as much as Keystone will be willing to divulge about it. 

Configuration
-------------

| Variable           | Default          | Description                     |
|--------------------|------------------|---------------------------------|
| `LOG_LEVEL`        | `INFO` | MySQL server host               |
| `KEYSTONE_TIMEOUT` | `10`   | MySQL server port               |
| `KEYSTONE_VERIFY`  | `true` | MySQL user w/ needed privileges |
| `KEYSTONE_CERT`    | unset  | Password for given user         |
| `KEYSTONE_SECRET`  | unset  | Secret to auto-load on startup  |
| `OS_AUTH_URL`            | unset | (**required**)               |
| `OS_USERNAME`            | unset | keystone username            |
| `OS_PASSWORD`            | unset | keystone password            |
| `OS_USER_DOMAIN_NAME`    | unset | keystone user domain name    |
| `OS_PROJECT_NAME`        | unset | keystone project name        |
| `OS_PROJECT_DOMAIN_NAME` | unset | keystone project domain name |

[1]: https://github.com/monasca/monasca-docker/blob/master/keystone-shell/
[2]: https://github.com/monasca/monasca-docker/blob/master/keystone-shell/Dockerfile
[3]: https://github.com/monasca/monasca-docker/
[4]: https://github.com/monasca/monasca-docker/blob/master/keystone-init/