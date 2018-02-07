from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView
from django.urls import reverse

from wanikani import service
from wanikani.error import error_text_constants
from wanikani.forms import ApiForm

import traceback
import logging

logger = logging.getLogger(__name__)


# Create your views here.
class IndexView(TemplateView):
    logger.debug("Called IndexView method: redirecting to homepage")
    template_name = 'wanikani/index.html'
    context_object_name = 'wanikani'


class WanikaniDetailView(DetailView):
    template_name = 'wanikani/progress.html'
    context_object_name = 'api_info'
    logger.info("About to render progress")

    def get(self, request, *args, **kwargs):
        if 'api' not in request.session:
            return redirect_due_to_error(request, error_text_constants.API_KEY_404)

        return render(request, self.template_name)


class WanikaniChartView(TemplateView):
    template_name = 'wanikani/charts.html'

    def get(self, request, *args, **kwargs):
        if 'api' not in request.session:
            return redirect_due_to_error(request, error_text_constants.API_KEY_404)

        request.session['api'] = request.session['api']
        return render(request, self.template_name)


class WanikaniComparisionView(TemplateView):
    template_name = 'wanikani/comparison.html'

    def get(self, request, *args, **kwargs):
        if 'api' not in request.session:
            return redirect_due_to_error(request, error_text_constants.API_KEY_404)
        #kanji_json = service.gather_kanji_list()
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
    if 'api' not in request.session:
        return redirect_due_to_error(request, error_text_constants.API_KEY_404)
    return render(request, 'wanikani/progress.html')


def progress(request):
    try:
        api_key = request.POST['api_key']
    except KeyError:
        return redirect_due_to_error(request, error_text_constants.API_KEY_404)

    if not api_key or not service.is_valid_api_key(api_key):
        logger.debug("testing result is {0}".format(service.is_valid_api_key(api_key)))
        return redirect_due_to_error(request, error_text_constants.API_KEY_MALFORMED)

    api_info = service.create_user_info(api_key)
    if api_info == 'error':
        return redirect_due_to_error(request, error_text_constants.API_KEY_BAD_CALL)

    request.session['api'] = api_info
    logger.debug("in method progress")
    return HttpResponseRedirect(reverse('wanikani:detail'))


def redirect_due_to_error(request, reason):
    messages.add_message(request, messages.ERROR,
                         error_text_constants.APIErrorMessage.construct_api_error_message(reason))
    return redirect('wanikani:index')
