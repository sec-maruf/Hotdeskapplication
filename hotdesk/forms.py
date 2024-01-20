from django import forms
from .models import Desk

class DeskForm(forms.ModelForm):
    class Meta:
        model = Desk
        fields = ['desk_id', 'location', 'availability']


class SolidCredentialsForm(forms.Form):
    username = forms.CharField(max_length=100, label="Solid Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Solid Password")
    idp = forms.URLField(label="Identity Provider URL")
    pod_endpoint = forms.URLField(label="POD Endpoint URL", help_text="Enter the URL of your Solid POD.")