from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views

app_name='home'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'projects/$', TemplateView.as_view(template_name='projects.html')),
]