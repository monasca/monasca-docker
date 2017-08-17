mysql-users-init Dockerfile
===========================

This image creates MySQL users and databases and can store the resulting
connection details in a Kubernetes secret.

Sources: [mysql-users-init][1] &middot; [Dockerfile][2] &middot; [monasca-docker][3]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.0.0`
 * `1.0.0`, `1.0`, `1`: standard semver tags

Usage
-----

This image requires access to a running MySQL server instance, along with valid
credentials with permission to create additional databases and users.

The job is intended to be run only once like so, and requires no persistent
storage:

    docker run --rm=true monasca/mysql-users-init:latest

If needed, connection parameters can be provided via environment variables as
described below. This script should be idempotent and will either leave MySQL
in the desired state or return an error. Subsequent executions will create or
potentially modify resources if the preload configuration changes but will
otherwise leave unchanged resources unchanged.

Note that the [Helm chart][4] can be used in a Kubernetes environment to easily
configure and run the job.

Configuration
-------------

| Variable              | Default              | Description                  |
|-----------------------|----------------------|------------------------------|
| `LOG_LEVEL`           | `INFO`               | Log level (`INFO`, `DEBUG`)  |
| `MYSQL_INIT_HOST`     | unset (**required**) | MySQL hostname               |
| `MYSQL_INIT_PORT`     | unset (**required**) | MySQL TCP port               |
| `MYSQL_INIT_USERNAME` | unset (**required**) | MySQL username               |
| `MYSQL_INIT_PASSWORD` | unset (**required**) | MySQL password               |
| `PRELOAD_PATH`        | `/preload.yml`       | Path to preload file to read |
| `NAMESPACE`           | unset (autodetect)   | K8s namespace                |

Preload configuration
---------------------

A single file, `/preload.yml`, should be mounted into the container to provide
preload configuration. The default config file is empty, and should be
overridden for this container to be of any use.

An empty config file looks as follows:

```yaml
users: []
databases: []
```

### Users

The `users` list accepts an arbitary number of user objects. Minimally these
should contain a username and a secret name:

```yaml
users:
  # recommended config, secret will be created in the job's namespace
  - username: example-user
    secret: mysql-example-user

  # the secret's namespace can be specified directly too
  - username: another-user
    secret:
      namespace: some-namespace
      name: mysql-example-user

  # if desired a hardcoded password can be used
  - username: other-user
    password: hunter2

  # hostnames can be specified too (['%', localhost] by default)
  # be wary of the 16 character username limit!
  - username: user4
    secret: mysql-user4
    host: '172.17.0.2' # either a string or list of strings
```

One `CREATE USER ...` query will be run per host per user that does not already
exist on the server. Note that `GRANT ...` queries during database creation (see
below) are handled similarly, using the hosts defined here.

If a user is to be created and a Kubernetes secret with the defined name already
exists, the existing password will be extracted from the secret and reused.
Otherwise, a new, random password will be generated and a secret will be
created.

Note that specifying a `secret` field in a Docker-only environment will result
in an error, as for now secret management is only available in Kubernetes.
Consequently, random password generation is probably undesirable in plain Docker
environments given there is no ability to save the generated password anywhere.
In this case, a `password` field can be added to user objects to manually
provide a password.

Each generated secret contains the following fields: `username`, `password`,
`host`, `port`

### Databases

Databases minimally require a name and a list of grants. Grants should generally
refer to a user defined in the `users` list:

```yaml
databases:
  - name: example-database
    grants:
      - example-user
```

In the above, two `GRANT ALL ...` queries are run, for `example-user@localhost`
and `example-user@%` (based on the hosts implicitly defined in the
example-users's definition in the `users` list).

Additional optional fields are available:
```yaml
databases:
  - name: another-database
    charset: utf8mb4
    collation: utf8mb4_unicode_ci
```

If either `charset` or `collation` are unset, the server's default values are
used.

Additionally, if desired more finely-grained privilege grants can be specified:
```yaml
databases:
  - name: other-database
    grants:
      - other-user # ALL by default

      # hosts can be overridden (pulled from users block by default)
      - username: another-user
        host: localhost

      # specific privileges can be granted
      - username: other-user
        privileges:
          - select
          - insert

      # comma-separated strings are okay too
      - username: user4
        privileges: create, drop
```

Some notes about privilege grants:
 - Only database-level GRANTs are supported
 - The `NO_AUTO_CREATE_USER` MySQL server option is explicitly enabled, so
   attempting to grant privileges to any user/host combination that hasn't been
   explicitly created will result in an error.


[1]: https://github.com/monasca/monasca-docker/blob/master/mysql-users-init/
[2]: https://github.com/monasca/monasca-docker/blob/master/mysql-users-init/Dockerfile
[3]: https://github.com/monasca/monasca-docker/
[4]: https://github.com/monasca/monasca-helm/tree/master/mysql-users-init
