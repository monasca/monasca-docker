Dockerfiles for building Monasca Images as well as [fig](http://orchardup.github.io/fig/index.html) config for running the cluster.
These images are intended for development.

Fig is used to simplify the start up of the entire cluster with proper links between different vms, it is not used in building the images.

To run install fig, `pip install fig` then just run it `fig up`.

# Development/Test Workflows
`TODO`

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
- Setup the ui
- Many containers should be changed to log to console rather than a log file
  - notification
  - persister
- Automated builds for the containers could be a big advantage and in that case each image should have its own git repo.
- Setup clustered versions of the various containers. This will mean a custom zookeeper.
