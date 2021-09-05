#!/usr/bin/env python

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

import argparse
import datetime
import gzip
import json
import logging
import os
import re
import shutil
import signal
import six
import subprocess
import sys
import time
import yaml


parser = argparse.ArgumentParser(description='CI command')
parser.add_argument('-p', '--pipeline', dest='pipeline', default=None, required=True,
                    help='Select the pipeline [metrics|logs]')
parser.add_argument('-nv', '--non-voting', dest='non_voting', action='store_true',
                    help='Set the check as non-voting')
parser.add_argument('-pl', '--print-logs', dest='printlogs', action='store_true',
                    help='Print containers logs')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='Increment verbosity')
parser.add_argument('--CI_BRANCH', dest='ci_branch', default=None, required=False,
                    help='')
parser.add_argument('--CI_EVENT_TYPE', dest='ci_event_type', default=None, required=False,
                    help='')
parser.add_argument('--CI_COMMIT_RANGE', dest='ci_commit_range', default=None, required=False,
                    help='')
args = parser.parse_args()

pipeline = args.pipeline
non_voting = args.non_voting
printlogs = args.printlogs
verbose = args.verbose
ci_branch = args.ci_branch if args.ci_branch else os.environ.get('CI_BRANCH', None)
ci_event_type = args.ci_event_type if args.ci_event_type else os.environ.get('CI_EVENT_TYPE', None)
ci_commit_range = args.ci_commit_range if args.ci_commit_range else os.environ.get('CI_COMMIT_RANGE', None)

logging.basicConfig(format = '%(asctime)s %(levelname)5.5s %(message)s')
LOG=logging.getLogger(__name__)
verbose = args.verbose
LOG.setLevel(logging.DEBUG) if verbose else LOG.setLevel(logging.INFO)
LOG.debug(args)

#TAG_REGEX = re.compile(r'^!(\w+)(?:\s+([\w-]+))?$')
TAG_REGEX = re.compile(r'^!(build|push|readme)(?:\s([\w-]+))$')

METRIC_PIPELINE_MARKER = 'metrics'
LOG_PIPELINE_MARKER = 'logs'

TEMPEST_TIMEOUT = 20 # minutes
BUILD_TIMEOUT = 20 # minutes
INITJOBS_ATTEMPS = 5

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
    'monasca-notification': 'monasca-notification',
    'grafana-init': 'grafana-init',
    'monasca-statsd': 'monasca-statsd'
}
LOGS_PIPELINE_MODULE_TO_COMPOSE_SERVICES = {
    'monasca-log-metrics': 'log-metrics',
    'monasca-log-persister': 'log-persister',
    'monasca-log-transformer': 'log-transformer',
    'elasticsearch': 'elasticsearch',
    'elasticsearch-curator': 'elasticsearch-curator',
    'elasticsearch-init': 'elasticsearch-init',
    'kafka-init': 'kafka-log-init',
    'kibana': 'kibana',
    'monasca-log-api': 'log-api',
    'monasca-log-agent': 'log-agent',
    'logspout': 'logspout',
}

METRIC_PIPELINE_INIT_JOBS = ('influxdb-init', 'kafka-init', 'mysql-init', 'grafana-init')
LOG_PIPELINE_INIT_JOBS = ('elasticsearch-init', 'kafka-log-init')
INIT_JOBS = {
    METRIC_PIPELINE_MARKER: METRIC_PIPELINE_INIT_JOBS,
    LOG_PIPELINE_MARKER: LOG_PIPELINE_INIT_JOBS
}

METRIC_PIPELINE_SERVICES = METRIC_PIPELINE_MODULE_TO_COMPOSE_SERVICES.values()
"""Explicit list of services for docker compose
to launch for metrics pipeline"""
LOG_PIPELINE_SERVICES = LOGS_PIPELINE_MODULE_TO_COMPOSE_SERVICES.values()
"""Explicit list of services for docker compose
to launch for logs pipeline"""

PIPELINE_TO_YAML_COMPOSE = {
    METRIC_PIPELINE_MARKER: 'docker-compose-metric.yml',
    LOG_PIPELINE_MARKER: 'docker-compose-log.yml'
}

