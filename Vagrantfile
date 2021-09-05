# This file can be used to simulate Travis VM locally using Vagrant
# It requires the vagrant-docker-compose plugin that can be installed with:
# $ vagrant plugin install vagrant-docker-compose 

# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  # config.vm.box = "ubuntu/bionic64" #10GB
  config.vm.box = "bento/ubuntu-18.04"
  config.vm.hostname = "monasca"
  # access a port on your host machine (via localhost) and have all data forwarded to a port on the guest machine.
  config.vm.network "forwarded_port", guest: 9092, host: 9092
  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.188.110"

  config.vm.provider "virtualbox" do |vb|
    vb.name = 'Monasca'
    vb.memory = 8200
    vb.cpus = 2
    #vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    #vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  # set up Docker in the new VM:
  config.vm.provision :docker
  config.vm.provision :docker_compose

  config.vm.provision "shell", privileged: false, inline: <<-SHELL
    # sudo apt-get update
    # sudo apt-get -y upgrade
    sudo apt install -y python-pip
    sudo pip install pip --upgrade
    sudo pip install git+https://github.com/monasca/dbuild.git
    sudo pip install "six>=1.13.0"
    sudo apt-get -y install git
    # Change to the branch you want to test
    git clone https://github.com/monasca/monasca-docker.git -b master
    cd monasca-docker
    export CI_EVENT_TYPE="pull_request"
    # Choose the pipeline you want to test (metrics XOR logs):
    python ci.py --pipeline metrics --verbose
    # python ci.py --pipeline logs --verbose
  SHELL

end
