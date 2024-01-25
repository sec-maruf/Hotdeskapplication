# views.py

from django.shortcuts import get_object_or_404, render, redirect
import httpx

from hotdesk.trust_awareness_calculation import calculate_trust_score_and_sort
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



logger = logging.getLogger(__name__)

@solid_username_required(['hotdeskadmin'])
def desk_create_view(request):
    desk_form = DeskForm(request.POST or None)
    solid_form = SolidCredentialsForm(request.POST or None)

    if request.method == 'POST':
        if desk_form.is_valid() and solid_form.is_valid():
            desk = desk_form.save()
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
            messages.error(request, "Form validation failed")

    return render(request, 'desk_form1.html', {'desk_form': desk_form, 'solid_form': solid_form})




@solid_username_required(['hotdeskadmin'])
def desk_detail_view(request, desk_id):
    desk = get_object_or_404(Desk, pk=desk_id)
    return render(request, 'desk_detail.html', {'desk': desk})

@solid_username_required(['hotdeskadmin'])
def desk_update_view(request, desk_id):
    desk = get_object_or_404(Desk, pk=desk_id)
    desk_form = DeskForm(request.POST or None, instance=desk)
    solid_form = SolidCredentialsForm(request.POST or None)

    if request.method == 'POST':
        if desk_form.is_valid() and solid_form.is_valid():
            updated_desk = desk_form.save(commit=False)

            solid_data = solid_form.cleaned_data
            api = get_solid_api(solid_data['idp'], solid_data['username'], solid_data['password'])
            pod_file_url = f"{solid_data['pod_endpoint'].rstrip('/')}/desk{desk.id}.ttl"

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

@solid_username_required(['hotdeskadmin'])
def desk_delete_view(request, desk_id):
    desk = get_object_or_404(Desk, pk=desk_id)
    solid_form = SolidCredentialsForm(request.POST or None)

    if request.method == 'POST' and solid_form.is_valid():
        solid_data = solid_form.cleaned_data
        api = get_solid_api(solid_data['idp'], solid_data['username'], solid_data['password'])

        try:
            # Define the full URL for the desk's Solid POD file
            pod_file_url = f"{solid_data['pod_endpoint'].rstrip('/')}/desk{desk.id}.ttl"

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


@solid_username_required(['hotdeskadmin'])
def dashboard_view(request):
    desks = Desk.objects.all() # Fetch all desk instances
    return render(request, 'dashboard.html', {'desks': desks})


# views.py

from django.shortcuts import render
from .solid import SolidAPI, Auth  # Ensure to import your SolidAPI and Auth classes
from httpx import HTTPStatusError

""" def solid_file_view(request):
    auth = Auth()  # Configure this with the correct credentials
    solid_api_instance = SolidAPI(auth=auth)

    file_urls = ["https://desk1.solidcommunity.net/desk1.ttl", "https://desk2.solidcommunity.net/desk2.ttl", 
                 "https://desk3.solidcommunity.net/desk3.ttl", "https://desk4.solidcommunity.net/desk4.ttl", 
                 "https://desk5.solidcommunity.net/desk5.ttl", "https://desk6.solidcommunity.net/desk6.ttl", 
                 "https://desk7.solidcommunity.net/desk7.ttl", "https://desk8.solidcommunity.net/desk8.ttl", 
                 "https://desk9.solidcommunity.net/desk9.ttl", "https://desk10.solidcommunity.net/desk10.ttl" 
                 
                 ]
    all_desk_details = []
    error_messages = []


    for file_url in file_urls:
        try:
            response = solid_api_instance.get(file_url)
            turtle_content = response.text
            desk_details = parse_turtle_content(turtle_content)
            all_desk_details.extend(desk_details)
         
        except HTTPStatusError as e:
            error_message = f"HTTP Error for {file_url}: {e.response.status_code} - {e.response.text}"
            error_messages.append(error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred for {file_url}: {str(e)}"
            error_messages.append(error_message)
        print(desk_details[0].get("desk_id"))    

    return render(request, 'solid_file.html', {
        'all_desk_details': all_desk_details,
        'error_messages': error_messages
    })
 """
    
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


@solid_username_required(['hotdeskadmin'])
def dashboard_view(request):
    desks = Desk.objects.all() # Fetch all desk instances
    return render(request, 'dashboard.html', {'desks': desks})


# views.py





from django.shortcuts import render
from .solid import SolidAPI, Auth  # Ensure to import your SolidAPI and Auth classes
from httpx import HTTPStatusError


def solid_file_view(request):
    auth = Auth()  # Configure this with the correct credentials
    solid_api_instance = SolidAPI(auth=auth)

    file_urls = ["https://desk1.solidcommunity.net/desk1.ttl", "https://desk2.solidcommunity.net/desk2.ttl", 
                 "https://desk3.solidcommunity.net/desk3.ttl", "https://desk4.solidcommunity.net/desk4.ttl", 
                 "https://desk5.solidcommunity.net/desk5.ttl", "https://desk6.solidcommunity.net/desk6.ttl", 
                 "https://desk7.solidcommunity.net/desk7.ttl", "https://desk8.solidcommunity.net/desk8.ttl", 
                 "https://desk9.solidcommunity.net/desk9.ttl", "https://desk10.solidcommunity.net/desk10.ttl" 
                 
                 ]
    all_desk_details = []
    error_messages = []

    for file_url in file_urls:
        try:
            response = solid_api_instance.get(file_url)
            turtle_content = response.text
            desk_details = parse_turtle_content(turtle_content)
            all_desk_details.extend(desk_details)
        except HTTPStatusError as e:
            error_messages.append(f"HTTP Error for {file_url}: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            error_messages.append(f"An unexpected error occurred for {file_url}: {str(e)}")

    # Define trust factors
    trust_factors = {
        "user_ratings": 0.4,
        "frequency_of_bookings": 0.3,
        "feedback": 0.2,
        "accuracy_of_description": 0.1
    }

    # Sort desks by trust score
    sorted_desks = calculate_trust_score_and_sort(all_desk_details, trust_factors)

    return render(request, 'solid_file.html', {
        'all_desk_details': sorted_desks,
        'error_messages': error_messages
    })




