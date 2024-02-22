# forms.py
import datetime
import json
from django import forms
from .models import Desk
from django.core.exceptions import ValidationError
from datetime import datetime

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
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), 
        required=False, 
        label='Start Date'
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), 
        required=False, 
        label='End Date'
    )
    class Meta:
        model = Desk
        fields = [
            'desk_id', 
            'desk_description',
            'capacity', 
            'country', 
            'city_name',  
            'price', 
            'post_code', 
            'desk_number', 
            'ergonomic_chair_number', 
            'desk_monitor_number'
        ]


    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Ensure the datetime class is correctly imported to use fromisoformat
        existing_date_ranges = json.loads(self.instance.date_times) if self.instance.date_times else []

        for date_range in existing_date_ranges:
            if isinstance(date_range, str):
                existing_start = existing_end = datetime.fromisoformat(date_range)
            elif isinstance(date_range, list) and len(date_range) == 2:
                existing_start_str, existing_end_str = date_range
                existing_start = datetime.fromisoformat(existing_start_str)
                existing_end = datetime.fromisoformat(existing_end_str)
            else:
                # Handle unexpected format
                raise ValidationError(f"Invalid date range format in existing bookings: {date_range}")

            if start_date <= existing_end and end_date >= existing_start:
                raise ValidationError("The selected date range conflicts with an existing booking.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Only proceed with date logic if both dates are provided
        if self.cleaned_data.get('start_date') and self.cleaned_data.get('end_date'):
            start_date = self.cleaned_data.get('start_date').isoformat()
            end_date = self.cleaned_data.get('end_date').isoformat()

            # Load existing date ranges or initialize to an empty list
            date_ranges = json.loads(instance.date_times) if instance.date_times else []

            # Append the new date range and save back as JSON
            date_ranges.append([start_date, end_date])
            instance.date_times = json.dumps(date_ranges)
        else:
            # If no dates are provided, set date_times to None or an empty string, depending on your model's field configuration
            # This example assumes your model allows null values for date_times
            instance.date_times = None

        if commit:
            instance.save()

        return instance


       


class SolidCredentialsForm(forms.Form):
    username = forms.CharField(max_length=100, label="Solid Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Solid Password")
    idp = forms.URLField(label="Identity Provider URL")
    pod_endpoint = forms.URLField(label="POD Endpoint URL",  help_text="Enter the URL of your Solid POD.")


class SolidLoginForm(forms.Form):
    username = forms.CharField(max_length=100, label="Solid Username")
    password = forms.CharField(widget=forms.PasswordInput(), label="Solid Password")

 