CI_COMPOSE_FILE = 'ci-compose.yml'

LOG_DIR = 'monasca-logs/' + \
          datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
BUILD_LOG_DIR = LOG_DIR + '/build/'
RUN_LOG_DIR = LOG_DIR + '/run/'
LOG_DIRS = [LOG_DIR, BUILD_LOG_DIR, RUN_LOG_DIR]


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


class BuildFailedException(Exception):
    pass


def print_logs():
    for log_dir in LOG_DIRS:
        for file_name in os.listdir(log_dir):
            file_path = log_dir + file_name
            if os.path.isfile(file_path):
                with open(file_path, 'r') as f:
                    log_contents = f.read()
                    LOG.info("#" * 100)
                    LOG.info("###### Container Logs from {0}".format(file_name))
                    LOG.info("#" * 100)
                    LOG.info(log_contents)


def set_log_dir():
    try:
        LOG.debug('Working directory: {0}'.format(os.getcwd()))
        if not os.path.exists(LOG_DIR):
            LOG.debug('Creating LOG_DIR: {0}'.format(LOG_DIR))
            os.makedirs(LOG_DIR)
        if not os.path.exists(BUILD_LOG_DIR):
            LOG.debug('Creating BUILD_LOG_DIR: {0}'.format(BUILD_LOG_DIR))
            os.makedirs(BUILD_LOG_DIR)
        if not os.path.exists(RUN_LOG_DIR):
            LOG.debug('Creating RUN_LOG_DIR: {0}'.format(RUN_LOG_DIR))
            os.makedirs(RUN_LOG_DIR)
    except Exception as e:
        LOG.error('Unexpected error {0}'.format(e))


def get_changed_files():
    if not ci_commit_range:
        return []
    LOG.debug('Execute: git diff --name-only {0}'.format(ci_commit_range))
    p = subprocess.Popen([
        'git', 'diff', '--name-only', ci_commit_range
    ], stdout=subprocess.PIPE)
    stdout, _ = p.communicate()

    if six.PY3:
        stdout = stdout.decode('utf-8')

    if p.returncode != 0:
        raise SubprocessException('git returned non-zero exit code')

    return [line.strip() for line in stdout.splitlines()]


def get_message_tags():
    if not ci_commit_range:
        return []
    LOG.debug('Execute: git log --pretty=%B -1 {0}'.format(ci_commit_range))
    p = subprocess.Popen([
        'git', 'log', '--pretty=%B', '-1', ci_commit_range
    ], stdout=subprocess.PIPE)
    stdout, _ = p.communicate()

    if six.PY3:
        stdout = stdout.decode('utf-8')

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

#    if len(dirty) > 5:
#        LOG.error('Max number of changed modules exceded.',
#                  'Please break up the patch set until a maximum of 5 modules are changed.')
#        sys.exit(1)
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
    LOG.debug('Executing build command: {0}\n'.format(' '.join(build_args)))

    p = subprocess.Popen(build_args, stdout=subprocess.PIPE, universal_newlines=True)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)

    start_time = datetime.datetime.now()
    while True:
        output = p.stdout.readline()
        print("  " + output.strip())
        return_code = p.poll()
        if return_code is not None:
            LOG.debug('Return code: {0}'.format(return_code))
            if return_code != 0:
                LOG.error('BUILD FAILED !!!')
                raise BuildFailedException('Build failed')
            if return_code == 0:
                LOG.info('Build succeeded')
            # Process has finished, read rest of the output 
            for output in p.stdout.readlines():
                LOG.debug(output.strip())
            break
        end_time = start_time + datetime.timedelta(minutes=BUILD_TIMEOUT)
        if datetime.datetime.now() >= end_time:
            LOG.error('BUILD TIMEOUT AFTER {0} MIN !!!'.format(BUILD_TIMEOUT))
            p.kill()
            raise BuildFailedException('Build timeout')


