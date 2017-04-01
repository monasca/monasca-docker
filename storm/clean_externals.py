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

from __future__ import print_function

import os
import shutil
import sys

EXTERNAL_PATH = os.environ.get('STORM_PATH', '/storm/external')
KEEP_EXTERNALS = os.environ.get('KEEP_EXTERNALS', None)


def main():
    externals = set(os.listdir(EXTERNAL_PATH))
    keep = set(map(lambda e: e.strip(),
                   KEEP_EXTERNALS.split(',')))
    if not keep:
        print('KEEP_EXTERNALS unset, will not remove any external libraries')
        return

    invalid = keep.difference(externals)
    if not keep.issubset(externals):
        print('Invalid values for KEEP_EXTERNALS: %r' % invalid,
              file=sys.stderr)
        sys.exit(1)

    externals.difference_update()

    remove = externals.difference(keep)
    for ext in remove:
        p = os.path.join(EXTERNAL_PATH, ext)
        print('Removing: %s' % p)
        shutil.rmtree(p, ignore_errors=True)

if __name__ == '__main__':
    main()
