from django import forms

class ApiForm(forms.Form):
    api_key = forms.CharField()

