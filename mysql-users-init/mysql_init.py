#!/usr/bin/env python3

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

from typing import (List, Dict, Union, Sequence, Iterable,
                    TypeVar, Callable, Optional, Any)

import pymysql
import yaml

from pymysql.connections import Connection
from pymysql.err import OperationalError
from requests import HTTPError
from requests import RequestException

from kubernetes import KubernetesAPIClient, KubernetesAPIResponse

PASSWORD_CHARACTERS = string.ascii_letters + string.digits

PRELOAD_PATH = os.environ.get('PRELOAD_PATH', '/preload.yml')
NAMESPACE_FILE = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'

LOG_LEVEL = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

_kubernetes_client = None

T = TypeVar('T')


def first(condition: Callable[[T], bool], seq: Sequence[T]) -> Optional[T]:
    try:
        return next(filter(condition, seq))
    except StopIteration:
        return None


class MySQLInitException(Exception):
    pass


def retry(retries=5, delay=2.0,
          exc_types=(OperationalError, RequestException)):

    def decorator(func):
        def f_retry(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exc_types as exc:
                    if i < retries - 1:
                        logger.info('%s failed (attempt %d of %d)',
                                    func.__name__, i + 1, retries)
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


def get_current_namespace() -> str:
    if 'NAMESPACE' in os.environ:
        return os.environ['NAMESPACE']

    if os.path.exists(NAMESPACE_FILE):
        with open(NAMESPACE_FILE, 'r') as f:
            return f.read()

    logger.warning('Not running in cluster and $NAMESPACE is not set, '
                   'assuming \'default\'!')
    return 'default'


def get_kubernetes_client() -> KubernetesAPIClient:
    global _kubernetes_client

    if _kubernetes_client is None:
        _kubernetes_client = KubernetesAPIClient()
        _kubernetes_client.load_auto_config()

    return _kubernetes_client


def generate_password(length=16) -> str:
    r = random.SystemRandom()
    return ''.join(r.choice(PASSWORD_CHARACTERS) for _ in range(length))


@retry(retries=10, delay=5.0)
def get_mysql_client() -> Connection:
    return pymysql.connect(host=os.environ.get('MYSQL_INIT_HOST'),
                           port=int(os.environ.get('MYSQL_INIT_PORT', '3306')),
                           user=os.environ.get('MYSQL_INIT_USERNAME'),
                           password=os.environ.get('MYSQL_INIT_PASSWORD'),
                           cursorclass=pymysql.cursors.DictCursor,
                           charset='utf8mb4',
                           sql_mode='NO_AUTO_CREATE_USER')


@retry()
def missing_hosts_for_user(client: Connection,
                           name: str,
                           hosts: List[str]) -> List[str]:
    """

    :param client:
    :param name: the user name
    :param hosts: a list of expected user hosts
    :return: true if user with given name exists, false if not
    """
    with client.cursor() as c:
        c.execute('select `Host` from mysql.user where `User` = %s',
                  (name,))
        found_hosts = map(lambda r: r['Host'], c.fetchall())

        return list(set(hosts) - set(found_hosts))


@retry()
def ensure_kubernetes_namespace(client: KubernetesAPIClient, namespace: str):
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
def get_kubernetes_secret(name: str,
                          namespace: str=None) -> Union[KubernetesAPIResponse,
                                                        None]:
    """
    :return: loaded secret dict or None if it does not exist
    """
    client = get_kubernetes_client()

    if namespace is None:
        namespace = get_current_namespace()

    try:
        return client.get('/api/v1/namespaces/{}/secrets/{}', namespace, name)
    except HTTPError as e:
        if e.response.status_code != 404:
            raise

        return None


def create_kubernetes_secret(fields: Dict[str, str],
                             name: str,
                             namespace: str=None):
    """

    :param fields:
    :param name:
    :param namespace: namespace, auto if None
    :return:
    """
    client = get_kubernetes_client()

    if namespace is None:
        namespace = get_current_namespace()

    ensure_kubernetes_namespace(client, namespace)

    def prep(value):
        return base64.b64encode(value.encode('utf-8')).decode('utf-8')

    encoded = {k: prep(v) for k, v in fields.items()}
    secret = {
        'kind': 'Secret',
        'apiVersion': 'v1',
        'type': 'Opaque',
        'metadata': {
            'name': name,
            'namespace': namespace,
            'labels': {
                'heritage': 'mysql-users-init-job'
            }
        },
        'data': encoded
    }

    logging.info('creating secret "%s" in namespace "%s"', name, namespace)
    return client.post('/api/v1/namespaces/{}/secrets',
                       namespace, json=secret)


def parse_secret(secret: Union[str, Dict[str, str]]):
    if isinstance(secret, str):
        if '/' in secret:
            namespace, name = secret.split('/', 1)
            return namespace, name
        else:
            return None, secret

    return secret['namespace'], secret['name']


def get_or_create_password(client: Connection,
                           user: Dict[str, Any]) -> str:
    if 'password' in user:
        return user['password']
    elif 'secret' in user:
        s_namespace, s_name = parse_secret(user['secret'])
        existing_secret = get_kubernetes_secret(s_name, s_namespace)

        if existing_secret:
            # the password already exists, so try to use it (else we would put
            # whichever service consumes this secret in an invalid state)

            if 'password' not in existing_secret.data:
                # probably not recoverable, short of deleting the existing
                # secret and re-creating (which would be awful in its own way)
                raise MySQLInitException('existing secret %s is '
                                         'invalid' % s_name)

            logging.info('will use existing password from secret %s for user '
                         '%s' % (s_name, user['username']))
            pass_bytes = base64.b64decode(existing_secret.data['password'])
            return pass_bytes.decode('utf-8')
        else:
            password = generate_password()
            create_kubernetes_secret({
                'username': user['username'],
                'password': password,
                'host': client.host,
                'port': str(client.port)
            }, s_name, s_namespace)

            return password


def create_user(client: Connection, username: str, host: str, password: str):
    with client.cursor() as c:
        c.execute('CREATE USER %s@%s IDENTIFIED BY %s',
                  (username, host, password))


def flush_privileges(client: Connection):
    with client.cursor() as c:
        logging.debug('flushing privileges...')
        c.execute('FLUSH PRIVILEGES;')


def get_current_databases(client: Connection) -> Iterable[str]:
    with client.cursor() as c:
        c.execute('SHOW DATABASES;')
        return map(lambda r: r['Database'], c.fetchall())


def create_database(client: Connection, name: str,
                    charset: str=None, collation: str=None):
    if charset:
        charset_part = ' DEFAULT CHARACTER SET %s' % charset
    else:
        charset_part = ''

    if collation:
        collation_part = ' DEFAULT COLLATE %s' % collation
    else:
        collation_part = ''

    with client.cursor() as c:
        c.execute('CREATE DATABASE %s%s%s' % (
            name, charset_part, collation_part
        ))


def grant_privileges(client: Connection,
                     database: str,
                     privileges: List[str],
                     user: str, host: str):
    with client.cursor() as c:
        privs = ', '.join(p.upper() for p in privileges)
        c.execute('GRANT %s ON %s.* TO \'%s\'@\'%s\'' % (
            privs, database, user, host
        ))

        logging.info('granted %s on %s to %s@%s', privs, database, user, host)


def load_grant(client: Connection, database: str,
               grant: Union[str, Dict[str, Any]],
               known_hosts: Dict[str, List[str]]):
    # note: sql grants are idempotent so we'll just apply them every time
    # note: only database-level privileges can be granted
    if isinstance(grant, str):
        # just a username
        hosts = known_hosts.get(grant, None)
        if not hosts:
            hosts = ['%']

        for host in hosts:
            grant_privileges(client, database, ['ALL'], grant, host)
    else:
        # block with optional hosts override / privileges
        username = grant['username']
        privileges = grant['privileges']
        if isinstance(privileges, str):
            privileges = map(lambda p: p.strip(), privileges.split(','))

        if 'host' in grant:
            hosts = grant['host']
            if isinstance(hosts, str):
                hosts = [hosts]
        else:
            hosts = known_hosts.get(username, None) or ['%']

        for host in hosts:
            grant_privileges(client, database, privileges, username, host)


def load_users(client: Connection,
               users: List[Dict[str, Union[List, str]]]) -> Dict[str, List]:
    known_hosts = {}

    for user in users:
        username = user['username']
        if 'host' in user:
            hosts = user['host']
            if isinstance(hosts, str):
                hosts = [hosts]
        else:
            hosts = ['%', 'localhost']

        known_hosts[username] = hosts

        hosts_to_create = missing_hosts_for_user(client, username, hosts)
        if hosts_to_create:
            logging.info('creating user %s for hosts: %r', username,
                         hosts_to_create)

            password = get_or_create_password(client, user)
            for host in hosts_to_create:
                create_user(client, username, host, password)
                logging.info('created user %s@%s' % (username, host))
        else:
            logging.info('user already exists: %s', username)

    return known_hosts


def load_databases(client: Connection,
                   databases: List[Dict[str, Union[List, str]]],
                   known_hosts: Dict[str, List[str]]):
    current_databases = set(get_current_databases(client))
    for database_cfg in databases:
        name = database_cfg['name']
        if name in current_databases:
            logging.info('database already exists: %s', name)
        else:
            charset = database_cfg.get('charset', None)
            collation = database_cfg.get('collation', None)

            create_database(client, name, charset, collation)

            logging.info('created database %s: charset=%r, collation=%r',
                         name, charset, collation)

        for grant_cfg in database_cfg.get('grants', []):
            load_grant(client, name, grant_cfg, known_hosts)


def main():
    mysql = get_mysql_client()

    with open(PRELOAD_PATH, 'r') as f:
        preload = yaml.safe_load(f)

        if 'users' in preload:
            logger.info('loading users...')
            known_hosts = load_users(mysql, preload['users'])
            flush_privileges(mysql)
        else:
            logger.info('no users to load')
            known_hosts = {}

        if 'databases' in preload:
            logger.info('loading databases...')
            load_databases(mysql, preload['databases'], known_hosts)
            flush_privileges(mysql)
        else:
            logger.info('no databases to load')

        logger.info('done')

if __name__ == '__main__':
    main()
