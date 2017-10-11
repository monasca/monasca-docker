Kibana 4 with monasca-kibana-plugin
===================================

Image extends official [Kibana image][1] with [monasca-kibana-plugin][2].
For more details about the aformentioned plugin, please visit plugin's
[repository][2].

Tags
----

Tags in this image match tags in the official [Kibana image][1]. 
This is dictated by the fact that plugin should be build for specific
Kibana version. Each tag includes also ``KIBANA_PLUGIN_BRANCH`` information
detail. Final tag is represented as ``{KIBANA_VERSION}-{KIBANA_PLUGIN_BRANCH}``.
That said, tagging presents as follows:

* `4.6.3-master` [`4.6-master`, `4-master`] - corresponds to **Kibana 4.6.3**
  [monasca-kibana-plugin][2] build from **master** branch.

Configuration
-------------

| Variable                       |   Default       | Description                       |
|--------------------------------|-----------------|-----------------------------------|
| `KEYSTONE_URI`                 | `keystone:5000` | An URI to Keystone Admin Endpoint |
| `MONASCA_PLUGIN_ENABLED`       | `False`         | Should the plugin be enabled or disabled |
| `ELASTIC_SEARCH_URL`           | `elasticsearch:9200` | An URL to Elasticsearch container |
| `BASE_PATH`                    | `unset`              | Path to mount Kibana at if you are running behind a proxy |

Usage
-----

To use this image, first you need to deploy [ElasticSearch][3] and [Keystone][4].

    Keystone is required only if ``MONASCA_PLUGIN_ENABLED`` 
    is set to ``True``

Once prerequisites are met, image can ba launched, for example, with:
```docker run -it --rm -l elasticsearch monasca/kibana:4.6.3-master``` 

[1]: https://hub.docker.com/r/library/kibana 
[2]: https://github.com/openstack/monasca-kibana-plugin
[3]: https://hub.docker.com/r/library/elasticsearch
[4]: https://github.com/monasca/monasca-docker/keystone
