# views.py

import datetime
import json
from uuid import uuid4
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, render, redirect
import httpx

from hotdesk.trust_awarness_calculation_single_desk import apply_trust_filters_to_single_desk

#from hotdesk.trust_awareness_calculation import calculate_trust_score_and_sort
from .models import Desk
from .forms import DeskForm, SolidCredentialsForm

from .solid import  get_solid_api  
from django.urls import reverse
from django.shortcuts import render, redirect
from .forms import DeskForm, SolidCredentialsForm, SolidLoginForm
from .rdf_utils import desk_to_rdf, parse_turtle_content
from django.urls import reverse
import logging
from django.contrib import messages
from .decorators import solid_username_required
from .trust_awareness_calculation import apply_trust_filters, trust_filter_capacity, trust_filter_country, trust_filter_desk_amenity, trust_filter_desk_description,  trust_filter_postcode, trust_filter_price_for_city
from django.db import transaction

logger = logging.getLogger(__name__)
allowed_usernames = ['hotdeskadmin','desk1','desk2','desk3','desk4','desk5','desk6','desk7','desk8','desk9','desk10']

""" def desk_create_view(request):
    desk_form = DeskForm(request.POST or None)
    solid_form = SolidCredentialsForm(request.POST or None)

    if request.method == 'POST':
        if desk_form.is_valid() and solid_form.is_valid():
            desk = desk_form.save()
            solid_username = request.session.get('solid_credentials', {}).get('username')
            desk.solid_username = solid_username  # Set the Solid username
            graph = desk_to_rdf(desk)
            turtle_data = graph.serialize(format="turtle").decode("utf-8")
            solid_data = solid_form.cleaned_data

            try:
                api = get_solid_api(solid_data['idp'], solid_data['username'], solid_data['password'])
                pod_file_url = f"{solid_data['pod_endpoint'].rstrip('/')}/desk{desk.id}.ttl"
                response = api.create_file(pod_file_url, turtle_data, 'text/turtle')
                if response.status_code == 201:
                    messages.success(request, "Desk POD file created successfully.")
                else:
                    messages.error(request, f"Unexpected response from server: {response.status_code} - {response.content}")
                return redirect(reverse('hotdesk:desk-detail', kwargs={'desk_id': desk.id}))
            except Exception as e:
                messages.error(request, f"Error during Solid POD interaction: {e}")
        else:
            print("Desk Form Errors:", desk_form.errors)
            print("Solid Form Errors:", solid_form.errors)
            messages.error(request, "Form validation failed")  
          

    return render(request, 'desk_form1.html', {'desk_form': desk_form, 'solid_form': solid_form}) """

@solid_username_required(allowed_usernames)
def desk_create_view(request):
    desk_form = DeskForm(request.POST or None)
    solid_form = SolidCredentialsForm(request.POST or None)

    if request.method == 'POST' and desk_form.is_valid() and solid_form.is_valid():
        try:
            with transaction.atomic():
                # Create the desk instance and save to get an ID
                desk = desk_form.save(commit=False)
                solid_username = request.session.get('solid_credentials', {}).get('username')
                desk.solid_username = solid_username
                desk.save()  # Now the desk has an ID

                # Serialize desk information to Turtle format for Solid POD
                graph = desk_to_rdf(desk)
                turtle_data = graph.serialize(format="turtle").decode("utf-8")
                solid_data = solid_form.cleaned_data

                # Interact with the Solid POD
                api = get_solid_api(solid_data['idp'], solid_data['username'], solid_data['password'])
                pod_file_url = f"{solid_data['web_id'].rstrip('/')}/desk{desk.id}.ttl"
                response = api.create_file(pod_file_url, turtle_data, 'text/turtle')

                if response.status_code != 201:
                    raise Exception(f"Unexpected response from server: {response.status_code} - {response.content}")

                messages.success(request, "Desk and POD file created successfully.")
                return redirect(reverse('hotdesk:desk-detail', kwargs={'desk_id': desk.id}))

        except Exception as e:
            messages.error(request, f"Error during desk or Solid POD interaction: {e}")
            # Note: In case of failure, the transaction will rollback including the desk save operation.

    else:
        messages.error(request, "Form validation failed")

    return render(request, 'desk_form1.html', {'desk_form': desk_form, 'solid_form': solid_form})


@solid_username_required(allowed_usernames)
def desk_detail_view(request, desk_id):
    desk = get_object_or_404(Desk, pk=desk_id)
    desk_dict = model_to_dict(desk)
    adjusted_desk_dict = apply_trust_filters_to_single_desk(desk_dict)
    return render(request, 'desk_detail.html', {'desk': adjusted_desk_dict})



