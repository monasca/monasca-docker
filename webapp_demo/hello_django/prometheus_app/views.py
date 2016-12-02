# prometheus_app/views.py
from django.shortcuts import render
from django.views.generic import TemplateView

from prometheus_client import start_http_server, Counter

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
