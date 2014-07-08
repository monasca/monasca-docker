Dockerfiles for building Monasca Images as well as [fig](http://orchardup.github.io/fig/index.html) config for running the cluster.
These images are intended for development.

Fig is used to simplify the start up of the entire cluster with proper links between different vms, it is not used in building the images.

To run install fig, `pip install fig` then just run it `fig up`.

# Development Workflows

# Building Docker Images
The majority of the installation work is done via chef-solo leveraging the same cookbooks used for vagrant and test baremetal setups.
The actual building of images is done with standard docker commands leveraging the various Dockerfiles.

## Details
- The base image used Ubuntu 14.04 with a modern chef and berksfile installed, largely copied from similar 12.04 images.
- Each Docker container has its own git repo as is standard practice for Docker, allowing automated verified builds.
- The databases are setup within the image and are not setup to use a Docker volume, this is the easier setup for dev.

### Working with web proxies

!! This isn't quite working yet
When working with a proxy you can set the proxy information for docker but they will persist making things difficult when no proxy is used.
An alternative is to setup this [transparent proxy](https://registry.hub.docker.com/u/jpetazzo/squid-in-a-can/). To use this follow the instructions
given and then modify /etc/squid3/squid.conf with a line like `cache_peer web-proxy.fc.hp.com parent 8080 0 no-digest` then start squid
`squid3 -N` and detach.
`iptables -t nat -I PREROUTING 1 -p tcp --dport 80 -j REDIRECT --to 3129`
