from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views

app_name='home'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'projects/$', TemplateView.as_view(template_name='home/projects/projects_home.html'), name='project'),
    url(r'resume/$', TemplateView.as_view(template_name='home/resume.html'), name='resume'),
    url(r'wanikani_project/$', TemplateView.as_view(template_name='home/projects/projects_wanikani.html'),
        name='wanikani_project'),
]