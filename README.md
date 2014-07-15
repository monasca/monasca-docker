Dockerfiles for building Monasca Images as well as [ansible](http://www.ansible.com) config for running the cluster.
These images are intended for development.

Ansibleis used to simplify the start up of the entire cluster with proper links between different vms, it is not used in building the images.

To run install ansible, `pip install ansible` also add the python docker client library `pip install docker-py`
Run the playbook to start things up `ansible-playbook mini-mon.yml`.
Stop and/or delete with the stopped and absent actions `ansible-playbook mini-mon.yml --extra-vars "action=stopped"`

# Development/Test Workflows
`TODO`

## Tooling
  - [nsenter](https://github.com/jpetazzo/nsenter) allows you to attach to running containers. Docker is working on this functionality natively but isn't there yet.
    - Run like `docker-enter my_container /bin/bash1`

# Building Docker Images
The majority of the installation work is done via chef-solo leveraging the same cookbooks used for vagrant and test baremetal setups.
The actual building of images is done with standard docker commands leveraging the various Dockerfiles.

## Details
- The base image used Ubuntu 14.04 with a modern chef and berksfile installed, largely copied from similar 12.04 images.
- Each Docker container has its own git repo as is standard practice for Docker, allowing automated verified builds.
- The databases are setup within the image and are not setup to use a Docker volume, this is the easier setup for dev.
- The smoke test is in the monasca/agent container
- Currently using a community devstack container and creating the mini-mon keystone user on the agent startup.

# Todo
- Setup a devstack docker image which is all ready to go, the community one just takes to long to get going.
- Setup the ui
- Many containers should be changed to log to console rather than a log file
  - notification
  - persister
- Automated builds for the containers could be a big advantage and in that case each image should have its own git repo.
- Setup clustered versions of the various containers. This will mean a custom zookeeper.

# Known Issues
- If DOCKER_HOST is not set the docker_url does not properly fall back to the default.
