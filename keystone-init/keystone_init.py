#!/usr/bin/env python

# (C) Copyright 2017 Hewlett Packard Enterprise Development LP
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

import base64
import logging
import os
import random
import string
import time

from collections import defaultdict
from itertools import ifilter

import yaml

from keystoneauth1.exceptions import RetriableConnectionFailure
from keystoneauth1.identity import Password
from keystoneauth1.session import Session
from keystoneclient.discover import Discover
from requests import HTTPError
from requests import RequestException

from kubernetes import KubernetesAPIClient

PASSWORD_CHARACTERS = string.ascii_letters + string.digits
KEYSTONE_PASSWORD_ARGS = [
    'auth_url', 'username', 'password', 'user_id', 'user_domain_id',
    'user_domain_name', 'project_id', 'project_name', 'project_domain_id',
    'project_domain_name', 'tenant_id', 'tenant_name', 'domain_id',
    'domain_name', 'trust_id', 'default_domain_id', 'default_domain_name'
]
KEYSTONE_TIMEOUT = int(os.environ.get('KEYSTONE_TIMEOUT', '10'))
KEYSTONE_VERIFY = os.environ.get('KEYSTONE_VERIFY', 'true') == 'true'
KEYSTONE_CERT = os.environ.get('KEYSTONE_CERT', None)

PRELOAD_PATH = os.environ.get('PRELOAD_PATH', '/preload.yml')
NAMESPACE_FILE = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'

LOG_LEVEL = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

_domain_cache = []
_project_cache = defaultdict(lambda: [])
_role_cache = defaultdict(lambda: [])

_kubernetes_client = None


def first(condition, seq):
    try:
        return next(ifilter(condition, seq))
    except StopIteration:
        return None


class KeystoneInitException(Exception):
    pass


