# Standalone Monasca


This repository contains a Docker Compose configuration for running 
a standalone Monasca and its required components in containers. Stability and repeatability is important, so
The goal is component versions should declared if possible, instead of `latest`.
Typical use case is demo.  

## Tags

Tags can be set in .env file.

## Usage

### First-time run

At the first time, initializer containers must be run, too.
Example command for running all initializer containers with all services:

`docker-compose --file docker-compose.yml --file compose-init.yml up`

This command builds and run initializer containers and all of components.
Initializer containers will exit automatically. See more details in [docker-compose up][1].

For debugging purposes, pulling, building and running can be executed separated.
Below script creates separated GNOME Terminal tab for each pulling and building of services:

`./build-all_gnome-terminal.sh`

Press any key if all of images already pulled, in order to start building.
Below messages may not be error:
* `ERROR: manifest for <service image> not found`
* `<service> uses an image, skipping`

Initializer containers must be run only once. Example for running initializer containers, including its dependencies:

`docker-compose --file docker-compose.yml --file compose-init.yml up mysql-init influxdb-init`

After exit of initializer containers, stop all containers, for example:

`docker-compose stop`

Below script creates separated GNOME Terminal tab for each service up:

`./up-all_gnome-terminal.sh`


### Stop

Default services can be stopped by below command:

`docker-compose stop`

Example command for stopping optional services (for example: initializer containers):

`docker-compose --file docker-compose.yml --file compose-init.yml stop`

See more details in [docker-compose stop][2].

### Start

In case of all containers stopped, the simplest command for starting all default services is:

`docker-compose up`

Starting only one or a few containers can be by below command:

`docker-compose start <service>...`

See more details in [docker-compose start][3].

For debugging purposes, below script creates separated GNOME Terminal tab for each service up:

`./up-all_gnome-terminal.sh`

This script uses `up` command, so all of containers must be stopped before executing the script.


### Down

Below command stops and removes containers and images:

`docker-compose --file docker-compose.yml --file compose-init.yml down -v`

## Configuration

More compose files can be specified to `docker-compose`, which combines them into a single configuration.
Using alternate compose files is a good idea for keeping related service configuration of different use cases in sync. 
See more details in [Overview of docker-compose CLI][4]. 

Another preferred way for using different configuration is editing `.env` file or setting environment variables.
See more details in [https://docs.docker.com/compose/env-file/][5]

### Official Grafana

Official Grafana service name is `grafana-official`. It has limitations to Monasca Keystone authentications, moreover,
Monasca datasource plugin must be installed manually by below command:
```
docker-compose exec grafana-official /bin/bash
grafana-cli plugins install monasca-datasource
exit
```
Influx database can be accessed directly by using InfluxDB datasource.
See default values for Grafana datasource options:

| Option   | Value                 |
|----------|-----------------------|
| Url      | http://localhost:8086 |
| Access   | direct                |
| Database | mon                   |
| User     | mon_persister         |
| Password | password              |

Values are declared in [`monasca-persister-python`](../monasca-persister-python/README.md)

## TODO

[1]: https://docs.docker.com/compose/reference/up/
[2]: https://docs.docker.com/compose/reference/stop/
[3]: https://docs.docker.com/compose/reference/start/
[4]: https://docs.docker.com/compose/reference/overview/
[5]: https://docs.docker.com/compose/env-file/
