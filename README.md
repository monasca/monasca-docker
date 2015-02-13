# Monasca Docker
This repo contains Dockerfiles for building Monasca Images as well as [Ansible](http://www.ansible.com) config for running all the services.
At this time each service is setup standalone and there is no HA. These images are currently intended for development or for use as mini-mon,
a system that monitors the full Monasca monitoring stack and avoids dependency loops in the even of a catastrophic error.

Ansible is used to simplify the start up of the entire cluster because its Docker plugin allows for easy setup with proper links between different containers.
To install Ansible, `pip install ansible` also add the python docker client library `pip install docker-py`

# Playbooks
To run the playbook an inventory file must exist with the mini-mon host group.

Run the playbook to start Monasca up `ansible-playbook -i hosts mini-mon.yml`.
Stop and/or delete with the stopped and absent actions `ansible-playbook -i hosts mini-mon.yml --extra-vars "action=absent"`
By default the tag for each image will be latest but in many cases it is useful to tag specifically in those cases set the variables of the form
`<name>_tag`, ie influxdb_tag.

# Building Docker Images
The majority of the installation work is done via Ansible leveraging the same roles used for the
[monasca-vagrant](https://github.com/stackforge/monasca-vagrant) development environment.
The actual building of images is done with standard docker commands leveraging the various Dockerfiles, for example:

    cd influxdb
    docker build -t monasca/influxdb .

In many cases custom settings are desired rather than relying on insecure defaults. In particular in many cases an existing keystone
is used so at the least the keystone related variables must be set:
- keystone_url 
- keystone_admin 
- keystone_admin_password 
- keystone_agent_user
- keystone_agent_password
- keystone_agent_project

If using a truststore with the api not only must the monasca_api_truststore variable be set but the truststore itself must be in the api
directory called 'truststore.jks'. Of course any other variables used by the roles which build Monasca can also be set.

To create images specifying custom variables create a host_vars/localhost variables file in the directory before running the docker build command.
Any variables which override those in the site.yml will need to be removed from the site.yml.

## Updating Images
Until Ansible 1.8 (1.7 is latest release as of this writing) there is no support in the Ansible playbook for a custom registry. As a result
updating images must be done by hand either using a custom registry or via a docker save/scp/docker load process.

## Image details
- The base image used Ubuntu 14.04.

# Todo
- For the monasca/openstack image
  - Add in the agent to this box.
  - Add in other services beside just horizon and keystone
- Fix the variable loading order so you don't have to modify site.yml to set vars
- I need to open up the various admin ports for the services.
- In Ansible 1.8 it will begin to support a custom registry, add support to my playbook.
  - When a custom registry is supported also add to the existing playbook or make a new playbook to enable updating of the image and restarting.
- A number of containers start up mulitple processes and have sleeps in the startup scripts so dependencies are up in time. It would be much nicer
  to be smart about these waits.
  - kafka
  - notification
  - thresh
- Many containers should be changed to log to console rather than a log file
  - notification
  - persister
  - Probably others
- There is a standalone keystone image in this repo but no good way to set it up at this point. Add a playbook for this.
- The stateful containers could have an option to connect to external storage.
