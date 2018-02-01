# Contribution Guide

We're happy to accept contributions from the community. To do so, simply submit
a pull request to this repository.

## Contribution Checklist

### Pull Request Scope

We prefer the scope of each change to be as limited as possible. In most cases
that means only a single "module" should be modified in one pull request,
especially if other modules depend on it. In this context, a "module" is a
subdirectory containing a Dockerfile, such as `monasca-agent`,
`monasca-api-python`, `mysql-init`, and so on.

That said, it occasionally makes sense to group a number of small changes
together into one pull request, such as when adding a new linter rule. A hard
maximum of 5 modules can be modified in a single pull request, however.

### Releasing Changes

By default, we do not publish new images with every change. An image push is
triggered in one of two ways:

 * The build configuration (`build.yml`) is changed, usually to increment a
   version number
 * A `!push <module>` tag is included in the merge commit message

Several components are not given explicit versions as they track upstream Git
repositories, so tags are generated automatically at build time. These
components will generally have an alias in `build.yml` that looks like
`:master-{date}-{time}`.

In these instances, `build.yml` will not generate a diff and so no images will
be built automatically. A `!push <module>` tag in the merge commit message can
be used to trigger a rebuild manually.

#### Example workflow: updating `monasca-agent`

The agent containers have fairly complex release requirements as we have a
base image (`monasca-agent-base`) and two dependent containers
(`monasca-agent-collector` and `monasca-agent-forwarder`).

The procedure for releasing looks like this:

 1. Merge any desired upstream changes to
    https://github.com/openstack/monasca-agent
 2. Make a pull request to `monasca-docker` with any desired changes
    (configuration, etc) to update `monasca-agent-base`
    * If no downstream changes are desired, make an empty commit with
      `git commit --allow-empty`
    * Ensure whoever merges the commit includes `!push monasca-agent-base` in
      the commit message
 3. Once a new `monasca-agent-base` image is published, make a new pull request
    to update `monasca-agent-collector` and `monasca-agent-forwarder`
    * These may be grouped together if desired
    * Update `MON_AGENT_BASE_VERSION` in the `build.yml` for the collector and
      forwarder modules
    * Ensure `!push monasca-agent-collector` and `!push monasca-agent-forwarder`
      make their way into the merge commits (both on separate lines in one
      merge commit works fine)
 4. Finally, once all images have been published, update
    `MON_AGENT_FORWARDER_VERSION` and `MON_AGENT_COLLECTOR_VERSION` in `.env`
    in a final PR to ensure the new images are tested in the future.

We have some automation in place for step #4 (and soon #3, assuming no changes
are needed).

### Signing Commits

We require a code sign-off for all contributions to indicate you have the right
to release any code as open-source. As explained by the [Docker project][1]:

> The sign-off is a simple line at the end of the explanation for the patch.
> Your signature certifies that you wrote the patch or otherwise have the right
> to pass it on as an open-source patch.

The agreement we use is the [Developer Certificate of Origin][1] (copied below),
as used by the Linux kernel, Docker, and many other open source projects:

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
1 Letterman Drive
Suite D4700
San Francisco, CA, 94129

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.

```

Assuming you agree, simply add a line like the following to the end of each
commit message:

```
Signed-off-by: Joe Smith <joe.smith@email.com>
```

(note that we do need a real name here!)

For best results, use `git commit -s` to have this metadata added automatically
based on your configured Git name and email.

Ideally, all commits should also be [GPG signed][2], though we aren't strictly
enforcing this at the moment.

## Getting Help

For any contribution-related questions, please file an issue on this repository,
or ask in the `#openstack-monasca` channel on Freenode.

[1]: https://developercertificate.org/
[2]: https://help.github.com/articles/signing-commits-using-gpg/
