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

import datetime
import json
import os
import re
import signal
import subprocess
import sys
import time
import yaml

import six
from google.oauth2 import service_account
from google.cloud import storage


TAG_REGEX = re.compile(r'^!(\w+)(?:\s+([\w-]+))?$')

METRIC_PIPELINE_MARKER = 'metrics'
LOG_PIPELINE_MARKER = 'logs'

METRIC_PIPELINE_MODULE_TO_COMPOSE_SERVICES = {
    'monasca-agent-forwarder': 'agent-forwarder',
    'zookeeper': 'zookeeper',
    'influxdb': 'influxdb',
    'kafka': 'kafka',
    'kafka-init': 'kafka-init',
    'monasca-thresh': 'thresh',
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
LOGS_PIPELINE_MODULE_TO_COMPOSE_SERVICES = {
    'monasca-log-metrics': 'log-metrics',
    'monasca-log-persister': 'log-persister',
    'monasca-log-transformer': 'log-transformer',
    'elasticsearch-init': 'elasticsearch-init',
    'kafka-init': 'kafka-log-init',
    'kibana': 'kibana',
    'monasca-log-api': 'log-api',
}

METRIC_PIPELINE_INIT_JOBS = ('influxdb-init', 'kafka-init', 'mysql-init')
LOG_PIPELINE_INIT_JOBS = ('elasticsearch-init', 'kafka-log-init')
INIT_JOBS = {
    METRIC_PIPELINE_MARKER: METRIC_PIPELINE_INIT_JOBS,
    LOG_PIPELINE_MARKER: LOG_PIPELINE_INIT_JOBS
}

METRIC_PIPELINE_SERVICES = METRIC_PIPELINE_MODULE_TO_COMPOSE_SERVICES.values()
"""Explicit list of services for docker compose 
to launch for metrics pipeline"""
LOG_PIPELINE_SERVICES = (['kafka', 'keystone'] +
                         LOGS_PIPELINE_MODULE_TO_COMPOSE_SERVICES.values())
"""Explicit list of services for docker compose 
to launch for logs pipeline"""

PIPELINE_TO_YAML_COMPOSE = {
    METRIC_PIPELINE_MARKER: 'docker-compose.yml',
    LOG_PIPELINE_MARKER: 'log-pipeline.yml'
}

CI_COMPOSE_FILE = 'ci-compose.yml'

LOG_DIR = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '_monasca_logs'


class SubprocessException(Exception):
    pass


class FileReadException(Exception):
    pass


class FileWriteException(Exception):
    pass


class InitJobFailedException(Exception):
    pass


class TempestTestFailedException(Exception):
    pass


class SmokeTestFailedException(Exception):
    pass


def get_client():
    cred_dict_str = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', None)
    if not cred_dict_str:
        return None

    cred_dict = json.loads(cred_dict_str)
    try:
        credentials = service_account.Credentials.from_service_account_info(cred_dict)
        return storage.Client(credentials=credentials, project='monasca-ci-logs')
    except Exception as e:
        print ('Unexpected error getting GCP credentials: {}'.format(e))
        return None


def upload_log_files():
    client = get_client()
    if not client:
        print ('Could not upload logs to GCP')
        return

    uploaded_files = set()
    bucket = client.bucket('monasca-ci-logs')
    uploaded_files.update(upload_files(LOG_DIR, bucket))

    log_dir = LOG_DIR + '/build'
    uploaded_files.update(upload_files(log_dir, bucket)) 

    log_dir = LOG_DIR + '/run'
    uploaded_files.update(upload_files(log_dir, bucket)) 

    return uploaded_files


def upload_manifest(pipeline, voting, uploaded_files, dirty_modules, files, tags):
    manifest_str = print_env(pipeline, voting, to_print=False)
    manifest_str += '\nUploaded Log Files\n'
    manifest_str += '\n'.join(uploaded_files)
    manifest_str += '\nDirty Modules:\n'
    manifest_str += '\n'.join(dirty_modules)
    manifest_str += '\nDirty Files:\n'
    manifest_str += '\n'.join(files)
    manifest_str += '\nTags:\n'
    manifest_str += '\n'.join(tags)
    remote_file_path = 'monasca-docker/' + LOG_DIR + '/' + 'manifest.txt'
    upload_file(bucket, remote_file_path, None, manifest_str)


def upload_files(log_dir, bucket):
    blob = bucket.blob('monasca-docker/' + log_dir)
    for f in os.listdir(log_dir):
        local_file_path = log_dir + '/' + f
        if os.path.isfile(local_file_path):
            remote_file_path = 'monasca-docker/' + log_dir  + '/' + f
            upload_file(bucket, remote_file_path, local_file_path)
            uploaded_files.add(remote_file_path)
    return uploaded_files


def upload_file(bucket, remote_file_path, local_file_path, file_str=None):
    print ('Uploading {} to monasca-ci-logs bucket in GCP'.format(remote_file_path))
    try:
        blob = bucket.blob(remote_file_path)
        if file_str:
            blob.upload_from_string(manifest_str)
        else:
            blob.upload_from_filename(local_file_path, content_type='text/plain')
        blob.make_public()

        url = blob.public_url
        if isinstance(url, six.binary_type):
            url = url.decode('utf-8')

        print ('Public url for log: {}'.format(url))
    except Exception as e:
        print ('Unexpected error uploading log files to {}'
               'Skipping upload. Got: {}'.format(remote_file_path, e))


def set_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    if not os.path.exists(LOG_DIR + '/build'):
        os.makedirs(LOG_DIR + '/build')
    if not os.path.exists(LOG_DIR + '/run'):
        os.makedirs(LOG_DIR + '/run')


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
    log_dir = LOG_DIR + '/build'
    build_args = ['dbuild', '-sd', '--build-log-dir', log_dir, 'build', 'all', '+', ':ci-cd'] + modules
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

    log_dir = LOG_DIR + '/build'
    push_args = ['dbuild', '-sd', '--build-log-dir', log_dir, 'build', 'push', 'all'] + modules
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

    log_dir = LOG_DIR + '/build'
    readme_args = ['dbuild', '-sd', '--build-log-dir', log_dir, 'readme'] + modules
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


def update_docker_compose(modules, pipeline):

    compose_dict = load_yml(PIPELINE_TO_YAML_COMPOSE['metrics'])
    services_to_changes = METRIC_PIPELINE_MODULE_TO_COMPOSE_SERVICES.copy()

    if pipeline == 'logs':
        print('\'logs\' pipeline is enabled, including in CI run')
        log_compose = load_yml(PIPELINE_TO_YAML_COMPOSE['logs'])
        compose_dict['services'].update(log_compose['services'])
        services_to_changes.update(
            LOGS_PIPELINE_MODULE_TO_COMPOSE_SERVICES.copy()
        )

    if modules:
        compose_services = compose_dict['services']
        for module in modules:
            # Not all modules are included in docker compose
            if module not in services_to_changes:
                continue
            service_name = services_to_changes[module]
            services_to_update = service_name.split(',')
            for service in services_to_update:
                image = compose_services[service]['image']
                image = image.split(':')[0]
                image += ":ci-cd"
                compose_services[service]['image'] = image

    # Update compose version
    compose_dict['version'] = '2'

    try:
        with open(CI_COMPOSE_FILE, 'w') as docker_compose:
            yaml.dump(compose_dict, docker_compose, default_flow_style=False)
    except:
        raise FileWriteException(
            'Error writing CI dictionary to %s' % CI_COMPOSE_FILE
        )


def load_yml(yml_path):
    try:
        with open(yml_path) as compose_file:
            compose_dict = yaml.safe_load(compose_file)
            return compose_dict
    except:
        raise FileReadException('Failed to read %s', yml_path)


def handle_pull_request(files, modules, tags, pipeline):
    modules_to_build = modules[:]

    for tag, arg in tags:
        if tag in ('build', 'push'):
            if arg is None:
                # arg-less doesn't make sense for PRs since any changes to a
                # module already result in a rebuild
                continue

            modules_to_build.append(arg)

    if modules:
        run_build(modules_to_build)
    else:
        print('No modules to build.')

    update_docker_compose(modules, pipeline)
    run_docker_compose(pipeline)
    wait_for_init_jobs(pipeline)

    cool_test_mapper = {
        'smoke': {
            METRIC_PIPELINE_MARKER: run_smoke_tests_metrics,
            LOG_PIPELINE_MARKER: lambda : print('No smoke tests for logs')
        },
        'tempest': {
            METRIC_PIPELINE_MARKER: run_tempest_tests_metrics,
            LOG_PIPELINE_MARKER: lambda : print('No tempest tests for logs')
        }
    }

    cool_test_mapper['smoke'][pipeline]()
    cool_test_mapper['tempest'][pipeline]()


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
    status_output = output.rstrip()

    exit_code, status = status_output.split(":", 1)
    return exit_code == "0" and status == "exited"


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


def output_compose_details(pipeline):
    print('Running docker-compose -f ', CI_COMPOSE_FILE)
    if pipeline == 'metrics':
        services = METRIC_PIPELINE_SERVICES
    else:
        services = LOG_PIPELINE_SERVICES
    print('All services that are about to start: ', services)


def get_docker_id(init_job):
    docker_id = ['docker-compose',
                 '-f', CI_COMPOSE_FILE,
                 'ps',
                 '-q', init_job]

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
    return output.rstrip()


def wait_for_init_jobs(pipeline):
    init_status_dict = {job: False for job in INIT_JOBS[pipeline]}
    docker_id_dict = {job: "" for job in INIT_JOBS[pipeline]}

    amount_succeeded = 0
    for attempt in range(40):
        time.sleep(30)
        amount_succeeded = 0
        for init_job, status in init_status_dict.items():
            if docker_id_dict[init_job] == "":
                docker_id_dict[init_job] = get_docker_id(init_job)
            if status:
                amount_succeeded += 1
            else:
                updated_status = get_current_init_status(docker_id_dict[init_job])
                init_status_dict[init_job] = updated_status
                if updated_status:
                    amount_succeeded += 1
        if amount_succeeded == len(docker_id_dict):
            print("All init-jobs passed!")
            break
        else:
            print("Not all init jobs have succeeded. Attempt: " + str(attempt + 1) + " of 40")

    if amount_succeeded != len(docker_id_dict):
        print("Init-jobs did not succeed, printing docker ps and logs")
        output_docker_ps()
        output_docker_logs()
        raise InitJobFailedException()

    # Sleep in case jobs just succeeded
    time.sleep(60)


def handle_push(files, modules, tags, pipeline):
    modules_to_push = []
    modules_to_readme = []

    force_push = False
    force_readme = False

    for tag, arg in tags:
        if tag in ('build', 'push'):
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


def run_docker_compose(pipeline):
    output_compose_details(pipeline)

    if pipeline == 'metrics':
        services = METRIC_PIPELINE_SERVICES
    else:
        services = LOG_PIPELINE_SERVICES

    docker_compose_command = ['docker-compose',
                              '-f', CI_COMPOSE_FILE,
                              'up', '-d'] + services

    with open(LOG_DIR + '/run/docker_compose.log', 'wb') as out:
        p = subprocess.Popen(docker_compose_command, stdin=subprocess.PIPE, stdout=out)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        print('docker compose failed, exiting!')
        sys.exit(p.returncode)

    # print out running images for debugging purposes
    output_docker_ps()


def run_smoke_tests_metrics():
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
        raise SmokeTestFailedException()


def run_tempest_tests_metrics():
    tempest_tests_run = ['docker', 'run', '-e', 'KEYSTONE_SERVER=keystone', '-e',
                         'KEYSTONE_PORT=5000', '--net', 'monascadocker_default',
                         'monasca/tempest-tests:latest']

    with open(LOG_DIR + 'tempest_tests.txt', 'wb') as out:
        p = subprocess.Popen(tempest_tests_run, stdin=subprocess.PIPE, stdout=out)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        print('Tempest-tests failed, listing containers/logs.')
        output_docker_logs()
        output_docker_ps()
        raise TempestTestFailedException()


def handle_other(files, modules, tags):
    print('Unsupported event type "%s", nothing to do.' % (
        os.environ.get('TRAVS_EVENT_TYPE')))


def print_env(pipeline, voting, to_print=True):
    environ_string = str('Environment details:\n'
        'TRAVIS_COMMIT=' + os.environ.get('TRAVIS_COMMIT') + '\n'
        'TRAVIS_COMMIT_RANGE=' + os.environ.get('TRAVIS_COMMIT_RANGE') + '\n'
        'TRAVIS_PULL_REQUEST=' + os.environ.get('TRAVIS_PULL_REQUEST') + '\n'
        'TRAVIS_PULL_REQUEST_SHA=' +
            os.environ.get('TRAVIS_PULL_REQUEST_SHA') + '\n'
        'TRAVIS_PULL_REQUEST_SLUG=' +
            os.environ.get('TRAVIS_PULL_REQUEST_SLUG') + '\n'
        'TRAVIS_SECURE_ENV_VARS='+  os.environ.get('TRAVIS_SECURE_ENV_VARS') + '\n'
        'TRAVIS_EVENT_TYPE=' + os.environ.get('TRAVIS_EVENT_TYPE') + '\n'
        'TRAVIS_BRANCH=' + os.environ.get('TRAVIS_BRANCH') + '\n'
        'TRAVIS_PULL_REQUEST_BRANCH=' +
            os.environ.get('TRAVIS_PULL_REQUEST_BRANCH') + '\n'
        'TRAVIS_TAG=' + os.environ.get('TRAVIS_TAG') + '\n'
        'TRAVIS_COMMIT_MESSAGE=' + os.environ.get('TRAVIS_COMMIT_MESSAGE') + '\n'

        'CI_PIPELINE=' + pipeline + '\n'
        'CI_VOTING=' + str(voting))

    if to_print:
        print (environ_string)
    return environ_string


def main():
    args = sys.argv[1:]
    pipeline = args[0] if len(args) >= 1 else None
    voting = bool(args[1]) if len(args) == 2 else True

    if os.environ.get('TRAVIS_BRANCH', None) != 'master':
        print('Not master branch, skipping tests.')
        return
    if not pipeline or pipeline not in ('logs', 'metrics'):
        print('Unkown pipeline=', pipeline)
        return

    print_env(pipeline, voting)
    set_log_dir()

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

    try:
        func(files, modules, tags, pipeline)
    except (FileReadException, FileWriteException):
        # those error must terminate the CI
        raise
    except (InitJobFailedException, SmokeTestFailedException,
            TempestTestFailedException):
        if voting:
            raise
        else:
            print('%s is not voting, skipping failure' % pipeline)
    uploaded_files = upload_log_files()
    upload_manifest(pipeline, voting, uploaded_files, modules, files, tags)


if __name__ == '__main__':
    main()
