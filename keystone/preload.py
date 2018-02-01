#!/usr/bin/env python
# coding=utf-8

# (C) Copyright 2015-2017 Hewlett-Packard Enterprise Development LP
# Copyright 2015 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import print_function

import os
import sys
import time
import urlparse

import yaml

from keystoneauth1.exceptions.connection import ConnectFailure
from keystoneauth1.identity import v3
from keystoneauth1 import session as ks_session
from keystoneclient.v3 import client


def _get_auth_plugin(auth_url, **kwargs):
    kwargs = {
        'username': kwargs.get('username'),
        'password': kwargs.get('password'),
        'project_name': kwargs.get('project_name'),
        'project_domain_id': kwargs.get('project_domain_id'),
        'user_domain_id': kwargs.get('user_domain_id'),
    }

    return v3.Password(auth_url=auth_url, **kwargs)


def _retry(func, retries=5, exc=None):
    if exc is None:
        exc = (ConnectFailure,)

    for i in range(retries):
        try:
            return func()
        except exc as e:
            if i < retries - 1:
                time.sleep(1.0)
                continue
            else:
                print("Max retries reached after {:d} attempts: {}"
                      .format(retries, e))
                raise


def get_default_domain(ks_client):
    """Get the default domain"""
    for domain in _retry(lambda: ks_client.domains.list()):
        if domain.id == "default":
            return domain

    return None


def get_project(ks_client, project_name):
    """Get the project by name"""
    for project in _retry(lambda: ks_client.projects.list()):
        if project.name == project_name:
            return project

    return None


def add_projects(ks_client, project_names):
    """Add the given project_names if they don't already exist"""
    default_domain = get_default_domain(ks_client)
    for project_name in project_names:
        if not get_project(ks_client, project_name):
            _retry(lambda: ks_client.projects.create(name=project_name,
                                                     domain=default_domain,
                                                     enabled=True))
            print("Created project '{}'".format(project_name))

    return True


def get_user(ks_client, user_name):
    for user in _retry(lambda: ks_client.users.list()):
        if user.name == user_name:
            return user
    return None


def get_role(ks_client, role_name=None, role_id=None):
    for role in _retry(lambda: ks_client.roles.list()):
        if role.name == role_name or role.id == role_id:
            return role
    return None


def add_users(ks_client, users):
    """Add the given users if they don't already exist"""
    for user in users:
        if not get_user(ks_client, user['username']):
            project_name = user['project']
            project = get_project(ks_client, project_name)

            password = user['password']
            if 'email' in user:
                email = user['email']
            else:
                email = None

            _retry(lambda: ks_client.users.create(name=user['username'],
                                                  password=password,
                                                  email=email,
                                                  project_id=project.id))
            print("Created user '{}'".format(user['username']))
    return True


def add_user_roles(ks_client, users):
    """Add the roles for the users if they don't already have them"""
    for user in users:
        if 'role' not in user:
            continue
        role_name = user['role']
        keystone_user = get_user(ks_client, user['username'])
        project = get_project(ks_client, user['project'])

        assignments = _retry(lambda: ks_client.role_assignments.list(
            user=keystone_user,
            project=project))
        for assignment in assignments:
            role = get_role(ks_client=ks_client, role_id=assignment.role['id'])
            if role.name == role_name:
                return True

        role = get_role(ks_client=ks_client, role_name=role_name)
        if not role:
            role = _retry(lambda: ks_client.roles.create(role_name))
            print("Created role '{}'".format(role_name))

        _retry(lambda: ks_client.roles.grant(user=keystone_user,
                                             role=role,
                                             project=project))
        print("Added role '{}' to user '{}'".format(role_name,
                                                    user['username']))
    return True


def add_service_endpoint(ks_client, name, description, endpoint_type,
                         url, region, interface):
    """Add the Monasca service to the catalog with the specified endpoint,
    if it doesn't yet exist.
    """
    services = _retry(lambda: ks_client.services.list())
    service_names = {service.name: service for service in services}
    if name in service_names.keys():
        service = service_names[name]
    else:
        service = _retry(lambda: ks_client.services.create(
            name=name,
            type=endpoint_type,
            description=description))
        print("Created service '{}' of type '{}'".format(name, endpoint_type))

    for endpoint in _retry(lambda: ks_client.endpoints.list()):
        if endpoint.service_id == service.id:
            if endpoint.url == url:
                if endpoint.interface == interface:
                    return True
            else:
                _retry(lambda: ks_client.endpoints.delete(endpoint))

    _retry(lambda: ks_client.endpoints.create(region=region, service=service,
                                              url=url, interface=interface))

    print("Added service endpoint '{}' at '{}' (interface: '{}') "
          .format(name, url, interface))
    return True


def add_monasca_service():
    return True


def resolve_k8s_service_by_url(url):
    import k8s_get_service
    parsed = urlparse.urlparse(url)
    service = parsed.hostname

    internal_port = parsed.port
    if not internal_port:
        if parsed.scheme == 'http':
            internal_port = 80
        elif parsed.scheme == 'https':
            internal_port = 443

    ip, port = k8s_get_service.resolve_service(service, internal_port)
    netloc = '{}:{}'.format(ip, port)
    modified = list(parsed)
    modified[1] = netloc

    return urlparse.urlunparse(modified)


def main(argv):
    """Get credentials to create a keystoneauth Session to instantiate a
    Keystone Client and then call methods to add users, projects and roles
    """

    path = os.environ.get('PRELOAD_YAML_PATH', '/preload.yml')
    try:
        with open(path, 'r') as pre:
            data = yaml.load(pre)
    except IOError:
        data = {'users': [], 'endpoints': []}
        print('No preload.yml at {}, using default values: {!r}'
              .format(path, data))

    users = data['users']
    url = 'http://localhost:35357/v3'

    # FIXME(clenimar): to date, devstack doesn't set domain-related enviroment
    # variables. That's why we need that little workaround when getting those
    # from sys.argv.
    kwargs = {
        'username': os.environ.get('KEYSTONE_USERNAME', 'admin'),
        'password': os.environ.get('KEYSTONE_PASSWORD', 's3cr3t'),
        'project_name': os.environ.get('KEYSTONE_PROJECT', 'admin'),
        'project_domain_id': 'default',
        'user_domain_id': 'default'
    }

    auth_plugin = _get_auth_plugin(auth_url=url, **kwargs)
    session = _retry(lambda: ks_session.Session(auth=auth_plugin))
    ks_client = _retry(lambda: client.Client(session=session))

    projects = []
    for user in users:
        if 'project' in user and user['project'] not in projects:
            projects.append(user['project'])

    add_projects(ks_client, projects)
    add_users(ks_client, users)
    add_user_roles(ks_client, users)

    do_resolve = os.environ.get('KUBERNETES_RESOLVE_PUBLIC_ENDPOINTS', False)

    for e in data['endpoints']:
        for interface in e['interfaces']:
            if isinstance(interface, (str, unicode)):
                interface_name = interface
                url = e['url']
            else:
                interface_name = interface['name']
                url = interface['url']

                if do_resolve \
                        and 'resolve' in interface \
                        and interface['resolve']:
                    url = resolve_k8s_service_by_url(url)

            add_service_endpoint(ks_client, e['name'], e['description'],
                                 e['type'], url, e['region'],
                                 interface=interface_name)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