def run_push(modules, pipeline):
    if ci_branch != 'master':
        LOG.warn('Push images to Docker Hub is only allowed from master branch')
        return

    if pipeline == 'logs':
        LOG.info('Images are already pushed by metrics-pipeline, skipping!')
        return

    username = os.environ.get('DOCKER_HUB_USERNAME', None)
    password = os.environ.get('DOCKER_HUB_PASSWORD', None)

    if not password:
        LOG.info('Not DOCKER_HUB_PASSWORD, skipping!')
        LOG.info('Not pushing: {0}'.format(modules))
        return

    if username and password:
        LOG.info('Logging into docker registry...')
        login = subprocess.Popen([
            'docker', 'login',
            '-u', username,
            '--password-stdin'
        ], stdin=subprocess.PIPE)
        login.communicate(password)
        if login.returncode != 0:
            LOG.error('Docker registry login failed, cannot push!')
            sys.exit(1)

    log_dir = BUILD_LOG_DIR
    push_args = ['dbuild', '-sd', '--build-log-dir', log_dir, 'build', 'push', 'all'] + modules
    LOG.debug('Executing push command: {0}\n'.format(' '.join(push_args)))

    p = subprocess.Popen(push_args)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        LOG.error('PUSH FAILED !!!')
        sys.exit(p.returncode)


def run_readme(modules):
    if ci_branch != 'master':
        LOG.warn('Update readme to Docker Hub is only allowed from master branch')
        return

    log_dir = BUILD_LOG_DIR
    readme_args = ['dbuild', '-sd', '--build-log-dir', log_dir, 'readme'] + modules
    LOG.debug('Executing readme command: {0}\n'.format(' '.join(readme_args)))

    p = subprocess.Popen(readme_args)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        LOG.error('README FAILED !!!')
        sys.exit(p.returncode)


def update_docker_compose(modules, pipeline):
    compose_dict = load_yml(PIPELINE_TO_YAML_COMPOSE['metrics'])
    services_to_changes = METRIC_PIPELINE_MODULE_TO_COMPOSE_SERVICES.copy()

    if pipeline == 'logs':
        LOG.info('\'logs\' pipeline is enabled, including in CI run')
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

    LOG.debug("Displaying {0}\n\n{1}".format(CI_COMPOSE_FILE, yaml.dump(compose_dict, default_flow_style=False)))

    try:
        with open(CI_COMPOSE_FILE, 'w') as docker_compose:
            yaml.dump(compose_dict, docker_compose, default_flow_style=False)
    except:
        raise FileWriteException(
            'Error writing CI dictionary to {0}'.format(CI_COMPOSE_FILE)
        )


