# The purpose of this image is to mimic the environment we will install in while retaining some of the advantages of Docker.
# Without a docker infrastructure in production installation is done to VMs or baremetal, this container acts like a freshly made vm with ssh and systemd.
# The big catch is that this container will only run a host that itself runs systemd this is because of the need to have the proper cgroups setup.
#
# The systemd work in a container was largely copied from https://github.com/maci0/docker-systemd-unpriv/blob/master/Dockerfile
#
# To run specify the cgroup mount point 'docker run -d -v /sys/fs/cgroup:/sys/fs/cgroup:ro --name ci-base monasca/ci-base'
#
# Known Issue:
#   - On initial run there are problems with systemd fulling coming up and no error output
#   - dbus does not start up correctly when running '/bin/systemd --system' after the container comes up with a shell as the initial command. ssh is fine

FROM debian:stable
MAINTAINER Tim Kuhlman <tim.kuhlman@hp.com>

USER root

RUN systemctl mask dev-mqueue.mount dev-hugepages.mount \
    systemd-remount-fs.service sys-kernel-config.mount \
    sys-kernel-debug.mount sys-fs-fuse-connections.mount
RUN systemctl mask display-manager.service systemd-logind.service
RUN systemctl disable graphical.target

# Install ssh, volume mounting or docker exec should be used to setup a authorized ssh key for root
RUN apt-get update
RUN apt-get install -y dbus openssh-server

ADD dbus.service /etc/systemd/system/dbus.service

VOLUME ["/sys/fs/cgroup"]

CMD ["/bin/systemd"]
