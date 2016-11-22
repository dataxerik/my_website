from django.shortcuts import render
from django.views.generic import TemplateView
from wanikani.forms import ApiForm
from wanikani import service
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.urls import reverse


# Create your views here.
class IndexView(TemplateView):
    template_name = 'wanikani/index.html'
    content_object_name = 'wanikani'


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
        return render(request, 'wanikani/index.html')
    api_info = service.get_api_information(api_key)
    request.session['_api'] = request.POST
    return HttpResponseRedirect(reverse('wanikani:detail'))