def load_yml(yml_path):
    try:
        with open(yml_path) as compose_file:
            compose_dict = yaml.safe_load(compose_file)
            return compose_dict
    except:
        raise FileReadException('Failed to read {0}'.format(yml_path))


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
        LOG.info('No modules to build.')

    update_docker_compose(pipeline_modules, pipeline)
    run_docker_keystone()
    run_docker_compose(pipeline)
    wait_for_init_jobs(pipeline)
    LOG.info('Waiting for containers to be ready 1 min...')
    time.sleep(60)
    output_docker_ps()

    cool_test_mapper = {
        'smoke': {
            METRIC_PIPELINE_MARKER: run_smoke_tests_metrics,
            LOG_PIPELINE_MARKER: lambda : LOG.info('No smoke tests for logs')
        },
        'tempest': {
            METRIC_PIPELINE_MARKER: run_tempest_tests_metrics,
            LOG_PIPELINE_MARKER: lambda : LOG.info('No tempest tests for logs')
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
    LOG.info('Modules to build: {0}'.format(modules))
    LOG.info('Modules to pull:  {0}'.format(pipeline_modules))

    # iterate over copy of all modules that are planned for the build
    # if one of them does not belong to active pipeline
    # remove from current run
    for m in modules[::]:
        if m not in pipeline_modules:
            if m in other_modules:
                LOG.info('Module {0} is not part of either pipeline, but it will be build anyway'.format(m))
                continue
            LOG.info('Module {0} does not belong to {1}, skipping'.format(m, pipeline))
            modules.remove(m)

    return modules


def get_current_init_status(docker_id):
    init_status = ['docker', 'inspect', '-f', '{{ .State.ExitCode }}:{{ .State.Status }}', docker_id]

    p = subprocess.Popen(init_status, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)

    output, err = p.communicate()

    if six.PY3:
        output = output.decode('utf-8')

    if p.wait() != 0:
        LOG.info('getting current status failed')
        return False
    status_output = output.rstrip()

    exit_code, status = status_output.split(":", 1)
    LOG.debug('Status from init-container {0}, exit_code {1}, status {2}'.format(docker_id, exit_code, status))
    return exit_code == "0" and status == "exited"


def output_docker_logs():
    LOG.info("Saving container logs at {0}".format(LOG_DIR))
    docker_names = ['docker', 'ps', '-a', '--format', '"{{.Names}}"']

    LOG.debug('Executing: {0}'.format(' '.join(docker_names)))
    p = subprocess.Popen(docker_names, stdout=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)

    output, err = p.communicate()

    if six.PY3:
        output = output.decode('utf-8')

    names = output.replace('"', '').split('\n')

    for name in names:
        if not name:
            continue

        docker_logs = ['docker', 'logs', '-t', name]
        log_name = RUN_LOG_DIR + 'docker_log_' + name + '.log'

        LOG.debug('Executing: {0}'.format(' '.join(docker_logs)))
        with open(log_name, 'w') as out:
            p = subprocess.Popen(docker_logs, stdout=out,
                                 stderr=subprocess.STDOUT)
        signal.signal(signal.SIGINT, kill)
        if p.wait() != 0:
            LOG.error('Error running docker log for {0}'.format(name))

def addtab(s):
    white = " " * 2
    return white + white.join(s.splitlines(1))

def output_docker_ps():
    docker_ps = ['docker', 'ps', '-a']

    LOG.debug('Executing: {0}'.format(' '.join(docker_ps)))
    p = subprocess.Popen(docker_ps, stdout=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)

    output, err = p.communicate()

    if six.PY3:
        output = output.decode('utf-8')
    LOG.info("Displaying all docker containers\n" + addtab(output))


def output_compose_details(pipeline):
    if pipeline == 'metrics':
        services = METRIC_PIPELINE_SERVICES
    else:
        services = LOG_PIPELINE_SERVICES
    if six.PY3:
        services = list(services)
    LOG.info('All services that are about to start: {0}'.format(', '.join(services)))


def get_docker_id(init_job):
    docker_id = ['docker-compose',
                 '-f', CI_COMPOSE_FILE,
                 'ps',
                 '-q', init_job]

    p = subprocess.Popen(docker_id, stdout=subprocess.PIPE)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)

    output, err = p.communicate()

    if six.PY3:
        output = output.decode('utf-8')

    if p.wait() != 0:
        LOG.error('error getting docker id')
        return ""
    return output.rstrip()


def wait_for_init_jobs(pipeline):
    LOG.info('Waiting 20 sec for init jobs to finish...')
    init_status_dict = {job: False for job in INIT_JOBS[pipeline]}
    docker_id_dict = {job: "" for job in INIT_JOBS[pipeline]}

    amount_succeeded = 0
    for attempt in range(INITJOBS_ATTEMPS):
        time.sleep(20)
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
            LOG.info("All init-jobs finished successfully !!!")
            break
        else:
            LOG.info("Not all init jobs have finished yet, waiting another 20 sec. " +
                     "Try " + str(attempt + 1) + " of {0}...".format(INITJOBS_ATTEMPS))
    if amount_succeeded != len(docker_id_dict):
        LOG.error("INIT-JOBS FAILED !!!")
        raise InitJobFailedException("Not all init-containers finished with exit code 0")


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
        run_push(modules_to_push, pipeline)
    else:
        LOG.info('No modules to push.')

    if modules_to_readme:
        run_readme(modules_to_readme)
    else:
        LOG.info('No READMEs to update.')

def run_docker_keystone():
    LOG.info('Running docker compose for Keystone')

    username = os.environ.get('DOCKER_HUB_USERNAME', None)
    password = os.environ.get('DOCKER_HUB_PASSWORD', None)

    if username and password:
        LOG.info('Logging into docker registry...')
        login = subprocess.Popen([
            'docker', 'login',
            '-u', username,
            '--password-stdin'
        ], stdin=subprocess.PIPE)
        login.communicate(password)
        if login.returncode != 0:
            LOG.error('Docker registry login failed!')
            sys.exit(1)


    docker_compose_dev_command = ['docker-compose',
                              '-f', 'docker-compose-dev.yml',
                              'up', '-d']

    LOG.debug('Executing: {0}'.format(' '.join(docker_compose_dev_command)))
    with open(RUN_LOG_DIR + 'docker_compose_dev.log', 'w') as out:
        p = subprocess.Popen(docker_compose_dev_command, stdout=out)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        LOG.error('DOCKER COMPOSE FAILED !!!')
        sys.exit(p.returncode)

    # print out running images for debugging purposes
    LOG.info('docker compose dev succeeded')
    output_docker_ps()


def run_docker_compose(pipeline):
    LOG.info('Running docker compose')
    output_compose_details(pipeline)

    username = os.environ.get('DOCKER_HUB_USERNAME', None)
    password = os.environ.get('DOCKER_HUB_PASSWORD', None)

    if username and password:
        LOG.info('Logging into docker registry...')
        login = subprocess.Popen([
            'docker', 'login',
            '-u', username,
            '--password-stdin'
        ], stdin=subprocess.PIPE)
        login.communicate(password)
        if login.returncode != 0:
            LOG.error('Docker registry login failed!')
            sys.exit(1)

    if pipeline == 'metrics':
        services = METRIC_PIPELINE_SERVICES
    else:
        services = LOG_PIPELINE_SERVICES

    if six.PY3:
        services = list(services)
    docker_compose_command = ['docker-compose',
                              '-f', CI_COMPOSE_FILE,
                              'up', '-d'] + services

    LOG.debug('Executing: {0}'.format(' '.join(docker_compose_command)))
    with open(RUN_LOG_DIR + 'docker_compose.log', 'w') as out:
        p = subprocess.Popen(docker_compose_command, stdout=out)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        LOG.error('DOCKER COMPOSE FAILED !!!')
        sys.exit(p.returncode)

    # print out running images for debugging purposes
    LOG.info('docker compose succeeded')
    output_docker_ps()


def run_smoke_tests_metrics():
    LOG.info('Running Smoke-tests')
    #TODO: branch as variable... use TRAVIS_PULL_REQUEST_BRANCH ?
    smoke_tests_run = ['docker', 'run',
                       '-e', 'OS_AUTH_URL=http://keystone:35357/v3',
                       '-e', 'MONASCA_URL=http://monasca:8070',
                       '-e', 'METRIC_NAME_TO_CHECK=monasca.thread_count',
                       '--net', 'monasca-docker_default',
                       '-p', '0.0.0.0:8080:8080',
                       '--name', 'monasca-docker-smoke',
                       'fest/smoke-tests:pike-latest']

    LOG.debug('Executing: {0}'.format(' '.join(smoke_tests_run)))
    p = subprocess.Popen(smoke_tests_run)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)
    if p.wait() != 0:
        LOG.error('SMOKE-TEST FAILED !!!')
        raise SmokeTestFailedException("Smoke Tests Failed")


