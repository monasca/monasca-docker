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

import os
import sys

import requests

# The Apache-Storm version used in Monasca was moved to archive.apache.org.
# In case of future update, if needed Storm version can be found in MIRROR, set os environment DIRECT to None
# DIRECT = os.environ.get('DIRECT', None)
MIRROR = os.environ.get('MIRROR', 'https://www.apache.org/dyn/closer.cgi')
DIRECT = os.environ.get('DIRECT', 'http://archive.apache.org/dist/')
PATH = '{mirror}storm/apache-storm-{version}/apache-storm-{version}.tar.gz'


def main():
    if len(sys.argv) != 2:
        print('Usage: {0} [storm_version]'.format(sys.argv[0]))
        sys.exit(1)

    version = sys.argv[1]

    if not DIRECT:
        req = requests.get(MIRROR, params={
            'path': 'apache-storm-{0}.tar.gz'.format(version),
            'as_json': '1'
        })
        req.raise_for_status()
        mirror = req.json()['preferred']
    else:
        mirror = DIRECT

    print(PATH.format(mirror=mirror, version=version))


if __name__ == '__main__':
    main()
