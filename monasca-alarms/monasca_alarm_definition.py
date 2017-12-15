#!/usr/bin/python
# coding=utf-8

# (c) Copyright 2017 Hewlett Packard Enterprise Development LP
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
'''
Loads Notifications and Alarm Definitions into Monasca. These are configured
via a yaml file which contains two sections:
notifications and alarm_definitions.
Within the sections are the notifications and alarm definitions to be
created, updated or deleted.

For the possible arguments, see the argument parser definition.

Valid fields for an Notification:
    name:
        required: true
        description:
            - The notification name
    type:
        required: true
        description:
            - The notification type
    address:
        required: true
        description:
            - The notification address, format varies with type
    period:
        required: true
        description:
            - The notification period, only valid for type WEBHOOK

Valid fields for an Alarm Definition:
    name:
        required: true
        description:
            - The alarm definition name
    description:
        required: false
        description:
            - The alarm definition description text
    expression:
        required: true
        description:
            - The alarm definition expression
    severity:
        required: false
        description:
            - The alarm definition severity, one of LOW, MEDIUM, HIGH, CRITICAL
    description:
        required: false
        description:
            - The alarm definition description text
    alarm_actions:
        required: false
        description:
            -  Array of notification names that are invoked for the transition to the ALARM state
    ok_actions:
        required: false
        description:
            -  Array of notification names that are invoked for the transition to the OK state
    severity:
        required: false
        default: "LOW"
        description:
            - The severity set for the alarm definition must be LOW, MEDIUM, HIGH or CRITICAL
    state:
        required: false
        default: "present"
        choices: [ present, absent ]
        description:
            - Whether the alarm definition should exist.  When absent, removes the alarm definition. The name
              is used to determine the alarm definition to remove
    undetermined_actions:
        required: false
        description:
            -  Array of notification names that are invoked for the transition to the UNDETERMINED state
Examle yaml file:

notifications:
  - name: Notify via Email
    type: email
    address: "root@localhost"

alarm_definitions:
  - name: "Host Status"
    description: "Alarms when the specified host is down or not reachable"
    severity: "HIGH"
    expression: "host_alive_status > 0"
    match_by:
      - "target_host"
      - "hostname"
    alarm_actions:
      - Notify via Email
    ok_actions:
      - Notify via Email
    undetermined_actions:
      - Notify via Email

  - name: "Delete me"
    expression: "http_status > 0"
    match_by:
      - "service"
    state: absent

  - name: "HTTP Status"
    description: >
      "Alarms when the specified HTTP endpoint is down or not reachable"
    severity: "HIGH"
    expression: "http_status > 0"
    match_by:
      - "service"
      - "component"
      - "hostname"
      - "url"
'''


import argparse
import os
import sys
import time
import yaml

from monascaclient import client

MONASCA_RETRIES = int(os.environ.get('MONASCA_RETRIES', '12'))
MONASCA_DELAY = float(os.environ.get('MONASCA_DELAY', '5.0'))


