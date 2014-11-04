# Monasca Docker
This repo contains Dockerfiles for building Monasca Images as well as [Ansible](http://www.ansible.com) config for running all the services.
At this time each service is setup standalone and there is no HA. These images are currently intended for development or for use as mini-mon,
a system that monitors the full Monasca monitoring stack and avoids dependency loops in the even of a catastrophic error.

Ansible is used to simplify the start up of the entire cluster because its Docker plugin allows for easy setup with proper links between different containers.
To install Ansible, `pip install ansible` also add the python docker client library `pip install docker-py`

# Playbooks

Run the playbook to start Monasca up `ansible-playbook -i hosts mini-mon.yml`.
Stop and/or delete with the stopped and absent actions `ansible-playbook -i hosts mini-mon.yml --extra-vars "action=absent"`
If the DOCKER_HOST environment variable is not defined you will need to define it as the default is not currently working.

The agent container can be attached to, `docker attach agent`, this will drop you to a shell from which you can run the smoke test `python /tests/smoke.py`.

# Building Docker Images
The majority of the installation work is done via Ansible leveraging the same roles used for the
[monasca-vagrant](https://github.com/stackforge/monasca-vagrant) development environment.
The actual building of images is done with standard docker commands leveraging the various Dockerfiles, for example:

    cd influxdb
    docker build -t monasca/influxdb .


## Details
- The base image used Ubuntu 14.04.

# Todo
- Many containers should be changed to log to console rather than a log file
  - notification
  - persister
  - Probably others
- A number of containers start up mulitple processes and have sleeps in the startup scripts so dependencies are up in time. It would be much nicer
  to be smart about these waits.
  - kafka
  - notification
  - thresh
- I need to open up the various admin ports for the services.
- Automated builds for the containers could be a big advantage and in that case each image should have its own git repo.

# Known Issues
- If DOCKER_HOST is not set the docker_url in the ansible playbook does not properly fall back to the default.
