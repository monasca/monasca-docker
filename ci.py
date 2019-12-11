#!/usr/bin/env python
# coding=utf-8

# (C) Copyright 2017-2018 Hewlett Packard Enterprise Development LP
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
import gzip
import json
import os
import re
import shutil
import signal
import six
import subprocess
import sys
import time
import yaml

from google.cloud import storage
from google.oauth2 import service_account

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
    'grafana-init': 'grafana-init',
    'monasca-statsd': 'monasca-statsd'
}
LOGS_PIPELINE_MODULE_TO_COMPOSE_SERVICES = {
    'monasca-log-metrics': 'log-metrics',
    'monasca-log-persister': 'log-persister',
    'monasca-log-transformer': 'log-transformer',
    'elasticsearch-curator': 'elasticsearch-curator',
    'elasticsearch-init': 'elasticsearch-init',
    'kafka-init': 'kafka-log-init',
    'kibana': 'kibana',
    'monasca-log-api': 'log-api',
    'monasca-log-agent': 'log-agent',
    'logspout': 'logspout',
}

METRIC_PIPELINE_INIT_JOBS = ('influxdb-init', 'kafka-init', 'mysql-init', 'alarms', 'grafana-init')
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

LOG_DIR = 'monasca-docker/' + \
          datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + \
          '_monasca_logs/'
BUILD_LOG_DIR = LOG_DIR + 'build/'
RUN_LOG_DIR = LOG_DIR + 'run/'
LOG_DIRS = [LOG_DIR, BUILD_LOG_DIR, RUN_LOG_DIR]
MAX_RAW_LOG_SIZE = 1024L  # 1KiB


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


def print_logs():
    for log_dir in LOG_DIRS:
        for f in os.listdir(log_dir):
            file_path = log_dir + f
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    log_contents = f.read()
                    print(log_contents)


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
        return print_logs()
    bucket = client.bucket('monasca-ci-logs')

    uploaded_files = {}
    for log_dir in LOG_DIRS:
        uploaded_files.update(upload_files(log_dir, bucket))

    return uploaded_files


def upload_manifest(pipeline, voting, uploaded_files, dirty_modules, files, tags):
    client = get_client()
    if not client:
        print ('Could not upload logs to GCP')
        return
    bucket = client.bucket('monasca-ci-logs')

    manifest_dict = print_env(pipeline, voting, to_print=False)
    manifest_dict['modules'] = {}
    for module in dirty_modules:
        manifest_dict['modules'][module] = {'files': []}
        for f in files:
            if module in f:
                if 'init' not in module and 'init' not in f or 'init' in module and 'init' in f:
                    manifest_dict['modules'][module]['files'].append(f)

        manifest_dict['modules'][module]['uploaded_log_file'] = {}
        for f, url in uploaded_files.iteritems():
            if module in f:
                if 'init' not in module and 'init' not in f or 'init' in module and 'init' in f:
                    manifest_dict['modules'][module]['uploaded_log_file'][f] = url

    manifest_dict['run_logs'] = {}
    for f, url in uploaded_files.iteritems():
        if 'run' in f:
            manifest_dict['run_logs'][f] = url
    manifest_dict['tags'] = tags

    file_path = LOG_DIR + 'manifest.json'
    upload_file(bucket, file_path, file_str=json.dumps(manifest_dict, indent=2),
                content_type='application/json')


def upload_files(log_dir, bucket):
    uploaded_files = {}
    for f in os.listdir(log_dir):
        file_path = log_dir + f
        if os.path.isfile(file_path):
            if os.stat(file_path).st_size > MAX_RAW_LOG_SIZE:
                with gzip.open(file_path + '.gz', 'w') as f_out, open(file_path, 'r') as f_in:
                    shutil.copyfileobj(f_in, f_out)
                file_path += '.gz'
                url = upload_file(bucket, file_path, content_encoding='gzip')
            else:
                url = upload_file(bucket, file_path)
            uploaded_files[file_path] = url
    return uploaded_files


def upload_file(bucket, file_path, file_str=None, content_type='text/plain',
                content_encoding=None):
    try:
        blob = bucket.blob(file_path)
        if content_encoding:
            blob.content_encoding = content_encoding
        if file_str:
            blob.upload_from_string(file_str, content_type=content_type)
        else:
            blob.upload_from_filename(file_path, content_type=content_type)
        blob.make_public()

        url = blob.public_url
        if isinstance(url, six.binary_type):
            url = url.decode('utf-8')

        print ('Public url for log: {}'.format(url))
        return url
    except Exception as e:
        print ('Unexpected error uploading log files to {}'
               'Skipping upload. Got: {}'.format(file_path, e))
        if content_encoding == 'gzip':
            f = gzip.open(file_path, 'r')
        else:
            f = open(file_path, 'r')
        log_contents = f.read()
        print(log_contents)
        f.close()


