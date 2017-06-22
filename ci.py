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
import re
import signal
import subprocess
import sys
import time
import yaml

TAG_REGEX = re.compile(r'^!(\w+)(?:\s+([\w-]+))?$')

MODULE_TO_COMPOSE_SERVICE = {
    'storm': 'storm-supervisor,storm-nimbus',
    'monasca-agent-forwarder': 'agent-forwarder',
    'zookeeper': 'zookeeper',
    'influxdb': 'influxdb',
    'kafka': 'kafka',
    'monasca-thresh': 'thresh-init',
    'monasca-persister-python': 'monasca-persister',
    'mysql-init': 'mysql-init',
    'monasca-api-python': 'monasca',
    'influxdb-init': 'influxdb-init',
    'monasca-agent-collector': 'agent-collector',
    'grafana': 'grafana',
    'keystone': 'keystone',
    'monasca-alarms': 'alarms',
    'monasca-notification': 'monasca-notification',
    'grafana-init': 'grafana-init'
}


class SubprocessException(Exception):
    pass


class FileReadException(Exception):
    pass


class FileWriteException(Exception):
    pass


def get_changed_files():
    commit_range = os.environ.get('TRAVIS_COMMIT_RANGE', None)
    if not commit_range:
        return []

    p = subprocess.Popen([
        'git', 'diff', '--name-only', commit_range
    ], stdout=subprocess.PIPE)

    stdout, _ = p.communicate()
    if p.returncode != 0:
        raise SubprocessException('git returned non-zero exit code')

    return [line.strip() for line in stdout.splitlines()]


def get_message_tags():
    commit = os.environ.get('TRAVIS_COMMIT_RANGE', None)
    if not commit:
        return []

    p = subprocess.Popen([
        'git', 'log', '--pretty=%B', '-1', commit
    ], stdout=subprocess.PIPE)
    stdout, _ = p.communicate()
    if p.returncode != 0:
        raise SubprocessException('git returned non-zero exit code')

    tags = []
    for line in stdout.splitlines():
        line = line.strip()
        m = TAG_REGEX.match(line)
        if m:
            tags.append(m.groups())

    return tags


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

    return list(dirty)


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


def run_build(modules):
    build_args = ['dbuild', '-sd', 'build', 'all', '+', ':ci-cd'] + modules
    print('build command:', build_args)

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


def run_push(modules):
    if os.environ.get('TRAVIS_SECURE_ENV_VARS', None) != "true":
        print('No push permissions in this context, skipping!')
        print('Not pushing: %r' % modules)
        return

    username = os.environ.get('DOCKER_HUB_USERNAME', None)
    password = os.environ.get('DOCKER_HUB_PASSWORD', None)
    if username and password:
        print('Logging into docker registry...')
        r = subprocess.call([
            'docker', 'login',
            '-u', username,
            '-p', password
        ])
        if r != 0:
            print('Docker registry login failed, cannot push!')
            sys.exit(1)

    push_args = ['dbuild', '-sd', 'build', 'push', 'all'] + modules
    print('push command:', push_args)

    p = subprocess.Popen(push_args, stdin=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        print('build failed, exiting!')
        sys.exit(p.returncode)


def run_readme(modules):
    if os.environ.get('TRAVIS_SECURE_ENV_VARS', None) != "true":
        print('No Docker Hub permissions in this context, skipping!')
        print('Not updating READMEs: %r' % modules)
        return

    readme_args = ['dbuild', '-sd', 'readme'] + modules
    print('readme command:', readme_args)

    p = subprocess.Popen(readme_args, stdin=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        print('build failed, exiting!')
        sys.exit(p.returncode)


def update_docker_compose(modules):
    try:
        with open("docker-compose.yml") as compose_file:
            compose_dict = yaml.load(compose_file)
    except:
        raise FileReadException('Error reading chart yaml for changed chart')
    if modules:
        compose_services = compose_dict['services']
        for module in modules:
            service_name = MODULE_TO_COMPOSE_SERVICE[module]
            services_to_update = []
            if ',' in service_name:
                services_to_update.extend(service_name.split(','))
            else:
                services_to_update.append(service_name)
            for service in services_to_update:
                image = compose_services[service]['image']
                image = image.split(':')[0]
                image += ":ci-cd"
                compose_services[service]['image'] = image
    # Update compose version
    compose_dict['version'] = '2'
    try:
        with open('docker-compose.yml', 'w') as docker_compose:
            yaml.dump(compose_dict, docker_compose, default_flow_style=False)
    except:
        raise FileWriteException('Error writing modified dictionary to docker-compose.yml')


def handle_pull_request(files, modules, tags):
    if modules:
        run_build(modules)
    else:
        print('No modules to build.')
    update_docker_compose(modules)
    run_docker_compose()
    wait_for_init_jobs()
    run_smoke_tests()


def get_current_init_status(docker_id):
    init_status = ['docker', 'inspect', '-f', '{{ .State.ExitCode }}:{{ .State.Status }}', docker_id]

    p = subprocess.Popen(init_status, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)

    output, err = p.communicate()

    if p.wait() != 0:
        print('getting current status failed')
        return False
    exit_code, status = output.split(":", 1)
    if exit_code == 0 and status == "exited":
        return True
    return False


def output_docker_logs():
    docker_logs = ['docker-compose', 'logs']

    docker_logs_process = subprocess.Popen(docker_logs, stdin=subprocess.PIPE)

    def kill(signal, frame):
        docker_logs_process.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)
    if docker_logs_process.wait() != 0:
        print('Error listing logs')


def output_docker_ps():
    docker_ps = ['docker', 'ps', '-a']

    docker_ps_process = subprocess.Popen(docker_ps, stdin=subprocess.PIPE)

    def kill(signal, frame):
        docker_ps_process.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)
    if docker_ps_process.wait() != 0:
        print('Error running docker ps')


