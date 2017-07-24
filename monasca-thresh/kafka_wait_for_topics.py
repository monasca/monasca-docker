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
import sys

from pykafka import KafkaClient

client = KafkaClient(hosts=os.environ.get('KAFKA_URI', 'kafka:9092'))

required_topics = os.environ.get('KAFKA_WAIT_FOR_TOPICS', '').split(',')
print('Checking for available topics:', repr(required_topics))
for req_topic in required_topics:
    if req_topic in client.topics:
        topic = client.topics[req_topic]
        if len(topic.partitions) > 0:
            print('Topic is ready:', req_topic)
        else:
            print('Topic has no partitions:', req_topic)
            sys.exit(1)
    else:
        print('Topic not found:', req_topic)
        sys.exit(1)
