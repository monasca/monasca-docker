elasticsearch-init
==================

A container for loading the templates to ElasticSearch.

Tags
----

**elasticsearch-init** uses simple [SemVer][3] tags as follows:

* `0.0.1` - `latest`

Usage
-----

**elasticsearch-init** leverages the [Docker volumes][1]. Each template,
that image is supposed to upload to [ElasticSearch][2], is represented as single file
mounted to ```/templates/``` directory inside the container.
Another point, to keep in mind, is that template uploading requires also a **template name**.
That bit is equal to the filename that holds the template. For instance:

```docker run -v ./tpls/logs.json:/templates/logs -l elasticsearch monasca/elasticsearch-init```

means that:

* content of ```/template/logs``` will be uploaded to [ElasticSearch][2]
* template name will be ```logs```

Configuration
-------------

A number of environment variables can be passed to the container:

| Variable                  | Default      | Description                       |
|---------------------------|--------------|-----------------------------------|
| `ELASTICSEARCH_URI`       | `elasticsearch:9200` | URI to connect to ES      |
| `ELASTICSEARCH_TIMEOUT`   | `60`         | How long to wait for ElasticSearch connection |

[1]: https://docs.docker.com/engine/tutorials/dockervolumes/
[2]: https://hub.docker.com/_/elasticsearch/
[3]: http://semver.org/
