from django.conf.urls import url
from . import views

app_name='wanikani'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^progress/$', views.progress, name='progress'),
    url(r'^details/$', views.WanikaniDetailView.as_view(), name='detail')
]