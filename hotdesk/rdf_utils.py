# rdf_utils.py
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD
from .models import Desk

# Define your namespace
EX = Namespace("http://example.org/")

def desk_to_rdf(desk: Desk) -> Graph:
    graph = Graph()
    
    # Create a URIRef for the desk
    desk_uri = URIRef(f"http://example.org/desk/{desk.desk_id}")

    # Add triples to the graph
    graph.add((desk_uri, RDF.type, EX.Desk))
    graph.add((desk_uri, EX.desk_id, Literal(desk.desk_id, datatype=XSD.string)))
    graph.add((desk_uri, EX.desk_description, Literal(desk.desk_description, datatype=XSD.string)))
    graph.add((desk_uri, EX.capacity, Literal(desk.capacity, datatype=XSD.integer)))
    graph.add((desk_uri, EX.location, Literal(desk.location, datatype=XSD.string)))
    graph.add((desk_uri, EX.availability, Literal(desk.availability, datatype=XSD.boolean)))
    graph.add((desk_uri, EX.start_time, Literal(desk.start_time.isoformat(), datatype=XSD.dateTime)))
    graph.add((desk_uri, EX.end_time, Literal(desk.end_time.isoformat(), datatype=XSD.dateTime)))
    graph.add((desk_uri, EX.price, Literal(desk.price, datatype=XSD.decimal)))
    graph.add((desk_uri, EX.user_ratings, Literal(desk.user_ratings, datatype=XSD.float)))
    graph.add((desk_uri, EX.frequency_of_bookings, Literal(desk.frequency_of_bookings, datatype=XSD.integer)))
    graph.add((desk_uri, EX.feedback, Literal(desk.feedback, datatype=XSD.string)))
    graph.add((desk_uri, EX.accuracy_of_description, Literal(desk.accuracy_of_description, datatype=XSD.float)))

    return graph

def parse_turtle_content(turtle_content):
    g = Graph()
    g.parse(data=turtle_content, format='turtle')

    details_list = []

    for desk_uri in g.subjects(RDF.type, EX.Desk):
        details = {
            'desk_id': str(desk_uri.split('/')[-1]),
            'desk_name': str(g.value(desk_uri, EX.desk_id, default="")),
            'desk_description': str(g.value(desk_uri, EX.desk_description, default="")),
            'capacity': str(g.value(desk_uri, EX.capacity, default="")),
            'location': str(g.value(desk_uri, EX.location, default="")),
            'availability': str(g.value(desk_uri, EX.availability, default="")),
            'start_time': str(g.value(desk_uri, EX.start_time, default="")),
            'end_time': str(g.value(desk_uri, EX.end_time, default="")),
            'price': str(g.value(desk_uri, EX.price, default="")),
            'user_ratings': str(g.value(desk_uri, EX.user_ratings, default="")),
            'frequency_of_bookings': str(g.value(desk_uri, EX.frequency_of_bookings, default="")),
            'feedback': str(g.value(desk_uri, EX.feedback, default="")),
            'accuracy_of_description': str(g.value(desk_uri, EX.accuracy_of_description, default="")),
        }
        details_list.append(details)

    return details_list


def format_datetime(dt):
    """Formats a datetime object to the iCalendar date-time format."""
    return dt.strftime("%Y%m%dT%H%M%S")

def booking_to_calendar_event(booking):
    calendar_event = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your Company//Your Product//EN\n"
    calendar_event += "BEGIN:VEVENT\n"
    calendar_event += f"UID:booking-{booking.id}@yourdomain.com\n"
    calendar_event += f"DTSTAMP:{format_datetime(booking.start_time)}\n"
    calendar_event += f"DTSTART:{format_datetime(booking.start_time)}\n"
    calendar_event += f"DTEND:{format_datetime(booking.end_time)}\n"
    calendar_event += f"SUMMARY:Booking for desk {booking.desk.desk_id}\n"

    if booking.desk.location:
        calendar_event += f"LOCATION:{booking.desk.location}\n"

    calendar_event += f"DESCRIPTION:Booking: {booking.desk.desk_description}\n"
    calendar_event += "END:VEVENT\n"
    calendar_event += "END:VCALENDAR\n"

    return calendar_event
