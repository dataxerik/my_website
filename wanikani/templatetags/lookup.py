from django.template.defaulttags import register
from django.template import Library
import json


@register.filter
def lookup(dict_, key_):
    return dict_.get(key_)
