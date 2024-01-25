from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import BookingForm
from hotdesk.models import Desk
from .models import Booking
from hotdesk.rdf_utils import parse_turtle_content
from hotdesk.solid import get_solid_api
from httpx import HTTPStatusError
from hotdesk.solid import SolidAPI, Auth

from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking
from hotdesk.models import Desk
from .forms import BookingForm
from hotdesk.solid import get_solid_api
from hotdesk.rdf_utils import booking_to_calendar_event

def book_desk_view(request, desk_id):
    desk = get_object_or_404(Desk, pk=desk_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.desk = desk
            booking.save()
            
            # Saving booking info to user's Solid POD
            calendar_event = booking_to_calendar_event(booking)
            solid_data = request.session.get('solid_credentials')
            api = get_solid_api(solid_data['idp'], solid_data['username'], solid_data['password'])
            pod_file_url = f"{solid_data['pod_endpoint'].rstrip('/')}/bookings/{booking.id}.ics"
            api.create_file(pod_file_url, calendar_event, 'text/calendar')

            return redirect('dashboard')
    else:
        form = BookingForm()

    return render(request, 'booking_desk/book_desk.html', {'form': form, 'desk': desk})