@solid_username_required(allowed_usernames)
def desk_update_view(request, desk_id):
    desk = get_object_or_404(Desk, pk=desk_id)
    desk_form = DeskForm(request.POST or None, instance=desk)
    solid_form = SolidCredentialsForm(request.POST or None)
    if request.method == 'POST':
        if desk_form.is_valid() and solid_form.is_valid():
            updated_desk = desk_form.save(commit=False)

            solid_data = solid_form.cleaned_data
            api = get_solid_api(solid_data['idp'], solid_data['username'], solid_data['password'])
            pod_file_url = f"{solid_data['web_id'].rstrip('/')}/desk{desk.id}.ttl"

            graph = desk_to_rdf(updated_desk)
            turtle_data = graph.serialize(format="turtle").decode("utf-8")

            try:
                api.put_file(pod_file_url, turtle_data, 'text/turtle')
                updated_desk.save()  # Commit the changes to the database
                messages.success(request, "Desk updated successfully on both local and Solid POD.")
                
                return redirect(reverse('hotdesk:desk-detail', kwargs={'desk_id':desk.id}))
            except httpx.HTTPStatusError as e:
                messages.error(request, "Failed to update desk on Solid POD: " + str(e))
                updated_desk.refresh_from_db()
            except Exception as e:
                messages.error(request, "An unexpected error occurred: " + str(e))
                updated_desk.refresh_from_db()
        else:
            print("Desk Form Errors:", desk_form.errors)
            print("Solid Form Errors:", solid_form.errors)
            messages.error(request, "Form validation failed") 
    else:
        # Instantiate the forms for a GET request
        desk_form = DeskForm(instance=desk)
        solid_form = SolidCredentialsForm()
               

    return render(request, 'desk_update.html', {
        'desk_form': desk_form,
        'solid_form': solid_form,
        'desk_id': desk_id
    })




@solid_username_required(['hotdeskadmin','desk1','desk2','desk3','desk4','desk5','desk6','desk7','desk8','desk9','desk10'])
def desk_delete_view(request, desk_id):
    desk = get_object_or_404(Desk, pk=desk_id)
    solid_form = SolidCredentialsForm(request.POST or None)

    if request.method == 'POST' and solid_form.is_valid():
        solid_data = solid_form.cleaned_data
        api = get_solid_api(solid_data['idp'], solid_data['username'], solid_data['password'])

        try:
            # Define the full URL for the desk's Solid POD file
            pod_file_url = f"{solid_data['web_id'].rstrip('/')}/desk{desk.id}.ttl"

            # Attempt to delete the file from the Solid POD
            api.delete(pod_file_url)
            print("Desk POD file deleted successfully.")

            # If successful, delete the desk from the local database
            desk.delete()
            messages.success(request, "Desk deleted successfully.")
            return redirect('hotdesk:desk-create')  # Redirect to the list of desks
        except httpx.HTTPStatusError as e:
            messages.error(request, f"HTTP error occurred: {e}")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    return render(request, 'desk_confirm_delete.html', {'desk': desk, 'solid_form': solid_form})




def solid_login_view(request):
    if request.method == 'POST':
        form = SolidLoginForm(request.POST)
        if form.is_valid():
            # Use form.cleaned_data to access the form data safely
            solid_username = form.cleaned_data.get('username')
            solid_password = form.cleaned_data.get('password')

            # Store the credentials in the session or use them as needed
            request.session['solid_credentials'] = {
                'username': solid_username,
                'password': solid_password,
            }
            return redirect('hotdesk:dashboard')
    else:
        form = SolidLoginForm()

    return render(request, 'solid_login.html', {'form': form})


def solid_logout_view(request):
    # Clear the session data, including Solid credentials
    request.session.flush()

    # Redirect to the login page or another appropriate page
    return redirect('hotdesk:solid-login')


""" @solid_username_required(['hotdeskadmin'])
def dashboard_view(request):
    desks = Desk.objects.all() # Fetch all desk instances
    return render(request, 'dashboard.html', {'desks': desks}) """


    
def solid_login_view(request):
    if request.method == 'POST':
        form = SolidLoginForm(request.POST)
        if form.is_valid():
            # Use form.cleaned_data to access the form data safely
            solid_username = form.cleaned_data.get('username')
            solid_password = form.cleaned_data.get('password')

            # Store the credentials in the session or use them as needed
            request.session['solid_credentials'] = {
                'username': solid_username,
                'password': solid_password,
            }
            return redirect('hotdesk:dashboard')
    else:
        form = SolidLoginForm()

    return render(request, 'solid_login.html', {'form': form})


def solid_logout_view(request):
    # Clear the session data, including Solid credentials
    request.session.flush()

    # Redirect to the login page or another appropriate page
    return redirect('hotdesk:solid-login')
@solid_username_required(['hotdeskadmin','desk1','desk2','desk3','desk4','desk5','desk6','desk7','desk8','desk9','desk10'])
def dashboard_view(request):
    solid_username = request.session.get('solid_credentials', {}).get('username')
    desks = Desk.objects.filter(solid_username=solid_username)  # Filter desks by Solid username
    return render(request, 'dashboard.html', {'desks': desks})


# views.py