class MonascaLoadDefinitions(object):
    """Loads Notifications and Alarm Definitions into Monasca
    """
    def __init__(self, monasca, args):
        self._monasca = monasca
        self._args = args
        self._existing_notifications = None
        self._existing_alarm_definitions = None
        self._verbose = args['verbose']

    def _get_existing_notifications(self):
        if self._existing_notifications is None:
            self._existing_notifications = self._monasca.notifications.list()
        return self._existing_notifications

    def _print_message(self, message):
        if self._verbose:
            print(message)

    def run(self, data_file):
        try:
            with open(data_file) as f:
                yaml_text = f.read()
        except IOError:
            raise Exception('Unable to open yaml alarm definitions: {}'
                            .format(data_file))

        yaml_data = yaml.safe_load(yaml_text)

        if 'notifications' not in yaml_data:
            raise Exception('No notifications section in {}'.format(data_file))

        processed, changed, notification_ids = self._do_notifications(yaml_data['notifications'])
        self._print_message(
            '{:d} Notifications Processed {:d} Notifications Changed'
            .format(processed, changed))

        if 'alarm_definitions' not in yaml_data:
            raise Exception('No alarm_definitions section in {}'
                            .format(data_file))

        processed, changed = self.do_alarm_definitions(yaml_data['alarm_definitions'], notification_ids)
        self._print_message(
            '{:d} Alarm Definitions Processed {:d} Alarm Definitions Changed'
            .format(processed, changed))

    def _do_notifications(self, notifications):
        processed = 0
        changed = 0
        notification_ids = {}
        for notification in notifications:
            processed += 1
            if self._process_notification(notification, notification_ids):
                changed += 1
        return processed, changed, notification_ids

    def _process_notification(self, notification, notification_ids):
        name = notification['name']

        self._print_message('Processing notification "{}"'.format(name))
        # Get existing notifications
        notifications = {notification['name']: notification for notification in self._get_existing_notifications()}

        if notification.get('state', 'present') == 'absent':
            if name not in notifications.keys():
                self._print_message('Notification "{}" with state absent already does not exist'.format(name))
                return False

            self._print_message('Deleting notification "{}"'.format(name))

            # TODO Delete could be tricky if this notification is used by alarm definitions
            resp = self._monasca.notifications.delete(notification_id=notifications[name]['id'])
            if resp.status_code == 204:
                self._print_message('Successfully deleted notification "{}"'.format(name))
                return True
            else:
                raise Exception(str(resp.status_code) + resp.text)
        else:  # Only other option is state=present

            def_kwargs = {'name': name, 'type': notification['type'].upper(), 'address': notification['address'],
                          'period': notification.get('period', 0)}

            if name in notifications.keys():
                existing = notifications[name]
                fields = ['type', 'address', 'period']
                matches = True
                for field in fields:
                    if existing[field] != def_kwargs[field]:
                        self._print_message('Notification "{}": Field {} value "{}" does not match expected "{}"'.format(
                              name, field, existing[field], def_kwargs[field]))
                        matches = False
                if matches:
                    self._print_message('Notification "{}" has no changes'.format(name))
                    notification_ids[name] = existing['id']
                    return False
                def_kwargs['notification_id'] = notifications[name]['id']
                self._print_message('Patching Notification "{}"'.format(name))
                body = self._monasca.notifications.patch(**def_kwargs)
            else:
                self._print_message('Creating Notification "{}"'.format(name))
                body = self._monasca.notifications.create(**def_kwargs)

            if 'id' in body:
                notification_ids[name] = body['id']
                return True
            else:
                raise Exception(body)

    def _get_existing_alarm_definitions(self):
        if self._existing_alarm_definitions is None:
            self._existing_alarm_definitions = self._monasca.alarm_definitions.list()
        return self._existing_alarm_definitions

    def do_alarm_definitions(self, definitions, notification_ids):
        processed = 0
        changed = 0
        for definition in definitions:
            processed += 1
            if self._process_alarm_definition(definition, notification_ids):
                changed += 1
        return processed, changed

    def _map_notifications(self, actions, notification_ids):
        mapped = []
        for action in actions:
            if action not in notification_ids:
                raise Exception("Unrecognized Notification {}".format(action))
            mapped.append(notification_ids[action])
        mapped.sort()
        return mapped

    def _process_alarm_definition(self, definition, notification_ids):
        name = definition['name']
        self._print_message('Processing Alarm Definition "{}"'.format(name))

        expression = definition['expression']

        # Get existing definitions
        definitions = {definition['name']: definition for definition in self._get_existing_alarm_definitions()}

        if definition.get('state', 'present') == 'absent':
            if name not in definitions.keys():
                self._print_message('Alarm Definition "{}" with state absent already does not exist'.format(name))
                return False

            resp = self._monasca.alarm_definitions.delete(alarm_id=definitions[name]['id'])
            if resp.status_code == 204:
                self._print_message('Successfully deleted Alarm Definition "{}"'.format(name))
                return True
            else:
                raise Exception(str(resp.status_code) + resp.text)
        else:  # Only other option is state=present

            alarm_actions = self._map_notifications(definition.get('alarm_actions', []), notification_ids)
            ok_actions = self._map_notifications(definition.get('ok_actions', []), notification_ids)
            undetermined_actions = self._map_notifications(definition.get('undetermined_actions', []), notification_ids)
            def_kwargs = {'name': name, 'description': definition.get('description', ''), 'expression': expression,
                          'match_by': definition.get('match_by', []), 'severity': definition.get('severity', 'LOW').upper(),
                          'alarm_actions': alarm_actions, 'ok_actions': ok_actions,
                          'undetermined_actions': undetermined_actions}

            if name in definitions.keys():
                existing = definitions[name]
                # Make sure the actions are in sorted order so the compare works.
                existing['alarm_actions'].sort()
                existing['ok_actions'].sort()
                existing['undetermined_actions'].sort()
                fields = ['name', 'description', 'expression', 'match_by', 'severity', 'alarm_actions', 'ok_actions', 'undetermined_actions']
                matches = True
                for field in fields:
                    if existing[field] != def_kwargs[field]:
                        self._print_message('Alarm Definition "{}": Field {} value "{}" does not match expected "{}"'.format(
                              name, field, existing[field], def_kwargs[field]))
                        matches = False
                if matches:
                    self._print_message('Alarm Definition "{}" has no changes'.format(name))
                    return False
                def_kwargs['alarm_id'] = definitions[name]['id']

                self._print_message('Patching Alarm Definition "{}"'.format(name))
                body = self._monasca.alarm_definitions.patch(**def_kwargs)
            else:
                self._print_message('Creating Alarm Definition "{}"'.format(name))
                body = self._monasca.alarm_definitions.create(**def_kwargs)

            if 'id' in body:
                return True
            else:
                raise Exception(body)


