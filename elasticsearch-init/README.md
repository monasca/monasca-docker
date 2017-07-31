elasticsearch-init
==================

A container for loading the templates to ElasticSearch.

Usage
-----

TBD (need to tweak image first)

Configuration
-------------

A number of environment variables can be passed to the container:

| Variable                  | Default      | Description                       |
|---------------------------|--------------|-----------------------------------|
| `ELASTICSEARCH_URI`       | `elasticsearch:9200` | URI to connect to ES      |
| `ELASTICSEARCH_TIMEOUT`   | `60`         | How long to wait for ElasticSearch connection |


