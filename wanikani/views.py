from django.shortcuts import render
from django.views import generic


# Create your views here.
class IndexView(generic.ListView):
    template_name='wanikani/index.html'
    content_object_name='wanikani'

def index(request):
    return render(request, 'wanikani/index.html')

def progress(request):
    return render(request, 'wanikani/progress/html')