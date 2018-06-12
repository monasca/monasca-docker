#!/usr/bin/env python
# coding=utf-8

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

from keystoneauth1.exceptions import NotFound
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

DEFAULT_MEMBER_ROLE = '_member_'

_domain_cache = []
_global_role_cache = []
_project_cache = defaultdict(lambda: [])
_role_cache = defaultdict(lambda: [])
_group_cache = defaultdict(lambda: [])
_service_cache = []
_endpoint_cache = []

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


@retry(retries=24, delay=5)
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
    """Get domain or create it if it doesn't exist

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
        logger.info('found existing domain: %s', domain.name)
    else:
        logger.info('creating domain: %s', name)
        domain = client.domains.create(name)
        _domain_cache.append(domain)
        logger.debug('created domain: %s', domain.name)

    return domain


def get_keystone_admin_url(client, domain):
    """Get Keystone admin URL

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
        logger.warn('failed to detect keystone admin URL!', exc_info=True)
        return None


@retry()
def get_or_create_project(client, domain, name):
    """Get project or create it if it doesn't exist

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
        logger.info('found existing project: %s', project.name)
    else:
        logger.info('creating project: %s', name)
        project = client.projects.create(name, domain)
        cache.append(project)
        logger.debug('created project: %r', project)

    return project


@retry()
def get_or_create_global_role(client, name):
    """Get global rule or create it if it doesn't exist

    :type client: keystoneclient.v3.client.Client
    :type name: str
    :rtype: keystoneclient.v3.roles.Role
    """
    if not _global_role_cache:
        _global_role_cache.extend(client.roles.list())

    role = first(lambda r: r.name == name, _global_role_cache)
    if role:
        logger.info('found existing global role: %s', role.name)
    else:
        logger.info('creating new global role: %s', name)
        role = client.roles.create(name)
        _global_role_cache.append(role)
        logger.debug('created new global role: %r', role)

    return role


@retry()
def get_or_create_role(client, domain, name):
    """Get role or create it if it doesn't exist

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param domain: domain when creating a role, None if global
    :type domain: keystoneclient.v3.domains.Domain
    :param name: role name
    :type name: str
    :return:
    :rtype: keystoneclient.v3.roles.Role
    """
    if not _global_role_cache:
        _global_role_cache.extend(client.roles.list())

    global_role = first(lambda r: r.name == name, _global_role_cache)
    if global_role:
        logger.info('found existing global role: name=%s id=%s',
                    global_role.name, global_role.id)
        return global_role

    cache = _role_cache[domain.id]
    if not cache:
        # NOTE: client.roles.list() does NOT function like
        # client.projects.list()! passing `domain=` does not work,
        # `domain_id=` must be used explicitly
        cache.extend(client.roles.list(domain_id=domain.id))

    role = first(lambda r: r.name == name, cache)
    if role:
        logger.info('found existing domain-scoped role: role=%s domain=%s',
                    role.name, domain.name)
    else:
        logger.info('creating new domain-scoped role: %s', name)
        role = client.roles.create(name, domain)
        cache.append(role)
        logger.debug('created domain-scoped role: %r', role)

    return role


def get_or_create_group(client, domain, group):
    """Get group or create it if it doesn't exist

    :type client: keystoneclient.v3.client.Client
    :type domain: keystoneclient.v3.domains.Domain
    :type group: str | dict
    :rtype: keystoneclient.v3.groups.Group
    """
    cache = _group_cache[domain.id]
    if not cache:
        cache.extend(client.groups.list())

    if isinstance(group, basestring):
        name = group
        project_roles = []
        domain_roles = []
    else:
        name = group['name']
        project_roles = group.get('project_roles', [])
        domain_roles = group.get('domain_roles', [])

    group = first(lambda g: g.name == name, cache)
    if group:
        logger.info('found existing group %s in domain %s',
                    group.name, domain.name)
    else:
        logger.info('creating new group %s in domain %s', name, domain.name)
        group = client.groups.create(name, domain=domain)
        cache.append(group)
        logger.debug('created group %r', group)

    for project_grant in project_roles:
        project_name = project_grant['project']
        project = get_or_create_project(client, domain, project_name)
        current_project_roles = get_group_project_role_assignments(
            client, group, project
        )
        project_roles_to_grant = _roles_to_grant(
            client, domain,
            current_project_roles,
            project_grant.get('roles', [])
        )
        logger.info('granting project roles to group: '
                    '%r', project_roles_to_grant)
        for role_id in project_roles_to_grant:
            grant_group_project_role(client, role_id, group, project)

    if domain_roles:
        # also add domain roles
        # domain_roles is just a list of role names for now
        # (are cross-domain role assignments even possible?)
        current_domain_roles = get_group_domain_role_assignments(
            client, group, domain
        )

        domain_roles_to_grant = _roles_to_grant(
            client, domain,
            current_domain_roles,
            domain_roles
        )

        logger.info('granting domain roles to group: %r', domain_roles_to_grant)
        for role_id in domain_roles_to_grant:
            grant_group_domain_role(client, role_id, group, domain)

    return group


@retry()
def get_or_create_service(client, name, service_type, description):
    """Get service or create it if doesn't exist.

    :type client: keystoneclient.v3.client.Client
    :type name: str
    :type service_type: str
    :type description: str
    :return:
    :rtype: keystoneclient.v3.services.Service
    """
    if not _service_cache:
        _service_cache.extend(client.services.list())

    service = first(lambda s: s.name == name, _service_cache)
    if service:
        logger.info('found existing service: %s', service.name)
    else:
        logger.info('creating new service %s of %s type', name, service_type)
        service = client.services.create(
            name=name,
            type=service_type,
            description=description,
        )
        _service_cache.append(service)
        logger.debug('created service %r', service)

    return service


@retry()
def get_or_create_endpoint(client, service, url, endpoint):
    """Get endpoint or create it if doesn't exist.

    :type client: keystoneclient.v3.client.Client
    :type service: keystoneclient.v3.services.Service
    :type url: str
    :type endpoint: dict[str, str]
    :return:
    :rtype: keystoneclient.v3.endpoints.Endpoint
    """
    global _endpoint_cache
    if not _endpoint_cache:
        _endpoint_cache.extend(client.endpoints.list())

    logger.debug('existing endpoints %r', _endpoint_cache)

    endpoints = filter(lambda ep: ep.service_id == service.id, _endpoint_cache)
    logger.debug('filtered endpoints %r', endpoints)

    for e in endpoints:
        if e.service_id == service.id:
            if e.interface == endpoint['interface']:
                if e.url == endpoint['url']:
                    logger.debug('endpoint already exists %r', e)
                    return e

                logger.info('updating endpoint %r', e)
                endpoint = client.endpoints.update(
                    endpoint=e.id,
                    service=service,
                    url=endpoint['url'],
                    interface=endpoint['interface'],
                    region=endpoint['region'],
                )
                _endpoint_cache = [endpoint
                                   if x.id == endpoint.id else x
                                   for x in _endpoint_cache]
                return endpoint

    logger.info(
        'creating new %s endpoint %s with url: %s on %s region',
        endpoint['interface'], service.name,
        endpoint['url'], endpoint['region']
    )

    endpoint = client.endpoints.create(
        service=service,
        url=endpoint['url'],
        interface=endpoint['interface'],
        region=endpoint['region'],
    )
    _endpoint_cache.append(endpoint)
    logger.debug('created endpoint %r', endpoint)

    return endpoint


@retry()
def get_user(client, domain, name):
    """Get user

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
    """Create user

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param username:
    :return:
    :rtype: keystoneclient.v3.users.User
    """
    user = client.users.create(username, **kwargs)
    logger.info("created user %s", username)

    return user


