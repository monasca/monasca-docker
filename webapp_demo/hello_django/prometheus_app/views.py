# prometheus_app/views.py
from django.shortcuts import render
from django.views.generic import TemplateView

from prometheus_client import start_http_server, Counter

CLICK_TIME = Counter('count_click_time', 'Description of counter')

# Start up the server to expose the metrics.
start_http_server(8005)


# Create your views here.
class HomePageView(TemplateView):
    def get(self, request, **kwargs):
        context = {
                'current_value': 0.0
            }
        if request.GET.get('click_btn'):
            CLICK_TIME.inc(amount=1)
            current_value = CLICK_TIME.__dict__.get('_value').__dict__.values()[0]
            context = {
                'current_value': current_value
            }
            # print value
        return render(request, 'index.html', context=context)