def set_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    if not os.path.exists(BUILD_LOG_DIR):
        os.makedirs(BUILD_LOG_DIR)
    if not os.path.exists(RUN_LOG_DIR):
        os.makedirs(RUN_LOG_DIR)


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

    if len(dirty) > 5:
        print ('Max number of changed modules exceded. '
               'Please break up the patch set until a maximum of 5 modules are changed.')
        sys.exit(1)
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
    log_dir = BUILD_LOG_DIR
    build_args = ['dbuild', '-sd', '--build-log-dir', log_dir, 'build', 'all', '+', ':ci-cd'] + modules
    print('build command:', build_args)

    p = subprocess.Popen(build_args)

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
        print('Not pushing: {!r}'.format(modules))
        return

    username = os.environ.get('DOCKER_HUB_USERNAME', None)
    password = os.environ.get('DOCKER_HUB_PASSWORD', None)
    if username and password:
        print('Logging into docker registry...')
        login = subprocess.Popen([
            'docker', 'login',
            '-u', username,
            '--password-stdin'
        ], stdin=subprocess.PIPE)
        login.communicate(password)
        if login.returncode != 0:
            print('Docker registry login failed, cannot push!')
            sys.exit(1)

    log_dir = BUILD_LOG_DIR
    push_args = ['dbuild', '-sd', '--build-log-dir', log_dir, 'build', 'push', 'all'] + modules
    print('push command:', push_args)

    p = subprocess.Popen(push_args)

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
        print('Not updating READMEs: {!r}'.format(modules))
        return

    log_dir = BUILD_LOG_DIR
    readme_args = ['dbuild', '-sd', '--build-log-dir', log_dir, 'readme'] + modules
    print('readme command:', readme_args)

    p = subprocess.Popen(readme_args)

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
    except (RuntimeError, EnvironmentError):
        raise FileWriteException(
            'Error writing CI dictionary to {}'.format(CI_COMPOSE_FILE)
        )


def load_yml(yml_path):
    try:
        with open(yml_path) as compose_file:
            compose_dict = yaml.safe_load(compose_file)
            return compose_dict
    except(RuntimeError, EnvironmentError):
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

    # note(kornicameister) check if module belong to the pipeline
    # if not, there's no point of building that as it will be build
    # for the given pipeline
    pipeline_modules = pick_modules_for_pipeline(modules_to_build, pipeline)

    if pipeline_modules:
        run_build(pipeline_modules)
    else:
        print('No modules to build.')

    update_docker_compose(pipeline_modules, pipeline)
    run_docker_compose(pipeline)
    wait_for_init_jobs(pipeline)

    cool_test_mapper = {
        'smoke': {
            METRIC_PIPELINE_MARKER: run_smoke_tests_metrics,
            LOG_PIPELINE_MARKER: lambda: print('No smoke tests for logs')
        },
        'tempest': {
            METRIC_PIPELINE_MARKER: run_tempest_tests_metrics,
            LOG_PIPELINE_MARKER: lambda: print('No tempest tests for logs')
        }
    }

    cool_test_mapper['smoke'][pipeline]()
    cool_test_mapper['tempest'][pipeline]()


def pick_modules_for_pipeline(modules, pipeline):
    if not modules:
        return []

    modules_for_pipeline = {
        LOG_PIPELINE_MARKER: LOGS_PIPELINE_MODULE_TO_COMPOSE_SERVICES.keys(),
        METRIC_PIPELINE_MARKER: METRIC_PIPELINE_MODULE_TO_COMPOSE_SERVICES.keys()
    }

    pipeline_modules = modules_for_pipeline[pipeline]

    # some of the modules are not used in pipelines, but should be
    # taken into consideration during the build
    other_modules = [
        'storm'
    ]
    print('modules: {} \n pipeline_modules: {}'.format(modules, pipeline_modules))

    # iterate over copy of all modules that are planned for the build
    # if one of them does not belong to active pipeline
    # remove from current run
    for m in modules[::]:
        if m not in pipeline_modules:
            if m in other_modules:
                print('{} is not part of either pipeline, but it will be build anyway'.format(m))
                continue
            print('Module {} does not belong to {}, skipping'.format(m, pipeline))
            modules.remove(m)

    return modules


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
    docker_names = ['docker', 'ps', '-a', '--format', '"{{.Names}}"']

    p = subprocess.Popen(docker_names, stdout=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)

    output, err = p.communicate()
    names = output.replace('"', '').split('\n')

    for name in names:
        if not name:
            continue

        docker_logs = ['docker', 'logs', '-t', name]
        log_name = RUN_LOG_DIR + 'docker_log_' + name + '.log'
        with open(log_name, 'w') as out:
            p = subprocess.Popen(docker_logs, stdout=out,
                                 stderr=subprocess.STDOUT)
        signal.signal(signal.SIGINT, kill)
        if p.wait() != 0:
            print('Error running docker log for {}'.format(name))


