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

import logging
import os
import subprocess
import sys
import time

from itertools import chain


SCRIPT_PATH = os.environ.get('KAFKA_CREATE_TOPICS_SCRIPT',
                             '/kafka/bin/kafka-topics.sh')

TOPIC_STRING = os.environ.get('KAFKA_CREATE_TOPICS', '')
CONFIG_STRING = os.environ.get('KAFKA_TOPIC_CONFIG', '')

ZOOKEEPER_CONNECTION_STRING = os.environ.get('ZOOKEEPER_CONNECTION_STRING')
KAFKA_LISTEN_PORT = os.environ.get('KAFKA_LISTEN_PORT', '9092')
KAFKA_WAIT_DELAY = os.environ.get('KAFKA_WAIT_DELAY', '5')
KAFKA_WAIT_RETRIES = os.environ.get('KAFKA_WAIT_RETRIES', '24')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CaptureException(Exception):
    def __init__(self, retcode, stdout, stderr):
        super(CaptureException, self).__init__(stderr)

        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return 'CaptureException(retcode=%s, stdout=%r, stderr=%r)' % (
            self.retcode,
            self.stdout,
            self.stderr
        )


def is_kafka_running():
    p = subprocess.Popen(['netstat', '-nlt'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    out, err = p.communicate()
    if p.returncode != 0:
        raise CaptureException(p.returncode, out, err)

    lines = out.splitlines()[2:]
    for line in lines:
        tokens = line.split()
        address = tokens[3]
        if address.endswith(':%s' % KAFKA_LISTEN_PORT):
            return True

    return False


def kafka_topics(verb, args=None):
    args = [
        SCRIPT_PATH,
        '--zookeeper', ZOOKEEPER_CONNECTION_STRING,
        '--%s' % verb
    ] + (args if args is not None else [])

    logger.debug('running: %s: %r', SCRIPT_PATH, args)
    p = subprocess.Popen(args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    out, err = p.communicate()
    if p.returncode != 0:
        raise CaptureException(p.returncode, out, err)

    return out, err


def get_default_config():
    if not CONFIG_STRING:
        return {}

    default_config = {}
    for config_str in CONFIG_STRING.split(','):
        logger.debug('config_str = %r', config_str)
        k, v = map(lambda s: s.strip(), config_str.split('=', 2))
        default_config[k] = v

    return default_config


def list_topics():
    out, err = kafka_topics('list')
    return out.splitlines()


def create_topic(name, partitions, replicas, configs=None):
    if configs:
        arg_pairs = map(lambda item: ['--config', '%s=%s' % item],
                        configs.items())
        config_args = list(chain(*arg_pairs))
    else:
        config_args = []

    return kafka_topics('create', [
        '--topic', name,
        '--partitions', str(partitions),
        '--replication-factor', str(replicas),
    ] + config_args)


def create_topics(default_config, existing_topics):
    if not TOPIC_STRING:
        return

    created = []

    for topic in TOPIC_STRING.split(','):
        params = topic.split(':')
        topic_name = params.pop(0)
        configs = default_config.copy()
        partitions = None
        replicas = None

        if topic_name in existing_topics:
            logger.info('Topic already exists, will not create: %s', topic_name)
            continue

        index = 0
        for param in params:
            if '=' in param:
                # key=value arg
                k, v = map(lambda s: s.strip(), param.split('=', 2))
                configs[k] = v
            else:
                # indexed arg
                if index == 0:
                    partitions = param.strip()
                elif index == 1:
                    replicas = param.strip()

                index += 1

        if 'partitions' in configs:
            partitions = configs['partitions']
            del configs['partitions']

        if 'replicas' in configs:
            replicas = configs['replicas']
            del configs['replicas']

        if replicas is None:
            logger.error(
                'replicas not set for topic %s, it will not be created!',
                topic_name)
            continue

        if partitions is None:
            logger.error(
                'partitions not set for topic %s, it will not be created!',
                topic_name)
            continue

        logger.info('Creating topic %s: partitions=%s, replicas=%s, config=%r',
                    topic_name, partitions, replicas, configs)
        create_topic(topic_name, partitions, replicas, configs)
        created.append(topic_name)

    return created


def main():
    retries = int(KAFKA_WAIT_RETRIES)
    delay = float(KAFKA_WAIT_DELAY)

    logging.info('Waiting for Kafka to start...')
    ready = False
    for i in range(retries):
        if is_kafka_running():
            logger.info('Kafka has started, continuing...')
            ready = True
            break
        else:
            logger.info('Kafka is not ready yet (attempt %d of %d)',
                        i + 1, retries)
            time.sleep(delay)

    if not ready:
        logger.error('Kafka did not become ready in time, giving up!')
        sys.exit(1)

    default_config = get_default_config()
    logger.info('Default topic config: %r', default_config)

    existing_topics = list_topics()
    logger.info('Kafka has topics: %r', existing_topics)

    created_topics = create_topics(default_config, existing_topics)
    logger.info('Topic creation finished successfully. Created: %r',
                created_topics)

if __name__ == '__main__':
    main()
