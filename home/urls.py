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
    url(r'puzzler_project/$', TemplateView.as_view(template_name='home/projects/udacity_vr/projects_puzzler.html'),
        name='puzzler_project'),
    url(r'night_at_the_museum_project/$',
        TemplateView.as_view(template_name='home/projects/udacity_vr/projects_night_at_the_museum.html'),name='night_at_the_museum_project'),
]