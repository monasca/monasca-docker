# Monasca Docker
This repo contains Dockerfiles for building Monasca Images. The images are used for demos or development and experimentation. The monasca/demo
image runs all of the various daemons for Monasca and is a great place to start as well as use for demos.

To run the demo simply setup Docker then run, `docker run -d -p 80:80 -p 8080:8080 -p 5000:5000  --name monasca monasca/demo`. The ui will be accessible on the docker host at port 80 the api at port 8080.

The rest of the images here are the individual daemons for Monasca split into their own containers. This is really intended for testing and
development at this point. The repo also contains an [Ansible](http://www.ansible.com) playbook to help run all the individual containers as one whole.

Ansible is used to simplify the start up of the entire service because its Docker plugin allows for easy setup with proper links between different containers.
To install Ansible, `pip install ansible` also add the python docker client library `pip install docker-py`

# Playbooks
Run the playbook to start Monasca up `ansible-playbook -i hosts -c local mini-mon.yml`.
If you want to run on a remote hosts edit the file `hosts` and remove the `-c local` from the command.

Stop and/or delete with the stopped and absent actions `ansible-playbook -i hosts -c local mini-mon.yml --extra-vars "action=absent"`

By default the tag for each image will be latest but in many cases it is useful to tag specifically in those cases set the variables of the form
`<name>_tag`, ie influxdb_tag.

# Building Docker Images
The majority of the installation work is done via Ansible leveraging the same roles used for the
[monasca-vagrant](https://github.com/stackforge/monasca-vagrant) development environment.
The actual building of images is done with standard docker commands leveraging the various Dockerfiles, for example:

    cd influxdb
    docker build -t monasca/influxdb .

# Todo
- Grafana uses the registered endpoint in keystone for a connection to the monasca api. This registered endpoint is the ip of the api box which works
  for all the docker images that can reach that ip but not for any web browser which can't. I can manually change the endpoint to a reachable ip to
  fix grafana but this tends to break the horizon portions.
- For the monasca/openstack image
  - Add in the agent to this box.
  - Add in other services beside just horizon and keystone
- I need to open up the various admin ports for the services.
- A number of containers start up mulitple processes and have sleeps in the startup scripts so dependencies are up in time. It would be much nicer
  to be smart about these waits.
  - kafka
  - notification
  - thresh
- Many containers should be changed to log to console rather than a log file
  - notification
  - persister
  - Probably others
- The stateful containers could have an option to connect to external storage.
- For some reason the agent is configured for postfix even when it isn't installed? This doesn't happen on devstack which also
  doesn't have postfix so I am unsure of the cause.