from django.shortcuts import render
from .solid import SolidAPI, Auth  # Ensure to import your SolidAPI and Auth classes
from httpx import HTTPStatusError


def desk_fetching_from_solid(request):
    auth = Auth()  # Configure this with the correct credentials
    solid_api_instance = SolidAPI(auth=auth)

    file_urls = ["https://desk1.solidcommunity.net/public/desk3.ttl","https://desk1.solidcommunity.net/public/desk6.ttl","https://desk1.solidcommunity.net/public/desk5.ttl","https://desk1.solidcommunity.net/public/desk7.ttl"]
    all_desk_details = []
    error_messages = []
   # booked_desk_ids = get_booked_desk_ids()
    for file_url in file_urls:
        try:
            response = solid_api_instance.get(file_url)
            turtle_content = response.text
            desk_details = parse_turtle_content(turtle_content)
            all_desk_details.extend(desk_details)
            
            request.session['all_desk_details'] = all_desk_details  # Store in session
            request.session.save()
        except HTTPStatusError as e:
            if e.response.status_code != 404:
               error_messages.append(f"HTTP Error for {file_url}: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            error_messages.append(f"An unexpected error occurred for {file_url}: {str(e)}")
    # Sort desks by trust score
    #sorted_desks = calculate_trust_score_and_sort(all_desk_details, trust_factors)
    trust_status_desks = trust_filter_desk_amenity(all_desk_details)
    trust_status_country= trust_filter_country(all_desk_details)
    trust_status_capacity= trust_filter_capacity(all_desk_details)
    trust_status_city_postcode= trust_filter_postcode(all_desk_details)
    trust_status_description= trust_filter_desk_description(all_desk_details)
    trust_status_price_for_city = trust_filter_price_for_city(all_desk_details)
    total_trust_decision = apply_trust_filters(all_desk_details)
    
    return render(request, 'desk_fetch.html', {
        'all_desk_details': trust_status_desks,'all_desk_details':trust_status_country, 'all_desk_details':trust_status_capacity,
       'all_desk_details': trust_status_city_postcode,'all_desk_details': trust_status_description, 
       'all_desk_details': trust_status_price_for_city,'all_desk_details': total_trust_decision,'error_messages': error_messages
    }) 



def deskbook(request):
    desk_id = request.POST.get('desk_id') or request.GET.get('desk_id')

    if not desk_id:
        messages.error(request, "No desk ID provided.")
        return redirect('hotdesk:solid-file')

    desk = get_object_or_404(Desk, desk_id=desk_id)
    book_desk_form = DeskForm(request.POST or None, instance=desk)
    book_solid_form = SolidCredentialsForm(request.POST or None)

    if request.method == 'POST':
        if book_desk_form.is_valid() and book_solid_form.is_valid():
            # Temporarily save the form to access cleaned_data, but don't commit to the database yet
            temp_desk = book_desk_form.save(commit=False)
            solid_data = book_solid_form.cleaned_data
            
            # Extract the current booking dates
            current_start_date = book_desk_form.cleaned_data.get('start_date')
            current_end_date = book_desk_form.cleaned_data.get('end_date')
            
            # Only proceed if both dates are provided
            if current_start_date and current_end_date:
                # Convert dates to ISO format for serialization
                current_start_date_iso = current_start_date.isoformat()
                current_end_date_iso = current_end_date.isoformat()

                # Serialize only the current booking dates
                # Assuming a modified version of desk_to_rdf that accepts start and end dates
                turtle_data = desk_to_rdf(temp_desk, current_start_date_iso, current_end_date_iso).serialize(format="turtle").decode("utf-8")
                
                try:
                    api = get_solid_api(solid_data['idp'], solid_data['username'], solid_data['password'])
                    pod_file_url = f"{solid_data['web_id'].rstrip('/')}/booking{desk.desk_id}.ttl"

                    response = api.create_file(pod_file_url, turtle_data, 'text/turtle')
                    if response.status_code == 201:
                        # Save the desk instance to the database after successful POD file creation
                        book_desk_form.save()  # Now actually commit the form data to the database
                        messages.success(request, "Book POD file created successfully.")
                        return redirect('hotdesk:booking_confirmation', desk_id=desk.desk_id)
                    else:
                        messages.error(request, f"Unexpected response from server: {response.status_code} - {response.content}")
                except Exception as e:
                    messages.error(request, f"Error during Solid POD interaction: {e}")
            else:
                messages.error(request, "Both start and end dates must be provided.")
        else:
            print("Desk Form Errors:", book_desk_form.errors)
            print("Solid Form Errors:", book_solid_form.errors)
            messages.error(request, "Form validation failed")

    return render(request, 'solid_cred_login_booking.html', {'book_desk_form': book_desk_form, 'book_solid_form': book_solid_form, 'desk': desk})



def booking_confirmation(request, desk_id):
    desk = get_object_or_404(Desk, desk_id=desk_id)
    return render(request, 'booking_confirmation.html', {'desk': desk})
