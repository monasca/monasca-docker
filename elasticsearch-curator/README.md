elasticsearch-curator
=====================

This image provide data retention possibilities for Elasticsearch.

Sources: [elasticsearch-curator][es-cur] &middot; [Dockerfile][es-cur-df] &middot; [monasca-docker][monasca-docker]

Tags
----

Images in this repository are tagged as follows:

 * `latest`: refers to the latest stable point release, e.g. `1.0.0`
 * `4.3.1-1.0.0`: a.k.a. `[elasticsearch-curator version]-[image version]`.
   In this case the image revision `1.0.0` has been built from a snapshot
   of Elasticsearch Curator `4.3.1`

Usage
-----

This image requires access to a running Elasticsearch instance.

If needed, connection parameters can be provided via environment variables as
described below.

Example of configuration for Docker Compose:
```yaml
elasticsearch-curator:
  image: monasca/elasticsearch-curator:4.3.1-1.0.0
  environment:
    LOGSTASH_FIELDS: "service=elasticsearch-curator"
  volumes:
    - ./elasticsearch-curator/actions.yml:/actions.yml
  depends_on:
    - elasticsearch
```


Configuration
-------------

|      Variable       |       Default        |         Description         |
|---------------------|----------------------|-----------------------------|
| `ELASTICSEARCH_URI` | `elasticsearch:9200` | URI to connect to ES        |
| `CURATOR_LOG_LEVEL` | `INFO`               | Curator log level           |
| `CURATOR_CRON`      | `0 0 * * *`          | Cron run time configuration |

By default Elasticsearch Curator is running thanks to cron every day
at 12 a.m.. You could get more information how to set it to different time
at <http://corntab.com>.


Actions configuration
---------------------

A single file, `/actions.yml`, should be mounted into the container to provide
actions configuration. In the default configuration file indices older
than 60 days are removed, to have custom configuration you need to override
`/actions.yml` for this container.

You are able to configure Elasticsearch Curator to delete oldest data
by `age` or `space`. You can also have more than one action at once:

```yaml
curator_actions:
  - {
      delete_by: age,
      description: 'Delete indices older than 60 days',
      deleted_days: 60,
      disable: False
    }
  - {
      delete_by: space,
      description: 'Delete oldest indices over 3 GB',
      deleted_space: 3,
      disable: False
    }
```
`deleted_space` could contain number smaller than `1`, like `0.05`.
If you want to disable some action from running simply set `disable`
to `True`.

You can exclude specific index from processing with `curator_excluded_index`:

```yaml
curator_excluded_index:
  - {
      index_name: .kibana,
      exclude: True
    }
```


[es-cur]: https://github.com/monasca/monasca-docker/blob/master/elasticsearch-curator/
[es-cur-df]: https://github.com/monasca/monasca-docker/blob/master/elasticsearch-curator/Dockerfile
[monasca-docker]: https://github.com/monasca/monasca-docker/