def run_tempest_tests_metrics():
    LOG.info('Running Tempest-tests')
    tempest_tests_run = ['docker', 'run',
                         '-e', 'KEYSTONE_IDENTITY_URI=http://keystone:35357',
                         '-e', 'OS_AUTH_URL=http://keystone:35357/v3',
                         '-e', 'MONASCA_WAIT_FOR_API=true',
                         '-e', 'STAY_ALIVE_ON_FAILURE=false',
                         '--net', 'monasca-docker_default',
                         '--name', 'monasca-docker-tempest',
                         'chaconpiza/tempest-tests:test']

    LOG.debug('Executing: {0}'.format(' '.join(tempest_tests_run)))
    p = subprocess.Popen(tempest_tests_run, stdout=subprocess.PIPE, universal_newlines=True)

    def kill(signal, frame):
        p.kill()
        LOG.warn('Finished by Ctrl-c!')
        sys.exit(2)

    signal.signal(signal.SIGINT, kill)

    start_time = datetime.datetime.now()
    while True:
        output = p.stdout.readline()
        LOG.info(output.strip())
        return_code = p.poll()
        if return_code is not None:
            LOG.debug('RETURN CODE: {0}'.format(return_code))
            if return_code != 0:
                LOG.error('TEMPEST-TEST FAILED !!!')
                raise TempestTestFailedException("Tempest Tests finished but some tests failed")
            if return_code == 0:
                LOG.info('Tempest-tests succeeded')
            # Process has finished, read rest of the output 
            for output in p.stdout.readlines():
                LOG.debug(output.strip())
            break
        end_time = start_time + datetime.timedelta(minutes=TEMPEST_TIMEOUT)
        if datetime.datetime.now() >= end_time:
            LOG.error('TEMPEST-TEST TIMEOUT AFTER {0} MIN !!!'.format(TEMPEST_TIMEOUT))
            p.kill()
            raise TempestTestFailedException("Tempest Tests failed by timeout")


