# Monasca Demo Image

This is configuration for building the one Monasca container to rule them all, it contains all dependencies and services of Monasca
in a single container. The latest build is available on the public docker registry so you can simply download it but if you wish to build
you do so by running `docker build -t monasca/demo .`

You can run with the command `docker run -p 80:80 -p 8080:8080 -p 5000:5000  --name monasca monasca/demo`

## Using the Monasca cli
The [Monasca cli](https://github.com/stackforge/python-monascaclient) is in the container and so from a shell in the container you can run `. /setup/env.sh` then run monasca cli commands.
