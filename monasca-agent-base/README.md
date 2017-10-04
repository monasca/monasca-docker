monasca-agent-base Dockerfile
========================

This image contains a containerized version of the Monasca agent code. For more
information on the Monasca project, see [the wiki][1].

Sources: [monasca-agent][2] &middot; [monasca-docker][3] &middot; [Dockerfile][4]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.6.0`
 * `1.6.0`, `1.6`, `1`: standard semver tags, based on git tags in the
   [official repository][2].
 * `mitaka`, `newton`, etc: named versions following OpenStack release names
   built from the tip of `stable/RELEASENAME` branches in the repository
 * `master`, `master-DATESTAMP`: unstable testing builds from the master branch,
   these may have features or enhancements not available in stable releases, but
   are not production-ready.

Note that features in this Dockerfile, particularly relating to Docker and
Kubernetes monitoring, require plugins that have not yet been officially
released or merged. Until this changes, only `master` images may be available.

Usage
-----

It is designed only for use as a base docker image for other images that run
the monasca-agent processes in separate containters. See monasca-agent-forwarder
and monasca-agent-collector. This image can not be run by itself.

Configuration
-------------

The images built using this image have their own configuration. See the README
for those images

Building
--------

[dbuild][6] can be used with the build.yml file to build and push the
container.

To build the container from scratch using just docker commands, run:

    docker build -t youruser/agent-base:latest .

A few build argument can be set:

 * `AGENT_REPO`: a git repository (`http://`, `https://`, or `git://`) with
   agent code to install
 * `AGENT_BRANCH`: a git refspec (not necessarily branch) to pull from. This can
   be a tagged point release (e.g. `1.6.0`), an OpenStack release branch (e.g.
   `stable/newton`), a Gerrit patch ref (e.g. `refs/changes/71/427271/10`),
   or any other valid Git ref for the target repository.
 * `REBULID`: a simple method to invalidate the Docker image cache. Set to
   `--build-arg REBUILD="$(date)"` to force a full image rebuild.
 * `HTTP_PROXY` and `HTTPS_PROXY` should be set as needed for your environment

If you'd like to build this image against an uncommitted working tree, consider
using [git-sync][5] to mirror your local tree to a temporary git repository.

[1]: https://wiki.openstack.org/wiki/Monasca
[2]: https://github.com/openstack/monasca-agent
[3]: https://github.com/hpcloud-mon/monasca-docker/
[4]: https://github.com/hpcloud-mon/monasca-agent-base/blob/master/monasca-agent/Dockerfile
[5]: https://github.com/timothyb89/git-sync
[5]: https://github.com/timothyb89/dbuild
