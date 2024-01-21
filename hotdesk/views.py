# views.py

from django.shortcuts import get_object_or_404, render, redirect
import httpx
from .models import Desk
from .forms import DeskForm, SolidCredentialsForm
from .rdf_utils import desk_to_rdf
from .solid import  get_solid_api  
from django.urls import reverse
from django.shortcuts import render, redirect
from .forms import DeskForm, SolidCredentialsForm
from .rdf_utils import desk_to_rdf
from django.urls import reverse
import logging
from django.contrib import messages
from solid.auth import Auth
from .decorators import solid_username_required



logger = logging.getLogger(__name__)

@solid_username_required(['hotdeskadmin'])
def desk_create_view(request):
    desk_form = DeskForm(request.POST or None)
    solid_form = SolidCredentialsForm(request.POST or None)

    if request.method == 'POST' and desk_form.is_valid() and solid_form.is_valid():
        desk = desk_form.save()
        graph = desk_to_rdf(desk)
        turtle_data = graph.serialize(format="turtle").decode("utf-8")

        solid_data = solid_form.cleaned_data

        try:
            api = get_solid_api(solid_data['idp'], solid_data['username'], solid_data['password'])
            pod_file_url = f"{solid_data['pod_endpoint'].rstrip('/')}/desk{desk.id}.ttl"
            api.create_file(pod_file_url, turtle_data, 'text/turtle')
            print("Desk POD file created successfully.")
            return redirect(reverse('hotdesk:desk-detail', kwargs={'desk_id': desk.id}))
        except Exception as e:
            print(f"Error during Solid POD interaction: {e}")
            # Handle your exceptions and possibly provide user feedback

    return render(request, 'desk_form1.html', {'desk_form': desk_form, 'solid_form': solid_form})



@solid_username_required(['hotdeskadmin'])
def desk_detail_view(request, desk_id):
    desk = get_object_or_404(Desk, pk=desk_id)
    return render(request, 'desk_detail.html', {'desk': desk})

@solid_username_required(['hotdeskadmin'])


def desk_update_view(request, desk_id):
    desk = get_object_or_404(Desk, pk=desk_id)
    form = DeskForm(request.POST or None, instance=desk)
    solid_form = SolidCredentialsForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid() and solid_form.is_valid():
            # Save the desk changes locally first
            updated_desk = form.save()

            # Convert the updated desk to RDF
            graph = desk_to_rdf(updated_desk)
            turtle_data = graph.serialize(format="turtle").decode("utf-8")

            # Get Solid credentials from the form
            solid_data = solid_form.cleaned_data
            api = get_solid_api(solid_data['idp'], solid_data['username'], solid_data['password'])
            pod_file_url = f"{solid_data['pod_endpoint'].rstrip('/')}/desk{desk.id}.ttl"
            
            try:
                # Use put_file method to update the file
                api.put_file(pod_file_url, turtle_data, 'text/turtle')
                print("Desk POD file updated successfully.")
                #messages.success(request, "Desk updated successfully on both local and Solid POD.")
                return redirect(reverse('hotdesk:desk-detail', kwargs={'desk_id': desk.id}))
            except httpx.HTTPStatusError as e:
                # If updating the Solid POD fails, rollback the local changes
                form.add_error(None, "Failed to update desk on Solid POD: " + str(e))
                updated_desk.refresh_from_db()  # Reload the original desk from the database
            except Exception as e:
                # Handle any other exceptions
                form.add_error(None, "An unexpected error occurred: " + str(e))
                updated_desk.refresh_from_db()  # Reload the original desk from the database
        # Render the form with errors if the form is not valid
        return render(request, 'desk_update.html', {'desk_form': form, 'solid_form': solid_form, 'desk_id': desk_id})

    # GET request or POST request with invalid form data
    return render(request, 'desk_update.html', {'form': form, 'solid_form': solid_form, 'desk_id': desk_id})



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
        form = SolidCredentialsForm(request.POST)
        if form.is_valid():
            # Use form.cleaned_data to access the form data safely
            solid_username = form.cleaned_data.get('username')
            solid_password = form.cleaned_data.get('password')
            idp = form.cleaned_data.get('idp')
            pod_endpoint = form.cleaned_data.get('pod_endpoint')

            # Store the credentials in the session or use them as needed
            request.session['solid_credentials'] = {
                'username': solid_username,
                'password': solid_password,
                'idp': idp,
                'pod_endpoint': pod_endpoint
            }
            return redirect('hotdesk:dashboard')
    else:
        form = SolidCredentialsForm()

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
