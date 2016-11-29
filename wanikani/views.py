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

    def get(self, request, *args, **kwargs):
        # kanji = service.get_jlpt_kanji(os.path.join(BASE_DIR, KANJI_FILE_LOCATION))
        # request.session['kanji'] = kanji
        return render(request, self.template_name)


class WanikaniChartView(TemplateView):
    template_name = 'wanikani/charts.html'

    def get(self, request, *args, **kwargs):
        jlpt_kanji = service.gather_kanji_list()
        request.session['kanji'] = jlpt_kanji
        return render(request, self.template_name)


class WanikaniComparisionView(TemplateView):
    template_name = 'wanikani/comparison.html'

    def get(self, request, *args, **kwargs):
        try:
            user_json = service.get_user_completion(request.session['api'])
        except KeyError:
            print(request.session.keys())
            return render(request, 'wanikani/index.html', {'error_message': "Couldn't find api information, please reenter it"})
        #kanji_json = service.gather_kanji_list()
        return render(request, self.template_name, {'user_json': user_json})


class ApiView(FormView):
    template_name = 'index.html'
    form_class = ApiForm
    success_url = '/thanks/'

    def form_valid(self, form):
        return super(ApiView, self).form_valid(form)


def index(request):
    return render(request, 'wanikani/index.html')


def detail(request):
    try:
        request.POST['api_key']
    except KeyError:
        return render(request, 'wanikani/index.html', {'error_message': "Couldn't find api key, please reenter it"})

    return render(request, 'wanikani/progress.html')


def progress(request):
    try:
        api_key = request.POST['api_key']
    except KeyError:
        return render(request, 'wanikani/index.html', {'error_message': "Couldn't find api key, please reenter it"})

    if not api_key or service.is_valid_api_key(api_key) is None:
        print(api_key + " testing")
        return render(request, 'wanikani/index.html', {'error_message': "Please enter a valid api key"})

    api_info = service.get_api_information(api_key)

    if 'error' in api_info:
        return render(request, 'wanikani/index.html', {'error_message': 'Couldn\'t find the given api key'})

    request.session['api'] = api_info
    return HttpResponseRedirect(reverse('wanikani:detail'))
