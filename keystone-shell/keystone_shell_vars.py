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
import sys

from typing import Union

from keystoneauth1.identity import Password
from keystoneauth1.session import Session
from keystoneclient.discover import Discover
from requests import HTTPError

from kubernetes import KubernetesAPIClient, KubernetesAPIResponse

NAMESPACE_FILE = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'

LOG_LEVEL = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))
logging.basicConfig(level=LOG_LEVEL,
                    handlers=(logging.StreamHandler(sys.stderr),))

logger = logging.getLogger(__name__)

KEYSTONE_PASSWORD_ARGS = [
    'auth_url', 'username', 'password', 'user_id', 'user_domain_id',
    'user_domain_name', 'project_id', 'project_name', 'project_domain_id',
    'project_domain_name', 'tenant_id', 'tenant_name', 'domain_id',
    'domain_name', 'trust_id', 'default_domain_id', 'default_domain_name'
]
KEYSTONE_TIMEOUT = int(os.environ.get('KEYSTONE_TIMEOUT', '10'))
KEYSTONE_VERIFY = os.environ.get('KEYSTONE_VERIFY', 'true') == 'true'
KEYSTONE_CERT = os.environ.get('KEYSTONE_CERT', None)

_kubernetes_client = None


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


def keystone_env_vars():
    ret = {}
    for arg in KEYSTONE_PASSWORD_ARGS:
        name = 'OS_{}'.format(arg.upper())
        if name in os.environ:
            ret[name] = os.environ[name]

    return ret


def keystone_args_from_env():
    ret = {}
    for arg in KEYSTONE_PASSWORD_ARGS:
        ret[arg] = os.environ.get('OS_{}'.format(arg.upper()))

    return ret


def get_keystone_client():
    auth = Password(**keystone_args_from_env())
    session = Session(auth=auth,
                      app_name='keystone-shell',
                      user_agent='keystone-shell',
                      timeout=KEYSTONE_TIMEOUT,
                      verify=KEYSTONE_VERIFY,
                      cert=KEYSTONE_CERT)

    discover = Discover(session=session)
    return discover.create_client()


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


def main():
    if len(sys.argv) > 1:
        secret_name = sys.argv[1]

        if len(sys.argv) > 2:
            secret_namespace = sys.argv[2]
        else:
            secret_namespace = None

        # purge existing keystone vars from the environment
        for var in keystone_env_vars().keys():
            print('unset {};'.format(var))

        secret = get_kubernetes_secret(secret_name, secret_namespace)
        for key, val in secret.data.items():
            val_bytes = base64.b64decode(val)
            print('export {}="{}"'.format(key, val_bytes.decode('utf-8')))

        logger.info('now using account from secret %s', secret_name)
    else:
        logger.info('no secret name arg provided, will use default environment')


if __name__ == '__main__':
    main()


