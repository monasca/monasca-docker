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

import logging
import os
import socket
import sys
import time

from typing import Tuple

from dotmap import DotMap
from tiny_kubernetes import KubernetesAPIClient

NAMESPACE = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
TIMEOUT = int(os.environ.get('WAIT_TIMEOUT', '10'))
RETRIES = int(os.environ.get('WAIT_RETRIES', '5'))
RETRY_DELAY = float(os.environ.get('WAIT_DELAY', '5.0'))

LOG_LEVEL = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))
logging.basicConfig(level=LOG_LEVEL,
                    format='%(asctime)-15s - %(levelname)-8s - %(message)s')
logger = logging.getLogger(__name__)

pod_is_self = True


def get_current_namespace() -> str:
    global pod_is_self

    if 'NAMESPACE' in os.environ:
        pod_is_self = False
        return os.environ['NAMESPACE']

    with open(NAMESPACE, 'r') as f:
        return f.read()


def get_current_pod() -> str:
    global pod_is_self

    if 'POD_NAME' in os.environ:
        pod_is_self = False
        return os.environ['POD_NAME']

    return socket.gethostname()


def is_condition_complete(condition: DotMap) -> bool:
    return condition.type == 'Complete' and str(condition.status) == 'True'


def try_delete_job(client: KubernetesAPIClient,
                   namespace: str,
                   job: DotMap,
                   retries: int,
                   force: bool=False) -> Tuple[bool, int]:
    if 'conditions' not in job.status and not force:
        logger.info('Job has no conditions (probably still running), '
                    'will wait for it to finish: %s/%s (%d attempts '
                    'remaining)', namespace, job.metadata.name, retries)
        return False, retries - 1

    if not force:
        complete = filter(is_condition_complete, job.status.conditions)
        if not complete:
            logger.info('Job is not complete, will wait for it to finish: %s/%s '
                        '(%d attempts remaining)',
                        namespace, job.metadata.name, retries)
            return False, retries - 1

    grace_period = 0 if force else TIMEOUT
    delete_options = {'gracePeriodSeconds': grace_period}

    job_name = job.metadata.name
    pods = client.get('/api/v1/namespaces/{}/pods', namespace,
                      params={'labelSelector': 'job-name={}'.format(job_name)})
    for pod in pods['items']:
        if pod.metadata.labels.get('defunct') == 'true':
            # we could exclude this in the labelSelector, but it's probably
            # better to surface the weird pod state as much as possible
            logger.warning('Pod is marked as defunct and will not be deleted: '
                           '%s/%s', namespace, pod.metadata.name)
            continue

        del_status = client.delete(
            '/api/v1/namespaces/{}/pods/{}', namespace, pod.metadata.name,
            raise_for_status=False, json=delete_options)

        # pod delete status is insane apparently
        # it returns the full Pod on success, or a Status if fail
        # wat
        if del_status.status_code == 200:
            logger.info('Deleted job pod %s/%s', namespace, job.metadata.name)
        else:
            logger.warning('Failed to delete job pod %s/%s: %r (job: %s, %d '
                           'attempts remaining)',
                           namespace, pod.metadata.name, del_status,
                           job.metadata.name, retries)
            return False, retries - 1

    ret = client.delete('/apis/batch/v1/namespaces/{}/jobs/{}',
                        namespace, job.metadata.name,
                        json=delete_options,
                        raise_for_status=False)
    if ret.status_code == 200:
        logger.info('Deleted job %s/%s', namespace, job.metadata.name)
        return True, 0
    else:
        logger.warning(
            'Failed to delete job %s/%s: %r (%d attempts remaining)',
            namespace, job.metadata.name, ret, retries)

        return False, retries - 1


def label_defunct(client: KubernetesAPIClient, namespace: str, job: DotMap):
    job_name = job.metadata.name
    pods = client.get('/api/v1/namespaces/{}/pods', namespace,
                      params={'labelSelector': 'job-name={}'.format(job_name)})

    defunct_ops = [{
        'op': 'add',
        'path': '/metadata/labels/defunct',
        'value': 'true'
    }]

    for pod in pods['items']:
        r = client.json_patch(defunct_ops,
                              '/api/v1/namespaces/{}/pods/{}',
                              namespace, pod.metadata.name,
                              raise_for_status=False)
        if r.status_code != 200:
            # oh well
            logger.error(
                'Failed to label pod as defunct: %s/%s',
                namespace, pod.metadata.name)