@retry()
def update_user(client, user, **kwargs):
    """Update user

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param user:
    :type user: keystoneclient.v3.users.User
    :return:
    """
    user = client.users.update(user, **kwargs)
    logger.info('updated user %s', user.name)


@retry()
def get_role_assignments(client, user, project):
    """Get role assignments

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
def get_group_project_role_assignments(client, group, project):
    """Get group role assignments

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param group:
    :type group: keystoneclient.v3.groups.Group
    :param project:
    :type project: keystoneclient.v3.projects.Project
    :return:
    :rtype: list[keystoneclient.v3.roles.Role]
    """
    return client.role_assignments.list(group=group, project=project)


@retry()
def get_group_domain_role_assignments(client, group, domain):
    """Get group role assignments

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param group:
    :type group: keystoneclient.v3.groups.Group
    :param domain:
    :type domain: keystoneclient.v3.domains.Domain
    :return:
    :rtype: list[keystoneclient.v3.roles.Role]
    """
    return client.role_assignments.list(group=group, domain=domain)


@retry()
def get_domain_role_assignments(client, user, domain):
    """Get domain role assignments

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param user:
    :type user: keystoneclient.v3.users.User
    :param domain:
    :type domain: keystoneclient.v3.domains.Domain
    :return:
    """
    return client.role_assignments.list(user=user, domain=domain)


@retry()
def grant_role(client, role_id, user, project):
    """Grant role

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
def grant_group_project_role(client, role_id, group, project):
    """Grant a role to a group on a project

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param role_id:
    :type role_id: str
    :param group:
    :type group: keystoneclient.v3.groups.Group
    :param project:
    :type project: keystoneclient.v3.projects.Project
    :return:
    """
    client.roles.grant(role_id, group=group, project=project)


