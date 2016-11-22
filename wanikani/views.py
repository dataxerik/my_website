from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from wanikani.forms import ApiForm
from wanikani import service
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.urls import reverse


# Create your views here.
class IndexView(TemplateView):
    template_name = 'wanikani/index.html'
    context_object_name = 'wanikani'

class WanikaniDetailView(DetailView):
    template_name = 'wanikani/progress.html'
    context_object_name = 'api_info'

    def get(self, request):
        print(request.session.keys())
        return render(request, self.template_name)



class ApiView(FormView):
    template_name = 'index.html'
    form_class = ApiForm
    success_url = '/thanks/'

    def form_valid(self, form):
        return super(ApiView, self).form_valid(form)


def index(request):
    return render(request, 'wanikani/index.html')


def detail(request):
    return render(request, 'wanikani/progress.html')


def progress(request):
    api_key = request.POST['api_key']
    if not api_key or service.is_valid_api_key(api_key) is None:
        print(api_key + " testing")
        return render(request, 'wanikani/index.html', {'error_message': "Please enter a valid api key"})


    api_info = service.get_api_information(api_key)

    if 'error' in api_info:
        return render(request, 'wanikani/index.html', {'error_message': 'Couldn\'t find the given api key'})

    request.session['api'] = api_info
    print(request.session['api'])
    return HttpResponseRedirect(reverse('wanikani:detail'))