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

from __future__ import print_function

import socket
import sys

import requests

CACERT_PATH = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
TOKEN_PATH = '/var/run/secrets/kubernetes.io/serviceaccount/token'
NAMESPACE_PATH = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
API_URL = "https://kubernetes.default:443"


def read(path):
    with open(path, 'r') as f:
        return f.read()


CURRENT_POD = socket.gethostname()
CURRENT_NAMESPACE = read(NAMESPACE_PATH)
TOKEN = read(TOKEN_PATH)


class KubernetesAPIException(Exception):
    pass


def api_get(endpoint):
    if endpoint.startswith('/'):
        endpoint = endpoint[1:]

    r = requests.get('{}/{}'.format(API_URL, endpoint),
                     timeout=1000,
                     headers={'Authorization': 'Bearer {}'.format(TOKEN)},
                     verify=CACERT_PATH)
    r.raise_for_status()

    return r.json()


def get_node_port(service_name, port=None):
    svc = api_get('/api/v1/namespaces/{}/services/{}'.format(
        CURRENT_NAMESPACE, service_name))

    ip = None
    if svc['spec']['type'] == 'NodePort':
        lb = svc['status']['loadBalancer']

        if 'ingress' in lb:
            ip = lb['ingress'][0]['ip']

    if port:
        if isinstance(port, int) or str(port).isdigit():
            for port_def in svc['spec']['ports']:
                if port_def.get('port') == port:
                    return ip, port_def['nodePort']
        else:
            for port_def in svc['spec']['ports']:
                if port_def.get('name') == port:
                    return ip, port_def['nodePort']
    else:
        for port_def in svc['spec']['ports']:
            if 'nodePort' in port_def and port_def['nodePort']:
                return ip, port_def['nodePort']

    raise KubernetesAPIException(
        'Could not get NodePort from k8s API: service={}, '
        'port={}'.format(service_name, port))


def get_node_ip():
    pod = api_get('/api/v1/namespaces/{}/pods/{}'.format(CURRENT_NAMESPACE,
                                                         CURRENT_POD))
    return pod['status']['hostIP']


def resolve_service(service_name, port=None):
    ingress_ip, node_port = get_node_port(service_name, port)
    if ingress_ip is None:
        # the node ip won't be "correct" for other services but k8s should
        # direct the traffic where it needs to go
        # it is not trivial to resolve a service -> pod node IP
        # (and doesn't make too much sense anyway)
        # potentially could just grab the master node from
        # /v1/api/nodes .items[0]
        ingress_ip = get_node_ip()

    return ingress_ip, node_port


def main():
    if len(sys.argv) not in (2, 3):
        print('A service name is required', file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) == 3:
        port_name = sys.argv[2]
    else:
        port_name = None

    ingress_ip, node_port = resolve_service(sys.argv[1], port_name)
    print('{}:{}'.format(ingress_ip, node_port))


if __name__ == '__main__':
    main()
