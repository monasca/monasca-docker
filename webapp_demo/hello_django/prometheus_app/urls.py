# howdy/urls.py
from django.conf.urls import url
from prometheus_app import views

urlpatterns = [
    url(r'^$', views.HomePageView.as_view()),
]