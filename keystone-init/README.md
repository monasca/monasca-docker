keystone-init Dockerfile
========================

This image creates resources in an existing Keystone deployment .

Sources: [keystone-init][1] &middot; [Dockerfile][2] &middot; [monasca-docker][3]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.0.0`
 * `1.0.0`, `1.0`, `1`: standard semver tags

Usage
-----

This image requires access to a running Keystone instance, along with valid
Keystone credentials with permission to create additional Keystone resources.

The job is intended to be run only once like so, and requires no persistent
storage:

    docker run --rm=true monasca/keystone-init:latest

If needed, connection parameters can be provided via environment variables as
described below. This script should be idempotent and will either leave Keystone
in the desired state or return an error. Subsequent executions will create or
potentially modify resources if the preload configuration changes but will
otherwise leave unchanged resources unchanged.

Note that the [Helm chart][4] can be used in a Kubernetes environment to easily
configure and run the job.

Configuration
-------------

| Variable           | Default          | Description                      |
|--------------------|------------------|----------------------------------|
| `LOG_LEVEL`        | `INFO` | Python logging level, e.g. `DEBUG`         |
| `KEYSTONE_TIMEOUT` | `10`   | Keystone connection timeout                |
| `KEYSTONE_VERIFY`  | `true` | If `false`, skip SSL verification          |
| `KEYSTONE_CERT`    | unset  | Path to mounted CA bundle (if self-signed) |
| `OS_AUTH_URL`            | unset | Keystone URL                          |
| `OS_USERNAME`            | unset | Keystone username                     |
| `OS_PASSWORD`            | unset | Keystone password                     |
| `OS_USER_DOMAIN_NAME`    | unset | Keystone user domain name             |
| `OS_PROJECT_NAME`        | unset | Keystone project name                 |
| `OS_PROJECT_DOMAIN_NAME` | unset | Keystone project domain name          |

Note that *all* `OS_` variables listed above are **required** but unset by
default. Many other standard Keystone environment variables (`OS_`) are also
supported but not generally needed; for a full list see [`keystone_init.py`][5].

Preload configuration
---------------------

A single file, `/preload.yml`, should be mounted into the container to provide
preload configuration. The default config file is empty, and should be
overridden for this container to be of any use.

An empty config file looks as follows:

```yaml
domains:
  default:
    projects: []
    roles: []
    users: []
    groups: []

services:
  example:
    type:
    description:
    endpoints: []
```

Domains are created by their unique name *except* for `default`, which
references the Keystone domain with the literal ID `default`. If you wish to
create a domain with no additional resources, define it like so:

```yaml
domains:
  example: {}
```

Projects, roles, and users are unique within a domain, and can be defined as
lists of strings under their respective YAML blocks. For example:

```yaml
domains:
  default:
    projects:
      - demo-project

    roles:
      - demo-role
```

The `users` block accepts a list of objects. As an example:

```yaml
domains:
  default:
    # ...
    users:
      - username: test-user
        project: some-project
        roles: [a, b, c]
        domain_roles: [d, e, f]
        secret: some-secret-name
```

Each defined user will have its Keystone `project` set to the resolved ID of
the project name provided in the preload config. If the user should not be
assigned to a project, the field can be ignored. The user will also have each
resolved role applied. Projects and roles that do not exist will be created
(note that projects and roles *do not* need to be defined in the `projects` or
`roles` blocks).

If the `password` field is not specified (recommended!) a password will be
randomly generated using the system's CSPRNG. When a `secret` field is specified
(also recommended!), a Kubernetes secret of the same name will be created as
well, in (by default) the namespace from which the job is run. If desired,
secrets can be specified in multiple ways:

```yaml
# will create in the job's namespace
secret: some-secret

# will create in 'some-namespace'
secret: some-namespace/some-secret

# will create in some namespace
secret:
  namespace: some-namespace
  name: some-secret
```

Note that specifying a `secret` field in a Docker-only environment will result
in an error, as for now secret management is only available in Kubernetes.
Consequently, random password generation is probably undesirable in plain Docker
environments given there is no ability to save the generated password anywhere.
In this case, a `password` field can be added to user objects to manually
provide a password.

Generated secrets will include several fields in the style of standard `OS_`
auth variables. If using Helm, we recommend using [`_keystone_env.tpl`][6] from
the [keystone-init][4] chart to consume these.

As an example, given this `values.yaml`:
```yaml
# in values.yaml
my_pod:
  auth:
    url:
      secret_name: some-secret
    username:
      secret_name: some-secret
    password:
      secret_name: some-secret
    user_domain_name:
      secret_name: some-secret
    project_name:
      secret_name: some-secret
    project_domain_name:
      secret_name: some-secret
```

Then this pod spec will include secrets using the `keystone_env` template:
```yaml
# snippet from an example Kubernetes Pod spec
containers:
  - name: some-name
    image: some-image
    env:
      - name: MY_VAR
        value: some-value
# adjust indent() as necessary
{{ include "keystone_env" .Values.my_pod.auth | indent(6) }}
```

The `groups` block can contain a list of groups to be created. The list
can consist of group names as string values, or objects containing role
grants. For instance:
```yaml
domains:
  default:
    groups:
      - a
      - name: b
        project_roles:
          - project: c
            roles: d, e
        domain_roles:
          - foo
          - bar

```

Services are created by their unique name:
```yaml
services:
  example:
    type:
    description:
    endpoints: []
```
In this case service with `example` name will be created first and then
endpoint will be added to it with provided endpoints.
`description` is optional.

The `endpoints` block accepts a list of objects. As an example:
```yaml
services:
  example:
    # ...
    endpoints:
      - url: http://int-url:8070/v2.0
        interface: internal
        region: some_region
      - url: http://other-url:8070/v2.0
        interface: admin
        region: other_region
```
In case when endpoint on same service and with same interface is already
specified in Keystone but `url` is different it will be updated with new `url`.

Keystone support following endpoint interface types:
`public`, `admin`, `internal`.

Other Notes
-----------

Users belong to a project if a special member role is applied to a particular
(domain, user, project) combination. `keystone-init` will automatically apply
(and if necessary, create) a global member role to users when `project:` is
specified on a User object.

By default this role is named `_member_`, but if your Keystone instance uses a
different member role, its name can be specified using the `member_role:`
property at the root of `preload.yml`. Note that this name should correspond to
the value of `member_role_name` in the `[DEFAULT]` section of `keystone.conf`.


[1]: https://github.com/monasca/monasca-docker/blob/master/keystone-init/
[2]: https://github.com/monasca/monasca-docker/blob/master/keystone-init/Dockerfile
[3]: https://github.com/monasca/monasca-docker/
[4]: https://github.com/monasca/monasca-helm/tree/master/keystone-init
[5]: https://github.com/monasca/monasca-docker/blob/7a7a6032c29ebba3a33e6af29566fd26243cf3ba/keystone-init/keystone_init.py#L39
[6]: https://github.com/monasca/monasca-helm/blob/master/keystone-init/templates/_keystone_env.tpl