def output_docker_ps():
    docker_ps = ['docker', 'ps', '-a']

    docker_ps_process = subprocess.Popen(docker_ps)

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

    p = subprocess.Popen(docker_id, stdout=subprocess.PIPE)

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
    print('Running docker compose')
    output_compose_details(pipeline)

    if pipeline == 'metrics':
        services = METRIC_PIPELINE_SERVICES
    else:
        services = LOG_PIPELINE_SERVICES

    docker_compose_command = ['docker-compose',
                              '-f', CI_COMPOSE_FILE,
                              'up', '-d'] + services

    with open(RUN_LOG_DIR + 'docker_compose.log', 'w') as out:
        p = subprocess.Popen(docker_compose_command, stdout=out)

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
    print('docker compose succeeded')
    output_docker_ps()


def run_smoke_tests_metrics():
    smoke_tests_run = ['docker', 'run', '-e', 'MONASCA_URL=http://monasca:8070', '-e',
                       'METRIC_NAME_TO_CHECK=monasca.thread_count', '--net', 'monasca-docker_default', '-p',
                       '0.0.0.0:8080:8080', 'monasca/smoke-tests:latest']

    p = subprocess.Popen(smoke_tests_run)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        print('Smoke-tests failed, listing containers/logs.')
        raise SmokeTestFailedException()


def run_tempest_tests_metrics():
    print ('Running Tempest-tests')
    tempest_tests_run = ['docker', 'run', '-e', 'KEYSTONE_SERVER=keystone', '-e',
                         'KEYSTONE_PORT=5000', '--net', 'monasca-docker_default',
                         'monasca/tempest-tests:latest']

    with open(LOG_DIR + 'tempest_tests.log', 'w') as out:
        p = subprocess.Popen(tempest_tests_run, stdout=out)

    def kill(signal, frame):
        p.kill()
        print()
        print('killed!')
        sys.exit(1)

    signal.signal(signal.SIGINT, kill)
    time_delta = 0
    while True:
        poll = p.poll()
        if poll is None:
            if time_delta == 1500:
                print ('Tempest-tests timed out at 25 min')
                raise TempestTestFailedException()
            if time_delta % 30 == 0:  # noqa: S001
                print ('Still running tempest-tests')
            time_delta += 1
            time.sleep(1)
        elif poll != 0:
            print('Tempest-tests failed, listing containers/logs.')
            raise TempestTestFailedException()
        else:
            break
    print('Tempest-tests succeeded')


def handle_other(files, modules, tags, pipeline):
    print('Unsupported event type "{}", nothing to do.'.format(
        os.environ.get('TRAVIS_EVENT_TYPE')))


def print_env(pipeline, voting, to_print=True):
    environ_vars = {'environment_details': {
        'TRAVIS_COMMIT': os.environ.get('TRAVIS_COMMIT'),
        'TRAVIS_COMMIT_RANGE': os.environ.get('TRAVIS_COMMIT_RANGE'),
        'TRAVIS_PULL_REQUEST': os.environ.get('TRAVIS_PULL_REQUEST'),
        'TRAVIS_PULL_REQUEST_SHA': os.environ.get('TRAVIS_PULL_REQUEST_SHA'),
        'TRAVIS_PULL_REQUEST_SLUG': os.environ.get('TRAVIS_PULL_REQUEST_SLUG'),
        'TRAVIS_SECURE_ENV_VARS': os.environ.get('TRAVIS_SECURE_ENV_VARS'),
        'TRAVIS_EVENT_TYPE': os.environ.get('TRAVIS_EVENT_TYPE'),
        'TRAVIS_BRANCH': os.environ.get('TRAVIS_BRANCH'),
        'TRAVIS_PULL_REQUEST_BRANCH': os.environ.get('TRAVIS_PULL_REQUEST_BRANCH'),
        'TRAVIS_TAG': os.environ.get('TRAVIS_TAG'),
        'TRAVIS_COMMIT_MESSAGE': os.environ.get('TRAVIS_COMMIT_MESSAGE'),
        'TRAVIS_BUILD_ID': os.environ.get('TRAVIS_BUILD_ID'),
        'TRAVIS_JOB_NUMBER': os.environ.get('TRAVIS_JOB_NUMBER'),

        'CI_PIPELINE': pipeline,
        'CI_VOTING': voting}}

    if to_print:
        print (json.dumps(environ_vars, indent=2))
    return environ_vars


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
            print('{} is not voting, skipping failure'.format(pipeline))
    finally:
        output_docker_ps()
        output_docker_logs()
        uploaded_files = upload_log_files()
        upload_manifest(pipeline, voting, uploaded_files, modules, files, tags)


if __name__ == '__main__':
    main()