def clean_orphaned(client: KubernetesAPIClient, this_app: str):
    logger.info('Cleaning orphaned job pods')

    namespace = get_current_namespace()

    selector = 'app={},job-name'.format(this_app)
    pods = client.get('/api/v1/namespaces/{}/pods', namespace,
                      params={'labelSelector': selector})

    orphaned = []
    for pod in pods['items']:
        job_name = pod.metadata.labels['job-name']
        response = client.get('/apis/batch/v1/namespaces/{}/jobs/{}',
                              namespace, job_name,
                              raise_for_status=False)
        if response.status_code != 404:
            # not orphaned
            continue

        if pod.status.phase == 'Running':
            logger.info('Orphaned pod %s is still running and will not be '
                        'deleted', pod.metadata.name)
            continue

        orphaned.append(pod)

    if not orphaned:
        logger.info('No orphaned pods to remove')
        return

    logger.info('Orphaned job pods to remove: %d (%s)',
                len(orphaned),
                ', '.join(p.metadata.name for p in orphaned))

    for pod in orphaned:
        del_status = client.delete(
            '/api/v1/namespaces/{}/pods/{}', namespace, pod.metadata.name,
            raise_for_status=False)
        if del_status.status_code == 200:
            logger.info('Orphaned pod removed successfully: %s',
                        pod.metadata.name)
        else:
            logger.warning('Could not delete orphaned pod: %r', del_status)

    logger.info('Finished cleaning orphaned pods')


def clean_jobs(client: KubernetesAPIClient, this_job: str, this_app: str):
    namespace = get_current_namespace()
    response = client.get('/apis/batch/v1/namespaces/{}/jobs', namespace,
                          params={'labelSelector': 'app={}'.format(this_app)})

    # only try to filter against None if we're running under a job
    if this_job is not None:
        jobs = filter(lambda j: j.metadata.name != this_job,
                      response['items'])
    else:
        jobs = response['items']

    items = [(item, RETRIES) for item in jobs]
    if not items:
        logger.info('No jobs to clean up!')
        return

    failed = []
    while items:
        logger.info('Removing %s jobs...', len(items))
        remaining = []
        for job, retries in items:
            success, retries = try_delete_job(client, namespace, job, retries)
            if not success:
                if retries is 0:
                    failed.append(job)
                else:
                    remaining.append((job, retries))

        if remaining:
            logger.info('Still waiting on some jobs to be removed...')
            time.sleep(RETRY_DELAY)

        items = []
        for job, retries in remaining:
            refreshed_job = client.get('/apis/batch/v1/namespaces/{}/jobs/{}',
                                       namespace, job.metadata.name)
            items.append((refreshed_job, retries))

    if failed:
        logger.warning('Some jobs did not finish in time, '
                       'they will be killed!')
        still_failed = []
        for job in failed:
            logger.info('Killing job: %s/%s', namespace, job.metadata.name)
            success, _ = try_delete_job(client, namespace, job, 0, force=True)
            if not success:
                still_failed.append(job)

        if still_failed:
            logger.warning('Not all jobs could be killed!')
            logger.warning('These jobs will be annotated with `defunct=true` '
                           'and will be ignored by future cleanup jobs. They '
                           'will need to be removed manually.')
            for job in still_failed:
                logger.warning(' - %s/%s', namespace, job.metadata.name)
                label_defunct(client, namespace, job)


def main():
    client = KubernetesAPIClient()
    client.load_auto_config()

    namespace = get_current_namespace()
    pod_name = get_current_pod()

    this_pod = client.get('/api/v1/namespaces/{}/pods/{}', namespace, pod_name)
    this_job = this_pod.metadata.labels.get('job-name', None)
    this_app = this_pod.metadata.labels.get('app')
    if not this_app:
        logger.error('The cleanup job must have an `app` label (pod: %s/%s)',
                     namespace, pod_name)
        sys.exit(1)

    clean_orphaned(client, this_app)

    clean_jobs(client, this_job, this_app)

    if pod_is_self:
        logger.info('All jobs deleted, removing cleanup job...')

        # ignore the returned status for now, since there isn't much we can do
        # about it
        if this_job:
            client.delete('/apis/batch/v1/namespaces/{}/jobs/{}',
                          namespace, this_job,
                          raise_for_status=False, json={})
            logger.info('Deleted own job: %s/%s', namespace, this_job)
        else:
            logger.debug('No (own) job to delete')

        # note: this job intentionally leaves a Completed pod behind
        # the next cleanup job will clean it up for us, meaning logs from this
        # iteration of the cleanup job will stick around

        logger.info('Done')
    else:
        logger.info('All jobs deleted successfully.')


if __name__ == '__main__':
    main()