@retry()
def grant_group_domain_role(client, role_id, group, domain):
    """Grant a role to a group on a domain

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param role_id:
    :type role_id: str
    :param group:
    :type group: keystoneclient.v3.groups.Group
    :param domain:
    :type domain: keystoneclient.v3.domains.Domain
    :return:
    """
    client.roles.grant(role_id, group=group, domain=domain)


@retry()
def grant_domain_role(client, role_id, user, domain):
    """Grant domain role

    :param client:
    :type client: keystoneclient.v3.client.Client
    :param role_id:
    :type role_id: str
    :param user:
    :type user: keystoneclient.v3.users.User
    :param domain:
    :type domain: keystoneclient.v3.domains.Domain
    :return:
    """
    client.roles.grant(role_id, user=user, domain=domain)


def ensure_user_in_group(client, user, group):
    """Ensure user is in the specified group

    :type client: keystoneclient.v3.client.Client
    :type user: keystoneclient.v3.users.User
    :type group: keystoneclient.v3.groups.Group
    :return:
    """
    try:
        client.users.check_in_group(user, group)
        logger.info('user %s is already in group %s', user.name, group.name)
    except NotFound:
        client.users.add_to_group(user, group)
        logger.info('added user %s to group %s', user.name, group.name)


@retry()
def ensure_kubernetes_namespace(client, namespace):
    """Ensure Kubernetes namespace exists

    :type client: kubernetes.KubernetesAPIClient
    :type namespace: str
    :return:
    """
    try:
        client.get('/api/v1/namespaces/{}', namespace)
    except HTTPError as e:
        if e.response.status_code == 404:
            logger.info('creating namespace: %s', namespace)
            client.post('/api/v1/namespaces', json={
                'apiVersion': 'v1',
                'kind': 'Namespace',
                'metadata': {
                    'name': namespace
                }
            })


@retry()
def get_kubernetes_secret(name, namespace=None):
    """Get Kubernetes secret

    :param name:
    :param namespace: namespace, auto if None
    :return: loaded secret dict or None if it does not exist
    """
    client = get_kubernetes_client()

    if namespace is None:
        namespace = get_current_namespace()

    try:
        return client.get('/api/v1/namespaces/{}/secrets/{}', namespace, name)
    except HTTPError as err:
        if err.response.status_code != 404:
            raise

        return None


def create_kubernetes_secret(fields, name, namespace=None, replace=False):
    """Create Kubernetes secret

    :param fields:
    :type fields: dict[str, str]
    :param name: name of the secret
    :type name: str
    :param namespace: namespace, auto if None
    :param replace: if True, replace secret (PUT); if False, create new
    :type replace: bool
    :return:
    """
    client = get_kubernetes_client()

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

    if replace:
        logger.info('replacing secret "%s" in namespace "%s"',
                    name, namespace)
        return client.request('PUT', '/api/v1/namespaces/{}/secrets/{}',
                              namespace, name, json=secret)

    logger.info('creating secret "%s" in namespace "%s"', name, namespace)
    return client.post('/api/v1/namespaces/{}/secrets',
                       namespace, json=secret)


def diff_kubernetes_secret(secret, desired_fields):
    """Computes a set of changed fields (either added, removed, or modified)
    between the given existing secret and the set of desired fields.

    :param secret: an existing secret as a KubernetesAPIResponse containing
                   encoded secret data
    :type secret: KubernetesAPIResponse
    :param desired_fields: a dict of desired fields
    :type desired_fields: dict[str, str]
    :return: set[str]
    """
    current_keys = set(secret.data.keys())
    desired_keys = set(desired_fields.keys())

    differences = current_keys.symmetric_difference(desired_keys)

    for field in current_keys.intersection(desired_keys):
        decoded_bytes = base64.b64decode(secret.data[field])
        decoded_str = decoded_bytes.decode('utf-8')
        if decoded_str != desired_fields[field]:
            differences.add(field)

    return differences


