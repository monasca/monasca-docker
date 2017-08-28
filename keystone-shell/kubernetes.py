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

import json
import os

import dpath.util
import requests
import yaml

from dotmap import DotMap

CACERT_PATH = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
TOKEN_PATH = '/var/run/secrets/kubernetes.io/serviceaccount/token'

KUBE_CONFIG_PATH = os.environ.get('KUBECONFIG', '~/.kube/config')

KUBERNETES_SERVICE_HOST = os.environ.get('KUBERNETES_SERVICE_HOST', 'kubernetes.default')
KUBERNETES_SERVICE_PORT = os.environ.get('KUBERNETES_SERVICE_PORT', '443')
KUBERNETES_API_URL = "https://{}:{}".format(KUBERNETES_SERVICE_HOST, KUBERNETES_SERVICE_PORT)

DEFAULT_TIMEOUT = 10


def load_current_kube_credentials():
    with open(os.path.expanduser(KUBE_CONFIG_PATH), 'r') as f:
        config = DotMap(yaml.safe_load(f))

        ctx_name = config['current-context']
        ctx = next(c for c in config.contexts if c.name == ctx_name)
        cluster = next(c for c in config.clusters if c.name == ctx.context.cluster).cluster

        if 'certificate-authority' in cluster:
            ca_cert = cluster['certificate-authority']
        else:
            ca_cert = None

        if ctx.context.user:
            user = next(u for u in config.users if u.name == ctx.context.user).user
            return cluster.server, ca_cert, (user['client-certificate'], user['client-key'])
        else:
            return cluster.server, ca_cert, None


class KubernetesAPIError(Exception):
    pass


class KubernetesAPIResponse(DotMap):

    def __init__(self, response, decoded=None):
        super(KubernetesAPIResponse, self).__init__(decoded, _dynamic=False)
        self.response = response

    def get(self, glob, separator="/"):
        return dpath.util.get(self, glob, separator)

    def search(self, glob, yielded=False, separator="/", afilter=None, dirs=True):
        return dpath.util.search(self, glob, yielded, separator, afilter, dirs)

    def set(self, glob, value):
        return dpath.util.set(self, glob, value)

    def new(self, path, value):
        return dpath.util.new(self, path, value)

    @property
    def status_code(self):
        return self.response.status_code


class KubernetesAPIClient(object):
    def __init__(self, verify=True):
        self.session = requests.Session()
        self.session.verify = verify
        self.api_url = None

    def load_cluster_config(self):
        self.session.verify = CACERT_PATH

        # requests will purge request Content-Type headers if we hit a
        # redirect, so try to avoid running into one because of an extra /
        self.api_url = KUBERNETES_API_URL.rstrip('/')

        with open(TOKEN_PATH, 'r') as f:
            token = f.read()
            self.session.headers.update({
                'Authorization': 'Bearer {}'.format(token)
            })

    def load_kube_config(self):
        server, ca_cert, cert = load_current_kube_credentials()
        self.api_url = server.rstrip('/')
        self.session.cert = cert
        self.session.verify = ca_cert

        if self.api_url.endswith('/'):
            self.api_url = self.api_url.rstrip('/')

    def load_auto_config(self):
        if os.path.exists(os.path.expanduser(KUBE_CONFIG_PATH)):
            self.load_kube_config()
        elif os.path.exists(TOKEN_PATH):
            self.load_cluster_config()
        else:
            raise KubernetesAPIError('No supported API configuration found!')

    def request(self, method, path, *args, **kwargs):
        raise_for_status = kwargs.pop('raise_for_status', True)
        timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT)

        if args:
            path = path.format(*args)

        slash = '' if path.startswith('/') else '/'
        res = self.session.request(
            method,
            '{}{}{}'.format(self.api_url, slash, path),
            timeout=timeout,
            **kwargs)

        if raise_for_status:
            res.raise_for_status()

        return KubernetesAPIResponse(res, res.json())

    def get(self, path, *args, **kwargs):
        kwargs.setdefault('allow_redirects', True)
        return self.request('GET', path, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        return self.request('POST', path, *args, **kwargs)

    def delete(self, path, *args, **kwargs):
        return self.request('DELETE', path, *args, **kwargs)

    def patch(self, path, *args, **kwargs):
        return self.request('PATCH', path, *args, **kwargs)

    def json_patch(self, ops, path, *args, **kwargs):
        if kwargs.get('allow_redirects') is True:
            raise ValueError('Patch is not compatible with redirects!')

        headers = kwargs.pop('headers', None)
        if headers:
            headers = headers.copy()
        else:
            headers = {}

        headers['Content-Type'] = 'application/json-patch+json'
        resp = self.patch(path,
                          data=json.dumps(ops), headers=headers,
                          allow_redirects=False,
                          *args, **kwargs)
        if 300 <= resp.status_code < 400:
            raise KubernetesAPIError('Encountered a redirect while sending a '
                                     'PATCH, failing!')

        return resp