def retry(retries=5, delay=2.0,
          exc_types=(RetriableConnectionFailure, RequestException)):

    def decorator(func):
        def f_retry(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exc_types as exc:
                    if i < retries - 1:
                        logger.debug('Caught exception, retrying...',
                                     exc_info=True)
                        time.sleep(delay)
                    else:
                        logger.exception('Failed after %d attempts', retries)
                        if isinstance(exc, RequestException):
                            logger.debug('Response was: %r', exc.response.text)

                        raise
        return f_retry
    return decorator


def get_current_namespace():
    if 'NAMESPACE' in os.environ:
        return os.environ['NAMESPACE']

    if os.path.exists(NAMESPACE_FILE):
        with open(NAMESPACE_FILE, 'r') as f:
            return f.read()

    logger.warn('Not running in cluster and $NAMESPACE is not set, assuming '
                '\'default\'!')
    return 'default'


def get_kubernetes_client():
    global _kubernetes_client

    if _kubernetes_client is None:
        _kubernetes_client = KubernetesAPIClient()
        _kubernetes_client.load_auto_config()

    return _kubernetes_client


def generate_password(length=16):
    r = random.SystemRandom()
    return ''.join(r.choice(PASSWORD_CHARACTERS) for _ in range(length))


def keystone_args_from_env():
    ret = {}
    for arg in KEYSTONE_PASSWORD_ARGS:
        ret[arg] = os.environ.get('OS_{}'.format(arg.upper()))

    return ret


@retry()
def get_keystone_client():
    auth = Password(**keystone_args_from_env())
    session = Session(auth=auth,
                      app_name='keystone-init',
                      user_agent='keystone-init',
                      timeout=KEYSTONE_TIMEOUT,
                      verify=KEYSTONE_VERIFY,
                      cert=KEYSTONE_CERT)

    discover = Discover(session=session)
    return discover.create_client()


@retry()
def get_or_create_domain(client, name=None):
    """

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param name:
    :return: the Domain instance
    :rtype: keystoneclient.v3.domains.Domain
    """
    # default domain should always exist
    if name is None:
        return client.domains.get('default')

    if not _domain_cache:
        _domain_cache.extend(client.domains.list())

    domain = first(lambda d: d.name == name, _domain_cache)
    if domain:
        logging.info('found existing domain: %s', domain.name)
    else:
        logging.info('creating domain: %s', name)
        domain = client.domains.create(name)
        _domain_cache.append(domain)
        logging.debug('created domain: %s', domain.name)

    return domain


def get_keystone_admin_url(client, domain):
    """
    :type client: keystoneclient.v3.client.Client
    :type domain: keystoneclient.v3.domains.Domain
    :rtype: str or None
    """
    if 'OS_ADMIN_URL' in os.environ:
        return os.environ['OS_ADMIN_URL']

    try:
        keystone_service = client.services.list(type='identity')[0]
        endpoints = client.endpoints.list(domain=domain,
                                          service=keystone_service,
                                          interface='admin')
        return endpoints[0].url
    except IndexError:
        logging.warn('failed to detect keystone admin URL!', exc_info=True)
        return None


@retry()
def get_or_create_project(client, domain, name):
    """

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param domain:
    :type domain: keystoneclient.v3.domains.Domain
    :param name: the name of the project
    :return: the Project instance
    :rtype: keystoneclient.v3.projects.Project
    """

    cache = _project_cache[domain.id]
    if not cache:
        cache.extend(client.projects.list(domain=domain))

    project = first(lambda p: p.name == name, cache)
    if project:
        logging.info('found existing project: %s', project.name)
    else:
        logging.info('creating project: %s', name)
        project = client.projects.create(name, domain)
        cache.append(project)
        logging.debug('created project: %r', project)

    return project


@retry()
def get_or_create_role(client, domain, name):
    """

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param domain: domain when creating a role, None if global
    :type domain: keystoneclient.v3.domains.Domain
    :param name:
    :return:
    :rtype: keystoneclient.v3.roles.Role
    """
    cache = _role_cache[domain.id]
    if not cache:
        # two special roles can exist in the None domain, so use them when
        # they exist
        cache.extend(client.roles.list(domain_id=None, name='admin'))
        cache.extend(client.roles.list(domain_id=None, name='_member_'))

        # NOTE: client.roles.list() does NOT function like
        # client.projects.list()! passing `domain=` does not work,
        # `domain_id=` must be used explicitly
        cache.extend(client.roles.list(domain_id=domain.id))

    role = first(lambda r: r.name == name, cache)
    if role:
        logging.info('found existing role: %s', role.name)
    else:
        logging.info('creating role: %s', name)
        role = client.roles.create(name, domain)
        cache.append(role)
        logging.debug('created role: %r', role)

    return role


@retry()
def get_user(client, domain, name):
    """

    :type client: keystoneclient.v3.client.Client
    :type domain: keystoneclient.v3.domains.Domain
    :type name: str
    :return:
    :rtype: keystoneclient.v3.users.User
    """
    # don't really need to cache users since we only touch each user once
    return first(lambda u: u.name == name, client.users.list(domain=domain))


@retry()
def create_user(client, username, **kwargs):
    """

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param username:
    :return:
    :rtype: keystoneclient.v3.users.User
    """
    user = client.users.create(username, **kwargs)
    logging.info("created user %s", username)

    return user


@retry()
def update_user(client, user, **kwargs):
    """

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param user:
    :type user: keystoneclient.v3.users.User
    :return:
    """
    user = client.users.update(user, **kwargs)
    logging.info('updated user %s', user.name)


@retry()
def get_role_assignments(client, user, project):
    """

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param user:
    :type user: keystoneclient.v3.users.User
    :param project:
    :type project: keystoneclient.v3.projects.Project
    :return:
    """
    return client.role_assignments.list(user=user, project=project)


@retry()
def grant_role(client, role_id, user, project):
    """

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param role_id:
    :type role_id: str
    :param user:
    :type user: keystoneclient.v3.users.User
    :param project:
    :type project: keystoneclient.v3.projects.Project
    :return:
    """
    client.roles.grant(role_id, user=user, project=project)


@retry()
def ensure_kubernetes_namespace(client, namespace):
    """

    :type client: kubernetes.KubernetesAPIClient
    :type namespace: str
    :return:
    """
    try:
        client.get('/api/v1/namespaces/{}', namespace)
    except HTTPError as e:
        if e.response.status_code == 404:
            logging.info('creating namespace: %s', namespace)
            client.post('/api/v1/namespaces', json={
                'apiVersion': 'v1',
                'kind': 'Namespace',
                'metadata': {
                    'name': namespace
                }
            })


@retry()
def get_kubernetes_secret(client, name, namespace=None):
    """

    :param client:
    :type client: kubernetes.KubernetesAPIClient
    :param name:
    :param namespace: namespace, auto if None
    :return: loaded secret dict or None if it does not exist
    """
    if namespace is None:
        namespace = get_current_namespace()

    try:
        return client.get('/api/v1/namespaces/{}/secrets/{}', namespace, name)
    except HTTPError as e:
        if e.response.status_code != 404:
            raise

        return None


def create_kubernetes_secret(client, fields, name, namespace=None):
    """

    :param client:
    :type client: kubernetes.KubernetesAPIClient
    :param fields:
    :type fields: dict[str, str]
    :param name:
    :param namespace: namespace, auto if None
    :return:
    """
    if namespace is None:
        namespace = get_current_namespace()

    ensure_kubernetes_namespace(client, namespace)

    encoded = {k: base64.b64encode(v) for k, v in fields.iteritems()}
    secret = {
        'kind': 'Secret',
        'apiVersion': 'v1',
        'type': 'Opaque',
        'metadata': {
            'name': name,
            'namespace': namespace,
            'labels': {
                'heritage': 'keystone-init-job'
            }
        },
        'data': encoded
    }

    logging.info('creating secret "%s" in namespace "%s"', name, namespace)
    return client.post('/api/v1/namespaces/{}/secrets',
                       namespace, json=secret)


def parse_secret(secret):
    if isinstance(secret, basestring):
        if '/' in secret:
            namespace, name = secret.split('/', 1)
            return namespace, name
        else:
            return None, secret

    return secret['namespace'], secret['name']


def load_domains(ks, domains):
    """

    :param ks:
    :type ks: keystoneclient.v3.client.Client
    :param domains:
    :type domains: dict[str, dict[str, list]]
    :return:
    """

    for name, options in domains.iteritems():
        domain = get_or_create_domain(ks, None if name == 'default' else name)
        admin_url = get_keystone_admin_url(ks, domain)

        logging.info('creating projects...')
        for project in options.get('projects', []):
            get_or_create_project(ks, domain, project)

        logging.info('creating roles...')
        for role in options.get('roles', []):
            get_or_create_role(ks, domain, role)

        logging.info('creating users...')
        for user_cfg in options.get('users', []):
            assert isinstance(user_cfg, dict)

            username = user_cfg.get('username')
            user = get_user(ks, domain, username)

            if 'project' in user_cfg:
                # currently assuming all valid projects are at least
                # referenced in `projects` block
                project = get_or_create_project(ks, domain, user_cfg['project'])
            else:
                project = None

            if user:
                if hasattr(user, 'project_id') \
                        and project is not None \
                        and project.id == user.project_id:
                    update_user(ks, user, project_id=project.id)

                    logger.info('reassigned user %s to project %s',
                                user.name, project.name)
            else:
                password = user_cfg.get('password', generate_password())
                email = user_cfg.get('email', None)

                if 'secret' in user_cfg:
                    s_namespace, s_name = parse_secret(user_cfg['secret'])

                    k8s = get_kubernetes_client()
                    secret = get_kubernetes_secret(k8s, s_name, s_namespace)
                    if secret:
                        # TODO use password from secret instead? overwrite?
                        pass
                    else:
                        fields = {
                            'OS_USERNAME': username,
                            'OS_PASSWORD': password,
                            'OS_AUTH_URL': ks.session.auth.auth_url,
                            'OS_USER_DOMAIN_NAME': domain.name
                        }

                        if admin_url:
                            fields.update({'OS_ADMIN_URL': admin_url})

                        if project:
                            fields.update({
                                'OS_PROJECT_NAME': project.name,
                                'OS_PROJECT_DOMAIN_NAME': domain.name,
                            })

                        create_kubernetes_secret(k8s, fields, s_name, s_namespace)
                        logging.info('created kubernetes secret: %s/%s',
                                     s_name, s_namespace)

                # project is supposedly deprecated in favor of default_project
                # ... but we'll use it anyway
                user = create_user(ks, username,
                                   domain=domain, password=password,
                                   email=email, project=project)

            current_roles = get_role_assignments(ks, user, project)
            current_ids = set(map(lambda a: a.role['id'], current_roles))

            desired_role_names = user_cfg.get('roles', [])
            desired_role_names.append('_member_')
            desired_roles = map(lambda n: get_or_create_role(ks, domain, n),
                                desired_role_names)
            desired_ids = set(map(lambda r: r.id, desired_roles))

            # TODO should we remove roles that aren't in the list?

            roles_to_grant = desired_ids - current_ids
            logging.info('granting roles to user: %r', roles_to_grant)
            for role_id in roles_to_grant:
                grant_role(ks, role_id, user, project)

        logging.info('finished initializing domain %s', name)

    logging.info('all domains initialized successfully')


def load_endpoints(ks, endpoints):
    for name, options in endpoints.iteritems():
        # TODO
        pass


def main():
    ks = get_keystone_client()

    with open(PRELOAD_PATH, 'r') as f:
        preload = yaml.safe_load(f)

        if 'domains' in preload:
            load_domains(ks, preload['domains'])

        if 'endpoints' in preload:
            load_endpoints(ks, preload['endpoints'])


if __name__ == '__main__':
    main()