def parse_secret(secret):
    if isinstance(secret, basestring):
        if '/' in secret:
            namespace, name = secret.split('/', 1)
            return namespace, name

        return None, secret

    return secret['namespace'], secret['name']


def get_password(secret):
    """Get password

    :type secret: KubernetesAPIResponse
    :return:
    """
    if 'OS_PASSWORD' not in secret.data:
        # probably not recoverable, short of deleting the existing
        # secret and re-creating (which would be awful in its own way)
        raise KeystoneInitException('existing secret {} is '
                                    'invalid'.format(secret.metadata.name))

    pass_bytes = base64.b64decode(secret.data['OS_PASSWORD'])
    return pass_bytes.decode('utf-8')


def ensure_kubernetes_secret(existing, fields, secret_cfg):
    """Ensures that a secret exists with the given fields and values. Existing
    secrets will be replaced if fields have changed.

    :param existing: the existing secret
    :type existing: KubernetesAPIResponse or None
    :param fields: map of fields+values that must be set
    :type fields: dict[str, str]
    :param secret_cfg: user-provided secret config from YAML
    :type secret_cfg: dict[str, str]
    """
    s_namespace, s_name = parse_secret(secret_cfg)

    if existing:
        diff = diff_kubernetes_secret(existing, fields)
        if diff:
            logger.info('secret fields are outdated in %s/%s: %r',
                        s_namespace, s_name, diff)
            create_kubernetes_secret(fields, s_name, s_namespace,
                                     replace=True)
        else:
            logger.info('secret is up-to-date: %s/%s', s_namespace, s_name)
    else:
        logger.info('creating new secret: %s/%s', s_namespace, s_name)
        create_kubernetes_secret(fields, s_name, s_namespace)


def load_global_roles(ks, global_roles):
    """Load global roles

    :type ks: keystoneclient.v3.client.Client
    :type global_roles: list[str]
    """
    logger.info('loading global roles...')
    for role_name in global_roles:
        get_or_create_global_role(ks, role_name)


def _roles_to_grant(ks, domain, current_roles, desired_role_names):
    """Which roles to grant

    :type ks: keystoneclient.v3.client.Client
    :type current_roles: list[keystoneclient.v3.roles.Role]
    :type desired_role_names: list[str]
    :return: A set of role IDs to grant (desired - current)
    :rtype: set[str]
    """

    current_ids = set(map(lambda a: a.role['id'], current_roles))
    desired_roles = map(lambda n: get_or_create_role(ks, domain, n),
                        desired_role_names)
    desired_ids = set(map(lambda r: r.id, desired_roles))

    return desired_ids - current_ids


