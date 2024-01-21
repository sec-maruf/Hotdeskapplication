
#rdf_utils.py
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
    graph.add((desk_uri, EX.location, Literal(desk.location, datatype=XSD.string)))
    graph.add((desk_uri, EX.availability, Literal(desk.availability, datatype=XSD.boolean)))

    return graph
