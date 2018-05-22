# Host configuration for Elasticsearch

Even though Elasticsearch is enclosed in Docker container it's still need some
more configuration that Docker is taking from the host.

https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html

https://www.elastic.co/guide/en/elasticsearch/reference/current/system-config.html

### Increase default heap size

By default this repository set heap size for Elasticsearch to 1 GB. This amount
is fine for development but is definitely too small for production use.
Find variable containing `HEAP_SIZE` in configuration file.
Set it to bigger value like `10g`, but don't set it to bigger values than
`31g` (you will find more in deep information how to set this value in
Elasticsearch documentation: [Heap: Sizing and Swapping][heap-size]).

### Increase mmap counts

First search for current limit: `sysctl vm.max_map_count`. If the output
is `262144` or bigger you don't need to change anything. If not, then search
for source of the current limit with:

```
grep -r vm.max_map_count /etc/sysctl.conf /etc/sysctl.d/
```

And update existing entry with `262144`. If no entry was found you can change
this limit with following command:

```
echo "vm.max_map_count=262144" | sudo tee /etc/sysctl.d/60-elasticsearch.conf
```

### Increase ulimits

Also you need to make sure that Docker daemon have increased ulimits
for `nofile` and `nproc`:

```
docker run --rm bash -c 'ulimit -Hn && ulimit -Sn && ulimit -Hu && ulimit -Su'
```

If returned numbers are bigger than `65536` or `unlimited` everything is fine.
In other case you need to increase them for Docker daemon. You can do this
by overwriting some of the variables for Docker service.

Run following command to open editor that will allow you to provide new values
for Docker service and will save it in proper overwrite file:
```
sudo systemctl edit docker
```
Fill it with the following data:
```
[Service]
LimitNOFILE=1048576
LimitNPROC=infinity
LimitCORE=infinity
LimitMEMLOCK=infinity
```

Restart host for this changes to take effect.


[heap-size]: https://www.elastic.co/guide/en/elasticsearch/guide/current/heap-sizing.html
