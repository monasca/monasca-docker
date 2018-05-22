# monasca-docker

This repository contains resources for building and deploying a
full Monasca stack in Docker and Kubernetes environments.

## Quick Start

To quickly get a Monasca environment running, you can use
[docker-compose][1]:

```sh
$ docker-compose up
```

or, if you want to deploy **log pipeline** as well:

```sh
$ docker-compose -f log-pipeline.yml -f docker-compose.yml up
```

For more details about the services that are available after
either of the aforementioned commands can be found
[here](./pipelines.md).

## Content

* [Repository layout](./repo_layout.md)
* [Requirements](./requirements.md)
* * [Host configuration for Elasticsearch](./elasticsearch.md)
* [Start&Stop](./start_stop.md)
* [Pipelines](./pipelines.md)
* [Using external components](./external_cmps.md)
* [.env](./env.md)
* [Tips & Tricks](./tips_and_tricks.md)
* [Contribution Guide](../CONTRIBUTING.md)

[1]: https://docs.docker.com/compose/
