# forms.py
from django import forms
from .models import Desk

CITY_CHOICES = [
    ('essen', 'Essen'),
    ('berlin', 'Berlin'),
    ('munich', 'Munich'),
    ('düsseldorf', 'Düsseldorf'),
    ('köln', 'Köln'),
    ('bamberg', 'Bamberg'),
    ('potsdam', 'Potsdam'),
    ('frankfurt', 'Frankfurt'),
    
]

class DeskForm(forms.ModelForm):
    city_name = forms.ChoiceField(choices=CITY_CHOICES, required=True, label='City')
    post_code = forms.CharField(max_length=5, required=True)
    desk_description = forms.CharField(required=False)
    start_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M'))
    end_time = forms.DateTimeField(required=False, widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M'))
    class Meta:
        model = Desk
        fields = [
            'desk_id', 
            'desk_description',
            'capacity', 
            'country', 
            'city_name', 
            'start_time', 
            'end_time', 
            'price', 
            'post_code', 
            'desk_number', 
            'ergonomic_chair_number', 
            'desk_monitor_number'
        ]


class SolidCredentialsForm(forms.Form):
    username = forms.CharField(max_length=100, label="Solid Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Solid Password")
    idp = forms.URLField(label="Identity Provider URL")
    pod_endpoint = forms.URLField(label="POD Endpoint URL",  help_text="Enter the URL of your Solid POD.")


class SolidLoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Solid Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Solid Password")

 