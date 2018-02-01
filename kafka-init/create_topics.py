#!/usr/bin/env python
# coding=utf-8

# (C) Copyright 2017 Hewlett Packard Enterprise Development LP
# Copyright 2017 Fujitsu LIMITED
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

from itertools import chain


SCRIPT_PATH = os.environ.get('KAFKA_CREATE_TOPICS_SCRIPT',
                             '/kafka/bin/kafka-topics.sh')
TOPIC_STRING = os.environ.get('KAFKA_CREATE_TOPICS', '')
CONFIG_STRING = os.environ.get('KAFKA_TOPIC_CONFIG', '')
ZOOKEEPER_CONNECTION_STRING = os.environ.get('ZOOKEEPER_CONNECTION_STRING')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

subprocess_env = os.environ.copy()
if 'JMX_PORT' in subprocess_env:
    del subprocess_env['JMX_PORT']
if 'KAFKA_JMX_OPTS' in subprocess_env:
    del subprocess_env['KAFKA_JMX_OPTS']


class CaptureException(Exception):
    def __init__(self, retcode, stdout, stderr):
        super(CaptureException, self).__init__(stderr)

        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return 'CaptureException(retcode={!s}, stdout={!r}, stderr={!r})' \
            .format(
                self.retcode,
                self.stdout,
                self.stderr
        )


def kafka_topics(verb, args=None):
    args = [
        SCRIPT_PATH,
        '--zookeeper', ZOOKEEPER_CONNECTION_STRING,
        '--{}'.format(verb)
    ] + (args if args is not None else [])

    logger.debug('running: %s: %r', SCRIPT_PATH, args)
    p = subprocess.Popen(args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         env=subprocess_env)

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
        arg_pairs = map(lambda item: ['--config', '{0}={1}'.format(*item)],
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
    existing_topics_config = {}

    for topic in TOPIC_STRING.split(','):
        params = topic.split(':')
        topic_name = params.pop(0)
        configs = default_config.copy()
        partitions = None
        replicas = None
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
        if topic_name in existing_topics:
            existing_topics_config[topic_name] = configs
            continue
        logger.info('Creating topic %s: partitions=%s, replicas=%s, config=%r',
                    topic_name, partitions, replicas, configs)
        create_topic(topic_name, partitions, replicas, configs)
        created.append(topic_name)

    return created, existing_topics_config


def update_topic_configs(existing_topics_config):
    for topic, config in existing_topics_config.iteritems():
        logger.info('Topic %s already exists, ensuring configuration options match up',
                    topic)
        logger.info('Attempting to set configuration options to %s', config)
        topic_describe_output, err = kafka_topics("describe", ["--topic", topic])
        topic_describe = topic_describe_output.split('\n')[0]
        current_config = {}
        if "Configs" in topic_describe:
            topic_config = topic_describe.split("Configs:")[1]
            if topic_config:
                for config_str in topic_config.split(","):
                    k, v = map(lambda s: s.strip(), config_str.split('=', 2))
                    current_config[k] = v

        configs_to_delete = filter(lambda x: x not in config.keys(), current_config.keys())
        if configs_to_delete:
            logger.info('Removing topic configuration options %s from topic %s', configs_to_delete, topic)
            config_input = []
            for config_opt in configs_to_delete:
                config_input.append("--delete-config")
                config_input.append(config_opt)
            kafka_topics("alter", ["--topic", topic] + config_input)

        if config:
            logger.info('Adding/Updating topic configuration options %s to topic %s', config.keys(), topic)
            arg_pairs = map(lambda item: ['--config', '{0}={1}'.format(*item)],
                            config.items())
            config_args = list(chain(*arg_pairs))
            kafka_topics("alter", ["--topic", topic] + config_args)


def main():
    default_config = get_default_config()
    logger.info('Default topic config: %r', default_config)

    existing_topics = list_topics()
    logger.info('Kafka has topics: %r', existing_topics)

    created_topics, existing_topics_config = create_topics(default_config, existing_topics)
    logger.info('Topic creation finished successfully. Created: %r',
                created_topics)

    update_topic_configs(existing_topics_config)


if __name__ == '__main__':
    main()
