from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404, render_to_response
from django.urls import reverse
from django.views import generic
from .models import Game

class IndexView(generic.ListView):
    template_name = 'games/index.html'
    context_object_name = 'game_list'

    def get_queryset(self):
        return Game.objects.order_by('name')[:5]

class DetailView(generic.DetailView):
    model = Game
    template_name = 'games/detail.html'
