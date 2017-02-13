mysql-init Dockerfile
=====================

This image runs a set of user-provided scripts to initialize a MySQL database.
These are standard `.sql` scripts that can manage users and databases as well as
import schemas.

Sources: [mysql-init][1] &middot; [Dockerfile][2] &middot; [monasca-docker][3]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.0.0`
 * `1.0.0`, `1.0`, `1`: standard semver tags

Usage
-----

This image requires access to a running MySQL instance. By default it comes with
the scripts necessary to initialize a MySQL database for Monasca's
[Docker][3] and [Kubernetes][4] environments, but these can be replaced at
runtime as described below.

The job is intended to be run only once like so, and requires no persistent
storage:

    docker run --rm=true monasca/mysql-init:latest

If needed, connection parameters can be provided via environment variables as
described below. This script does not make any attempt to prevent re-execution
of scripts when run against an already-initialized MySQL instance. There are
several methods to account for this:

 * Configure your runtime environment to only execute the job once.
   [Kubernetes Jobs][5] are appropriate for this purpose.
 * Design your MySQL scripts to only execute on a clean database, or use
   constructs like `CREATE DATABASE IF NOT EXISTS...`
 * Use any of the password-changing variables described below to make future
   login attempts fail

Configuration
-------------

| Variable              | Default          | Description                     |
|-----------------------|------------------|---------------------------------|
| `MYSQL_INIT_HOST`     | `mysql`          | MySQL server host               |
| `MYSQL_INIT_PORT`     | `3306`           | MySQL server port               |
| `MYSQL_INIT_USERNAME` | `root`           | MySQL user w/ needed privileges |
| `MYSQL_INIT_PASSWORD` | `secretmysql`    | Password for given user         |
| `MYSQL_INIT_RANDOM_PASSWORD`     | unset | If `true`, reset the user password    |
| `MYSQL_INIT_DISABLE_REMOTE_ROOT` | unset | If `true`, disable remote root login  |
| `MYSQL_INIT_SET_PASSWORD`        | unset | If set, reset password to given value |

While this image requires access (probably `root`-level) to a MySQL instance at
startup, `MYSQL_INIT_DISABLE_REMOTE_LOGIN`, `MYSQL_INIT_RANDOM_PASSWORD`, and
`MYSQL_INIT_CHANGE_PASSWORD` may be used to better lock down the container
once initialization has completed successfully. These commands will only run
if all scripts could be executed successfully.

Notes about password-related variables:
 * `MYSQL_INIT_DISABLE_REMOTE_LOGIN` will remove access from all wildcard hosts
   to the `root` account. As such, it requires privileges to modify the
   `mysql.users` table.
 * `MYSQL_INIT_RANDOM_PASSWORD` will set the specified user's password to a
   random value by running `pwgen -1 32`. It will be written as a line to stdout
   of the form `GENERATED ${MYSQL_INIT_USERNAME} PASSWORD: $(pwgen -1 32)`

Scripts matching `/mysql-init.d/*.sql` will be executed in alphabetical order.
While the image has Monasca-specific scripts built in, these can be replaced
with a Docker volume mount:

    docker run --rm=true -v /path/to/new/scripts:/mysql-init.d monasca/mysql-init:latest

[1]: https://github.com/hpcloud-mon/monasca-docker/blob/master/mysql-init/
[2]: https://github.com/hpcloud-mon/monasca-docker/blob/master/mysql-init/Dockerfile
[3]: https://github.com/hpcloud-mon/monasca-docker/
[4]: https://github.com/hpcloud-mon/monasca-docker/blob/master/k8s/
[5]: https://kubernetes.io/docs/user-guide/jobs/