def handle_other(files, modules, tags, pipeline):
    LOG.error('Unsupported event type: {0}, nothing to do.'.format(ci_event_type))
    exit(2)

def print_env():

    env_vars_used = ['pipeline={0}'.format(pipeline),
                     'non_voting={0}'.format(non_voting),
                     'printlogs={0}'.format(printlogs),
                     'verbose={0}'.format(verbose),
                     'CI_EVENT_TYPE="{0}"'.format(ci_event_type),
                     'CI_BRANCH="{0}"'.format(ci_branch),
                     'CI_COMMIT_RANGE="{0}"'.format(ci_commit_range)
                     ]

    LOG.info('Variables used in CI:\n  {0}'.format('\n  '.join(env_vars_used)))

def main():
    try:
        LOG.info("DOCKER_HUB_USERNAME: {0}".format(os.environ.get('DOCKER_HUB_USERNAME', None)))
        LOG.info("DOCKER_HUB_PASSWORD: {0}".format(os.environ.get('DOCKER_HUB_PASSWORD', None)))
        print_env()

        if not pipeline or pipeline not in ('logs', 'metrics'):
            LOG.error('UNKNOWN PIPELINE: {0} !!! Choose (metrics|logs)'.format(pipeline))
            exit(2)

        set_log_dir()
        files = get_changed_files()
        LOG.info('Changed files: {0}'.format(files))
        modules = get_dirty_modules(files)
        LOG.info('Dirty modules: {0}'.format(modules))
        tags = get_message_tags()
        LOG.info('Message tags:  {0}'.format(tags))

        if tags:
            LOG.debug('Tags detected:')
            for tag in tags:
                LOG.debug('  '.format(tag))
        else:
            LOG.info('No tags detected.')

        func = {
            'cron': handle_pull_request,
            'pull_request': handle_pull_request,
            'push': handle_push
        }.get(ci_event_type, handle_other)

        func(files, modules, tags, pipeline)
    except (FileReadException, FileWriteException, SubprocessException) as ex:
        LOG.error("FAILED !!! RCA: {0}".format(ex))
        exit(1)
    except (InitJobFailedException, SmokeTestFailedException,
            TempestTestFailedException) as ex:
        if non_voting:
            LOG.warn('{0} is non voting, skipping failure'.format(pipeline))
        else:
            LOG.error("FAILED !!! RCA: {0}".format(ex))
            exit(1)
    except Exception as ex:
        LOG.error("UNKNOWN EXCEPTION !!! RCA: {0}".format(ex))
        exit(1)
    finally:
        output_docker_ps()
        output_docker_logs()
        if printlogs:
            print_logs()


if __name__ == '__main__':
    main()
