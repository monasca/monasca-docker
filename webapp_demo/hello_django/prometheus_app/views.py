#!/usr/bin/env python
# coding=utf-8

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

# prometheus_app/views.py
from django.shortcuts import render
from django.views.generic import TemplateView

from prometheus_client import Counter
from prometheus_client import start_http_server

CLICK_TIME = Counter('button_click_counter', 'Counter for a button',
                     ['version', 'button_name'])
CLICK_TIME.labels(version='v1.0', button_name='START')

# Start up the server to expose the metrics.
start_http_server(8005)


# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        context = {
            'current_value': 0.0
        }
        if request.GET.get('click_btn'):
            CLICK_TIME.labels(version='v1.0', button_name='START').inc(
                amount=1)
            current_value = CLICK_TIME.__dict__.get('_metrics').values()[
                0].__dict__.get('_value').__dict__.values()[0]
            context = {
                'current_value': current_value
            }
        return render(request, 'index.html', context=context)