def get_docker_id(init_job):
    docker_id = ['docker-compose', 'ps', '-q', init_job]

    p = subprocess.Popen(docker_id, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)

    output, err = p.communicate()

    if p.wait() != 0:
        print('error getting docker id')
        return ""
    return output


def wait_for_init_jobs():
    init_status_dict = {"mysql-init": False,
                        "thresh-init": False,
                        "influxdb-init": False}
    docker_id_dict = {"mysql-init": "",
                      "thresh-init": "",
                      "influxdb-init": ""}
    amount_succeeded = 0
    for attempt in range(20):
        time.sleep(30)
        amount_succeeded = 0
        for init_job, status in init_status_dict.iteritems():
            if docker_id_dict[init_job] == "":
                docker_id_dict[init_job] = get_docker_id(init_job)
            if status:
                amount_succeeded += 1
            else:
                updated_status = get_current_init_status(docker_id_dict[init_job])
                init_status_dict[init_job] = updated_status
                if updated_status:
                    amount_succeeded += 1
        if amount_succeeded == 3:
            print("All init-jobs passed!")
            break

    if amount_succeeded != 3:
        print("Init-jobs did not succeed printing docker ps and logs")
        output_docker_ps()
        output_docker_logs()
        print('Exiting!')
        sys.exit(1)

    # Sleep incase jobs just succeeded
    time.sleep(30)

def handle_push(files, modules, tags):
    modules_to_push = []
    modules_to_readme = []

    force_push = False
    force_readme = False

    for tag, arg in tags:
        if tag == 'push':
            if arg is None:
                force_push = True
            else:
                modules_to_push.append(arg)
        elif tag == 'readme':
            if arg is None:
                force_readme = True
            else:
                modules_to_readme.append(arg)

    for module in modules:
        dirty = get_dirty_for_module(files, module)
        if force_push or 'build.yml' in dirty:
            modules_to_push.append(module)

        if force_readme or 'README.md' in dirty:
            modules_to_readme.append(module)

    if modules_to_push:
        run_push(modules_to_push)
    else:
        print('No modules to push.')

    if modules_to_readme:
        run_readme(modules_to_readme)
    else:
        print('No READMEs to update.')


def run_docker_compose():
    docker_compose_command = ['docker-compose', 'up', '-d']

    p = subprocess.Popen(docker_compose_command, stdin=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        print('docker compose failed, exiting!')
        sys.exit(p.returncode)


def run_smoke_tests():
    smoke_tests_run = ['docker', 'run', '-e', 'MONASCA_URL=http://monasca:8070', '-e',
                       'METRIC_NAME_TO_CHECK=monasca.thread_count', '--net', 'monascadocker_default', '-p',
                       '0.0.0.0:8080:8080', 'monasca/smoke-tests:latest']

    p = subprocess.Popen(smoke_tests_run, stdin=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        print('Smoke-tests failed, listing containers/logs.')
        output_docker_logs()
        output_docker_ps()
        print('Exiting!')
        sys.exit(p.returncode)


def handle_other(files, modules, tags):
    print('Unsupported event type "%s", nothing to do.' % (
        os.environ.get('TRAVS_EVENT_TYPE')))


def main():
    print('Environment details:')
    print('TRAVIS_COMMIT=', os.environ.get('TRAVIS_COMMIT'))
    print('TRAVIS_COMMIT_RANGE=', os.environ.get('TRAVIS_COMMIT_RANGE'))
    print('TRAVIS_PULL_REQUEST=', os.environ.get('TRAVIS_PULL_REQUEST'))
    print('TRAVIS_PULL_REQUEST_SHA=',
          os.environ.get('TRAVIS_PULL_REQUEST_SHA'))
    print('TRAVIS_PULL_REQUEST_SLUG=',
          os.environ.get('TRAVIS_PULL_REQUEST_SLUG'))
    print('TRAVIS_SECURE_ENV_VARS=', os.environ.get('TRAVIS_SECURE_ENV_VARS'))
    print('TRAVIS_EVENT_TYPE=', os.environ.get('TRAVIS_EVENT_TYPE'))
    print('TRAVIS_BRANCH=', os.environ.get('TRAVIS_BRANCH'))
    print('TRAVIS_PULL_REQUEST_BRANCH=',
          os.environ.get('TRAVIS_PULL_REQUEST_BRANCH'))
    print('TRAVIS_TAG=', os.environ.get('TRAVIS_TAG'))
    print('TRAVIS_COMMIT_MESSAGE=', os.environ.get('TRAVIS_COMMIT_MESSAGE'))

    if os.environ.get('TRAVIS_BRANCH', None) != 'master':
        print('Not master branch, skipping tests.')
        return

    files = get_changed_files()
    modules = get_dirty_modules(files)
    tags = get_message_tags()

    if tags:
        print('Tags detected:')
        for tag in tags:
            print('  ', tag)
    else:
        print('No tags detected.')

    func = {
        'pull_request': handle_pull_request,
        'push': handle_push
    }.get(os.environ.get('TRAVIS_EVENT_TYPE', None), handle_other)

    func(files, modules, tags)


if __name__ == '__main__':
    main()
