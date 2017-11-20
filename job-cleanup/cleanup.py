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
import socket
import sys
import time

from kubernetes import KubernetesAPIClient


NAMESPACE = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
TIMEOUT = float(os.environ.get('WAIT_TIMEOUT', '10'))
RETRIES = int(os.environ.get('WAIT_RETRIES', '24'))
RETRY_DELAY = float(os.environ.get('WAIT_DELAY', '5.0'))

USE_KUBE_CONFIG = os.environ.get('USE_KUBE_CONFIG', False)

pod_is_self = True


def get_current_namespace():
    global pod_is_self

    if 'NAMESPACE' in os.environ:
        pod_is_self = False
        return os.environ['NAMESPACE']

    with open(NAMESPACE, 'r') as f:
        return f.read()


def get_current_pod():
    global pod_is_self

    if 'POD_NAME' in os.environ:
        pod_is_self = False
        return os.environ['POD_NAME']

    return socket.gethostname()


def is_condition_complete(condition):
    return condition.type == 'Complete' and str(condition.status) == 'True'


def try_delete_job(client, namespace, job, retries, force=False):
    if 'conditions' not in job.status and not force:
        print('Job has no conditions (probably still running), '
              'will wait for it to finish: {}/{} ({} attempts '
              'remaining)'.format(namespace, job.metadata.name, retries))
        return False, retries - 1

    if not force:
        complete = filter(is_condition_complete, job.status.conditions)
        if not complete:
            print('Job is not complete, will wait for it to finish: {}/{} ({} '
                  'attempts remaining)'.format(namespace, job.metadata.name, retries))
            return False, retries - 1

    grace_period = 0 if force else TIMEOUT
    delete_options = {'propagationPolicy': 'Foreground',
                      'gracePeriodSeconds': grace_period}

    job_name = job.metadata.name
    pods = client.get('/api/v1/namespaces/{}/pods', namespace,
                      params={'labelSelector': 'job-name={}'.format(job_name)})
    for pod in pods['items']:
        if pod.metadata.labels.get('defunct') == 'true':
            # we could exclude this in the labelSelector, but it's probably
            # better to surface the weird pod state as much as possible
            print('Pod is marked as defunct and will not be deleted: '
                  '{}/{}'.format(namespace, pod.metadata.name))
            continue

        del_status = client.delete('/api/v1/namespaces/{}/pods/{}',
                                   namespace, pod.metadata.name,
                                   raise_for_status=False,
                                   json=delete_options)

        # pod delete status is insane apparently
        # it returns the full Pod on success, or a Status if fail
        # wat
        if del_status.status_code == 200:
            print('Deleted job pod {}/{}'.format(namespace, job.metadata.name))
        else:
            print('Failed to delete job pod {}/{}: {!r} (job: {}, {} attempts '
                  'remaining'.format(namespace, pod.metadata.name, del_status,
                                 job.metadata.name, retries), file=sys.stderr)
            return False, retries - 1

    ret = client.delete('/apis/batch/v1/namespaces/{}/jobs/{}',
                        namespace, job.metadata.name,
                        json=delete_options,
                        raise_for_status=False)
    if ret.status_code == 200:
        print('Deleted job {}/{}'.format(namespace, job.metadata.name))
        return True, 0
    else:
        print('Failed to delete job {}/{}: {!r} ({} attempts '
              'remaining)'.format(namespace, job.metadata.name, ret, retries),
              file=sys.stderr)

        return False, retries - 1


def label_defunct(client, namespace, job):
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
            print('Failed to label pod as defunct: '
                  '{}/{}'.format(namespace, pod.metadata.name),
                  file=sys.stderr)


def main():
    client = KubernetesAPIClient()
    if USE_KUBE_CONFIG:
        client.load_kube_config()
    else:
        client.load_cluster_config()

    namespace = get_current_namespace()
    pod_name = get_current_pod()

    pod = client.get('/api/v1/namespaces/{}/pods/{}', namespace, pod_name)

    app = pod.metadata.labels['app']
    component = pod.metadata.labels.get('component', None)
    this_job = pod.metadata.labels.get('job-name', None)

    if pod_is_self and this_job:
        selector = 'app={},component!={}'.format(app, component)
    else:
        selector = 'app={}'.format(app)

    jobs = client.get('/apis/batch/v1/namespaces/{}/jobs', namespace,
                      params={'labelSelector': selector})

    items = [(item, RETRIES) for item in jobs['items']]
    if not items:
        print('No jobs to clean up!')
        sys.exit(0)

    for job, retries in items:
        job.pprint()

    failed = []
    while items:
        print('Removing {} jobs...'.format(len(items)))
        remaining = []
        for job, retries in items:
            success, retries = try_delete_job(client, namespace, job, retries)
            if not success:
                if retries is 0:
                    failed.append(job)
                else:
                    remaining.append((job, retries))

        if remaining:
            print('Still waiting on some jobs to be removed...')
            time.sleep(RETRY_DELAY)

        items = []
        for job, retries in remaining:
            refreshed_job = client.get('/apis/batch/v1/namespaces/{}/jobs/{}',
                                       namespace, job.metadata.name)
            items.append((refreshed_job, retries))

    if failed:
        print('Some jobs did not finish in time, they will be killed!',
              file=sys.stderr)
        still_failed = []
        for job in failed:
            print('Killing job: {}/{}'.format(namespace, job.metadata.name))
            success, _ = try_delete_job(client, namespace, job, 0, force=True)
            if not success:
                still_failed.append(job)

        if still_failed:
            print('Not all jobs could be killed!', file=sys.stderr)
            print('These jobs will be annotated with `defunct=true` and will '
                  'be ignored by future cleanup jobs. They will need to be '
                  'removed manually.', file=sys.stderr)
            for job in still_failed:
                print(' - {}/{}'.format(namespace, job.metadata.name))
                label_defunct(client, namespace, job)

            sys.exit(1)

    if pod_is_self:
        print('All jobs deleted, removing cleanup job...')

        # ignore the returned status for now, since there isn't much we can do
        # about it
        client.delete('/apis/batch/v1/namespaces/{}/jobs/{}',
                      namespace, pod.metadata.labels['job-name'],
                      raise_for_status=False, json={})

        # we invert the ordering of delete job / delete pod here
        # if we get killed too quickly, we mainly want the job to be deleted
        # so no new jobs can spawn
        client.delete('/api/v1/namespaces/{}/pods/{}',
                      namespace, pod.metadata.name,
                      raise_for_status=False, json={})
    else:
        print('All jobs deleted successfully.')


if __name__ == '__main__':
    main()
