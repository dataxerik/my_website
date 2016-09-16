from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404, render_to_response
from django.urls import reverse
from django.views import generic

def index(request):
    return render_to_response('home/index.html')
'''
class IndexView(generic.View):
    template_name = 'home/index.html'
'''