def load_user(ks, domain, user_cfg, member_role_name, admin_url=None):
    """Load user

    :type ks: keystoneclient.v3.client.Client
    :type domain: keystoneclient.v3.domains.Domain
    :type user_cfg: dict
    :type member_role_name: str
    :type admin_url: str or None
    :return:
    """
    username = user_cfg.get('username')
    user = get_user(ks, domain, username)

    reset_password = False

    if 'project' in user_cfg:
        # currently assuming all valid projects are at least
        # referenced in `projects` block
        project = get_or_create_project(ks, domain, user_cfg['project'])
    else:
        project = None

    if 'secret' in user_cfg:
        s_namespace, s_name = parse_secret(user_cfg['secret'])
        secret = get_kubernetes_secret(s_name, s_namespace)
        if secret:
            # TODO(timothyb89) consider verifying this password (i.e. attempt to log in)
            password = get_password(secret)
            logger.info('using existing password from secret %s for user %s',
                        s_name, username)
        elif user:
            logger.warning('keystone user %s exists with missing secret '
                           '%s (ns: %s), the password will be reset to a '
                           'random value!', username, s_name, s_namespace)
            password = generate_password()
            reset_password = True
        else:
            logger.info('generating random password for user %s', username)
            password = generate_password()
    else:
        logger.info('using static password for user %s', username)
        password = user_cfg['password']
        secret = None

    if user:
        if hasattr(user, 'project_id') \
                and project is not None \
                and project.id == user.project_id:
            update_user(ks, user, project_id=project.id)
            logger.info('reassigned user %s to project %s',
                        user.name, project.name)

        if reset_password:
            update_user(ks, user, password=password)
            logger.warning('reset password for user %s', username)
    else:
        email = user_cfg.get('email', None)

        # project is supposedly deprecated in favor of default_project
        # ... but we'll use it anyway
        user = create_user(ks, username,
                           domain=domain, password=password,
                           email=email, project=project)

    if 'secret' in user_cfg:
        fields = {
            'OS_USERNAME': username,
            'OS_PASSWORD': password,
            'OS_AUTH_URL': ks.session.auth.auth_url,
            'OS_USER_DOMAIN_NAME': domain.name
        }

        if admin_url:
            fields['OS_ADMIN_URL'] = admin_url

        if project:
            fields['OS_PROJECT_NAME'] = project.name
            fields['OS_PROJECT_ID'] = project.id
            fields['OS_PROJECT_DOMAIN_NAME'] = domain.name

        logger.info('ensuring secret for user %s is valid...', username)
        ensure_kubernetes_secret(secret, fields, user_cfg['secret'])

    if 'group' in user_cfg:
        group = get_or_create_group(ks, domain, user_cfg['group'])
        ensure_user_in_group(ks, user, group)

    if 'groups' in user_cfg:
        for group_name in user_cfg['groups']:
            group = get_or_create_group(ks, domain, group_name)
            ensure_user_in_group(ks, user, group)

    # TODO(sjmc7) should we remove roles that aren't in the list? Could modify
    # roles_to_grant to return two lists
    desired_project_roles = user_cfg.get('roles', [])
    if desired_project_roles:
        desired_project_roles.append(member_role_name)
        current_project_roles = get_role_assignments(ks, user, project)
        proj_roles_to_grant = _roles_to_grant(ks, domain,
                                              current_project_roles,
                                              desired_project_roles)
        logger.info('granting project roles to user: %r', proj_roles_to_grant)
        for role_id in proj_roles_to_grant:
            grant_role(ks, role_id, user, project)

    # Now do the same for domains
    desired_domain_roles = user_cfg.get('domain_roles', [])
    if desired_domain_roles:
        current_domain_roles = get_domain_role_assignments(ks, user, domain)
        domain_roles_to_grant = _roles_to_grant(ks, domain,
                                                current_domain_roles,
                                                desired_domain_roles)
        logger.info('granting domain roles to user: %r', domain_roles_to_grant)
        for role_id in domain_roles_to_grant:
            grant_domain_role(ks, role_id, user, domain)


def load_domains(ks, domains, member_role_name):
    """Load domains

    :type ks: keystoneclient.v3.client.Client
    :type domains: dict[str, dict[str, list]]
    :type member_role_name: str
    :return:
    """
    for name, options in domains.iteritems():
        domain = get_or_create_domain(ks, None if name == 'default' else name)
        admin_url = get_keystone_admin_url(ks, domain)

        logger.info('creating projects...')
        for project in options.get('projects', []):
            get_or_create_project(ks, domain, project)

        logger.info('creating roles...')
        for role in options.get('roles', []):
            get_or_create_role(ks, domain, role)

        logger.info('creating groups...')
        for group in options.get('groups', []):
            get_or_create_group(ks, domain, group)

        logger.info('creating users...')
        for user_cfg in options.get('users', []):
            assert isinstance(user_cfg, dict)

            load_user(ks, domain, user_cfg, member_role_name, admin_url)

        logger.info('finished initializing domain %s', name)

    logger.info('all domains initialized successfully')


def load_services(ks, services):
    """Load services into Keystone.

    :type ks: keystoneclient.v3.client.Client
    :type services: dict[str, dict[str, list]]
    :return:
    """
    for name, options in services.viewitems():
        logger.debug('%r', options)
        logger.info('creating service...')
        service = get_or_create_service(
            client=ks,
            name=name,
            service_type=options.get('type'),
            description=options.get('description', None)
        )

        logger.info('creating %s endpoints...', name)
        for endpoint in options.get('endpoints', []):
            assert isinstance(endpoint, dict)

            get_or_create_endpoint(
                client=ks,
                service=service,
                url=options.get('url', ''),
                endpoint=endpoint
            )

    logger.info('all services initialized successfully')


def main():
    ks = get_keystone_client()

    with open(PRELOAD_PATH, 'r') as f:
        preload = yaml.safe_load(f)

        # if a _member_ role doesn't exist, create it globally
        member_role_name = preload.get('member_role', DEFAULT_MEMBER_ROLE)
        logger.info('making sure member role (%s) exists...', member_role_name)
        get_or_create_global_role(ks, member_role_name)

        if 'global_roles' in preload:
            load_global_roles(ks, preload['global_roles'])

        if 'domains' in preload:
            load_domains(ks, preload['domains'], member_role_name)

        if 'services' in preload:
            load_services(ks, preload['services'])


if __name__ == '__main__':
    main()
