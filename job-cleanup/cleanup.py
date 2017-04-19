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
import socket
import sys
import time

# NOTE: requires version >= 2.0.0a1
from kubernetes import client, config
from kubernetes.client import V1DeleteOptions


NAMESPACE = '/var/run/secrets/kubernetes.io/serviceaccount/namespace'
TIMEOUT = 10
RETRIES = 24
RETRY_DELAY = 5.0

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


def try_delete_job(api, batch_api, namespace, job, retries):
    if not job.status.conditions:
        print('Job has no conditions (probably still running), '
              'will wait for it to finish: %s/%s (%d attempts '
              'remaining)' % (namespace, job.metadata.name, retries))
        return False, retries - 1

    complete = filter(is_condition_complete, job.status.conditions)
    if not complete:
        print('Job is not complete, will wait for it to finish: %s/%s (%d '
              'attempts remaining)' % (namespace, job.metadata.name, retries))
        return False, retries - 1

    delete_options = V1DeleteOptions(propagation_policy='Foreground')

    pods = api.list_namespaced_pod(namespace,
                                   label_selector='job-name=%s' % job.metadata.name,
                                   timeout_seconds=TIMEOUT)
    for pod in pods.items:
        del_status = api.delete_namespaced_pod(pod.metadata.name, namespace,
                                               delete_options,
                                               grace_period_seconds=TIMEOUT)
        # pod delete status is insane apparently
        if del_status.code is None or del_status.code == 200:
            print('Deleted job pod %s/%s' % (namespace, job.metadata.name))
        else:
            print('Failed to delete job pod %s/%s: %r (job: %s, %d attempts '
                  'remaining' % (namespace, pod.metadata.name, del_status,
                                 job.metadata.name, retries), file=sys.stderr)
            return False, retries - 1

    ret = batch_api.delete_namespaced_job(job.metadata.name, namespace,
                                          delete_options,
                                          grace_period_seconds=TIMEOUT)
    if ret.code == 200:
        print('Deleted job %s/%s' % (namespace, job.metadata.name))
        return True, 0
    else:
        print('Failed to delete job %s/%s: %r (%d attempts '
              'remaining)' % (namespace, job.metadata.name, ret, retries),
              file=sys.stderr)

        return False, retries - 1


def main():
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    bv1 = client.BatchV1Api()

    namespace = get_current_namespace()
    pod_name = get_current_pod()

    pod = v1.read_namespaced_pod(pod_name, namespace)
    app = pod.metadata.labels['app']
    this_job = pod.metadata.labels.get('job-name', None)

    jobs = bv1.list_namespaced_job(namespace,
                                   label_selector='app=%s' % app,
                                   timeout_seconds=TIMEOUT)
    items = [(item, RETRIES) for item in jobs.items]
    if not items:
        print('No jobs to clean up!')
        sys.exit(0)

    failed = []
    while items:
        print('Removing %d jobs...' % len(items))
        remaining = []
        for job, retries in items:
            if pod_is_self and this_job and job.metadata.name == this_job:
                # don't delete this job yet
                continue

            success, retries = try_delete_job(v1, bv1, namespace, job, retries)
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
            refreshed_job = bv1.read_namespaced_job(job.metadata.name,
                                                    namespace)
            items.append((refreshed_job, retries))

    if failed:
        print('Some jobs could not be deleted:', file=sys.stderr)
        for job in failed:
            print(' - %s' % job.metadata.name)
        sys.exit(1)

    if pod_is_self:
        print('All jobs deleted, removing cleanup job...')
        # ignore the returned status for now, since there isn't much we can do
        # about it
        bv1.delete_namespaced_job(pod.metadata.labels['job-name'],
                                  namespace, V1DeleteOptions())
        v1.delete_namespaced_pod(pod.metadata.name, namespace, V1DeleteOptions())
    else:
        print('All jobs deleted successfully.')


if __name__ == '__main__':
    main()
