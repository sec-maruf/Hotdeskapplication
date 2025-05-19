🚀 Project Description
This project addresses the challenges of centralized data control by leveraging Solid PODs (Personal Online Datastores) for decentralized storage. Users retain ownership of their desk booking data while interacting with a trust-aware system that evaluates desk reliability based on:

Amenities distribution (ergonomic chairs, monitors)

Geographical consistency (country, city, postcode)

Capacity vs. amenities ratio

Pricing alignment with city standards

Built with Django and integrated with Solid’s authentication and RDF data models, this application exemplifies the future of privacy-focused, user-centric web apps.

✨ Key Features
Decentralized Data Storage: Desk data stored in user-controlled Solid PODs.

Trust Awareness System: Automated evaluation of desks using:

Amenities verification

Location validation (Germany-focused)

Capacity-to-amenities ratio checks

Postcode/city consistency

Pricing benchmarks

CRUD Operations: Create, read, update, and delete desks with Solid authentication.

RDF Data Representation: Data serialization in Turtle format for interoperability.

Responsive UI: Bootstrap-powered interface for seamless cross-device use.

🛠️ Technology Stack
Backend: Django 4.2

Decentralization: Solid Protocol, Solid PODs

Data Handling: RDF, rdflib 6.0+

Authentication: WebID, Solid-OIDC

Frontend: Bootstrap 5, Django Templates

Tools: Docker, Git, GitHub Actions
