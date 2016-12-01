Build docker image:
under root, run:
root@devstack:/vagrant_home/python_repos/monasca-docker/webapp_demo#
docker build -t django_docker /vagrant_home/python_repos/monasca-docker/webapp_demo/

Run docker image:
root@devstack:/vagrant_home/python_repos/monasca-docker/webapp_demo#
docker run -iti -p 8000:8000 -p 8005:8005 django_docker