def _get_parser():
    parser = argparse.ArgumentParser(
        prog='monasca_alarm_definition',
        # description=__doc__.strip(),
        add_help=False,
        # formatter_class=HelpFormatter,
        formatter_class=lambda prog: argparse.HelpFormatter(
            prog,
            max_help_position=29)
    )

    # Global arguments
    parser.add_argument('-h', '--help',
                        action='store_true',
                        help=argparse.SUPPRESS)

    parser.add_argument('-v', '--verbose',
                        default=False, action="store_true",
                        help="Print more verbose output.")

    parser.add_argument('-k', '--insecure',
                        default=False,
                        action='store_true',
                        help="Explicitly allow the client to perform "
                        "\"insecure\" SSL (https) requests. The server's "
                        "certificate will not be verified against any "
                        "certificate authorities. "
                        "This option should be used with caution.")

    parser.add_argument('--cert-file',
                        help='Path of certificate file to use in SSL '
                        'connection. This file can optionally be '
                        'prepended with the private key.')

    parser.add_argument('--key-file',
                        help='Path of client key to use in SSL connection. '
                        'This option is not necessary if your key is'
                        ' prepended to your cert file.')

    parser.add_argument('--os-cacert',
                        default=_env('OS_CACERT'),
                        help='Specify a CA bundle file to use in verifying'
                        ' a TLS (https) server certificate. Defaults to'
                        ' env[OS_CACERT]. Without either of these, the'
                        ' client looks for the default system CA'
                        ' certificates.')

    parser.add_argument('--timeout',
                        default=600,
                        help='Number of seconds to wait for a response.')

    parser.add_argument('--os-username',
                        default=_env('OS_USERNAME'),
                        help='Defaults to env[OS_USERNAME].')

    parser.add_argument('--os_username',
                        help=argparse.SUPPRESS)

    parser.add_argument('--os-password',
                        default=_env('OS_PASSWORD'),
                        help='Defaults to env[OS_PASSWORD].')

    parser.add_argument('--os_password',
                        help=argparse.SUPPRESS)

    parser.add_argument('--os-project-id',
                        default=_env('OS_PROJECT_ID'),
                        help='Defaults to env[OS_PROJECT_ID].')

    parser.add_argument('--os_project_id',
                        help=argparse.SUPPRESS)

    parser.add_argument('--os-project-name',
                        default=_env('OS_PROJECT_NAME'),
                        help='Defaults to env[OS_PROJECT_NAME].')

    parser.add_argument('--os_project_name',
                        help=argparse.SUPPRESS)

    parser.add_argument('--os-domain-id',
                        default=_env('OS_DOMAIN_ID'),
                        help='Defaults to env[OS_DOMAIN_ID].')

    parser.add_argument('--os_domain_id',
                        help=argparse.SUPPRESS)

    parser.add_argument('--os-domain-name',
                        default=_env('OS_DOMAIN_NAME'),
                        help='Defaults to env[OS_DOMAIN_NAME].')

    parser.add_argument('--os_domain_name',
                        help=argparse.SUPPRESS)

    parser.add_argument('--os-project-domain-name',
                        default=_env('OS_PROJECT_DOMAIN_NAME'),
                        help='Defaults to env[OS_PROJECT_DOMAIN_NAME].')

    parser.add_argument('--os-user-domain-name',
                        default=_env('OS_USER_DOMAIN_NAME'),
                        help='Defaults to env[OS_USER_DOMAIN_NAME].')

    parser.add_argument('--os-auth-url',
                        default=_env('OS_AUTH_URL'),
                        help='Defaults to env[OS_AUTH_URL].')

    parser.add_argument('--os-region-name',
                        default=_env('OS_REGION_NAME'),
                        help='Defaults to env[OS_REGION_NAME].')

    parser.add_argument('--os_region_name',
                        help=argparse.SUPPRESS)

    parser.add_argument('--os-auth-token',
                        default=_env('OS_AUTH_TOKEN'),
                        help='Defaults to env[OS_AUTH_TOKEN].')

    parser.add_argument('--os_auth_token',
                        help=argparse.SUPPRESS)

    parser.add_argument('--os-no-client-auth',
                        default=_env('OS_NO_CLIENT_AUTH'),
                        action='store_true',
                        help="Do not contact keystone for a token. "
                             "Defaults to env[OS_NO_CLIENT_AUTH].")

    parser.add_argument('--monasca-api-url',
                        default=_env('MONASCA_API_URL'),
                        help='Defaults to env[MONASCA_API_URL].')

    parser.add_argument('--monasca_api_url',
                        help=argparse.SUPPRESS)

    parser.add_argument('--monasca-api-version',
                        default=_env(
                            'MONASCA_API_VERSION',
                            default='2_0'),
                        help='Defaults to env[MONASCA_API_VERSION] or 2_0')

    parser.add_argument('--monasca_api_version',
                        help=argparse.SUPPRESS)

    parser.add_argument('--os-service-type',
                        default=_env('OS_SERVICE_TYPE'),
                        help='Defaults to env[OS_SERVICE_TYPE].')

    parser.add_argument('--os_service_type',
                        help=argparse.SUPPRESS)

    parser.add_argument('--os-endpoint-type',
                        default=_env('OS_ENDPOINT_TYPE'),
                        help='Defaults to env[OS_ENDPOINT_TYPE].')

    parser.add_argument('--os_endpoint_type',
                        help=argparse.SUPPRESS)

    parser.add_argument('--definitions-file',
                        help='YAML file of Notifications and Alarm Definitions')

    return parser


