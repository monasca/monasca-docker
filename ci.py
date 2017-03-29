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
#

from __future__ import print_function

import os
import signal
import subprocess
import sys


class SubprocessException(Exception):
    pass


def get_changed_files():
    if 'TRAVIS_COMMIT_RANGE' not in os.environ:
        return None

    p = subprocess.Popen([
        'git', 'diff', '--name-only',
        os.environ['TRAVIS_COMMIT_RANGE']
    ], stdout=subprocess.PIPE)

    stdout, _ = p.communicate()
    if p.returncode != 0:
        raise SubprocessException('git returned non-zero exit code')

    return [line.strip() for line in stdout.splitlines()]


def get_dirty_modules(dirty_files):
    dirty = set()
    for f in dirty_files:
        if os.path.sep in f:
            mod, _ = f.split(os.path.sep, 1)

            if not os.path.exists(os.path.join(mod, 'Dockerfile')):
                continue

            if not os.path.exists(os.path.join(mod, 'build.yml')):
                continue

            dirty.add(mod)

    return dirty


def get_dirty_for_module(files, module=None):
    ret = []
    for f in files:
        if os.path.sep in f:
            mod, rel_path = f.split(os.path.sep, 1)
            if mod == module:
                ret.append(rel_path)
        else:
            # top-level file, no module
            if module is None:
                ret.append(f)

    return ret


def main():
    files = get_changed_files()

    modules_to_build = []
    modules_to_push = []
    for module in get_dirty_modules(files):
        dirty = get_dirty_for_module(files, module)

        # if build.yml was modified, perform a full release
        # TODO verify this workflow: need to be sure that...
        #   - travis gives us access to encrypted variables (docker login ...)
        #   - releases only apply to trusted merges
        #   - readmes get updated after builds complete

        modules_to_build.append(module)
        if 'build.yml' in dirty:
            modules_to_push.append(module)

    if modules_to_build:
        build_args = ['dbuild', '-sd', 'build', 'all'] + modules_to_build
        print('build args:', build_args)

        p = subprocess.Popen(build_args, stdin=subprocess.PIPE)

        def kill(signal, frame):
            p.kill()
            print()
            print('killed!')
            sys.exit(1)

        signal.signal(signal.SIGINT, kill)
        if p.wait() != 0:
            print('build failed, exiting!')
            sys.exit(p.returncode)
    else:
        print('no modules to build')

    if modules_to_push:
        print('RELEASE NOT IMPLEMENTED, not pushing modules:',
              modules_to_push)
    else:
        print('no modules to push')


if __name__ == '__main__':
    main()