def _env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.
    """
    for var in vars:
        value = os.environ.get(var)
        if value:
            return value
    return kwargs.get('default', '')


def get_monasca_client(args, keystone_args):
    api_url = args.get('monasca_api_url')
    if not api_url:
        raise Exception('Error: monasca_api_url is required')

    monasca = client.Client(args['api_version'], api_url, **keystone_args)
    print('Using Monasca at {}'.format(api_url))

    for i in range(MONASCA_RETRIES):
        try:
            # just make an api call that should always succeed
            monasca.notifications.list(limit=1)
            print('Monasca API is ready')
            return monasca

        # I don't feel like spending an hour digging through osc-lib's
        # spaghetti to figure out what exceptions list() raises, so, yeah.
        except Exception as ex:
            print('Attempt {} of {} to {} failed: {}'.format(
                i, MONASCA_RETRIES, api_url, ex.message
            ))

            if i < MONASCA_RETRIES - 1:
                time.sleep(MONASCA_DELAY)

    print('Could not connect to Monasca after {} retries, '
          'giving up!'.format(MONASCA_RETRIES))
    raise Exception('could not connect to monasca at {}', api_url)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = _get_parser()
    args = parser.parse_args(args)

    if not args or args.help:
        parser.print_help()
        return

    if not args.os_username and not args.os_auth_token:
        raise Exception("You must provide a username via"
                        " either --os-username or env[OS_USERNAME]"
                        " or a token via --os-auth-token or"
                        " env[OS_AUTH_TOKEN]")

    if not args.os_password and not args.os_auth_token:
        raise Exception("You must provide a password via"
                        " either --os-password or env[OS_PASSWORD]"
                        " or a token via --os-auth-token or"
                        " env[OS_AUTH_TOKEN]")

    all_keystone_kwargs = {
        'auth_url': args.os_auth_url,
        'username': args.os_username,
        'password': args.os_password,
        'project_id': args.os_project_id,
        'project_name': args.os_project_name,
        'project_domain_name': args.os_project_domain_name,
        'user_domain_name': args.os_user_domain_name,
        'domain_id': args.os_domain_id,
        'domain_name': args.os_domain_name
    }
    ks_kwargs = {k: v for k, v in all_keystone_kwargs.iteritems() if v}

    kwargs = {
        'keystone_kwargs': ks_kwargs,
        'keystone_token': args.os_auth_token,
        'endpoint_type': args.os_endpoint_type,
        'os_cacert': args.os_cacert,
        'service_type': args.os_service_type,
        'insecure': args.insecure,
        'monasca_api_url': args.monasca_api_url,
        'api_version': args.monasca_api_version,
        'verbose': args.verbose
    }

    if not args.definitions_file:
        raise Exception('--definitions-file argument is required')

    monasca = get_monasca_client(kwargs, ks_kwargs)

    definition = MonascaLoadDefinitions(monasca, kwargs)
    definition.run(args.definitions_file)


if __name__ == "__main__":
    main()
