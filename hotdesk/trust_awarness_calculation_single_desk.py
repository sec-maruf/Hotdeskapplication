def trust_filter_desk_amenity(desk):
    if desk['desk_number'] == desk['ergonomic_chair_number'] and desk['desk_monitor_number'] == desk['ergonomic_chair_number']:
        desk['trust_status'] = "Trusted desk! Desk amenities are properly distributed."
    else:
        desk['trust_status'] = "Untrusted desk! Desk amenities are not properly distributed."

def trust_filter_country(desk):
    if desk['country'].lower() == "germany":
        desk['trust_status_Country'] = "Trusted! The desk can be trusted for booking according to the expected country (Germany)."
    else:
        desk['trust_status_Country'] = "Untrusted! The expected country should be Germany."

def trust_filter_capacity(desk):
    try:
        capacity = int(desk['capacity'])
        desk_number = int(desk['desk_number'])
        ergonomic_chair_number = int(desk['ergonomic_chair_number'])
        desk_monitor_number = int(desk['desk_monitor_number'])
        amenities_average = (desk_number + desk_monitor_number + ergonomic_chair_number) / 3
    except ValueError:
        desk['trust_status_capacity'] = "Invalid data for capacity or desk number."
        return

    if capacity <= amenities_average and capacity >= (amenities_average * 0.5):
        desk['trust_status_capacity'] = "Trusted! The information of the capacity for this desk is fine."
    elif capacity > amenities_average:
        desk['trust_status_capacity'] = "Untrusted! The capacity for the desk is high compared to desk amenities."
    else:
        desk['trust_status_capacity'] = "Untrusted! The capacity for the desk is low compared to desk amenities."

def trust_filter_postcode(desk):
    city_postcode_mapping = {
        'essen': '45',
        'frankfurt': '60',
        'berlin': '10',
        'düsseldorf': '40',
        'munich': '80',
        'köln': '50',
        'bamberg': '96',
        'potsdam': '14',
    }
    city = desk['city_name'].lower()
    postcode = desk['post_code']

    if city in city_postcode_mapping and postcode.startswith(city_postcode_mapping[city]):
        desk['trust_status_postcode'] = "Trusted! Postcode matches the expected format for " + city.capitalize() + "."
    else:
        desk['trust_status_postcode'] = "Untrusted! Postcode does not match the expected format for " + city.capitalize() + "."

def trust_filter_desk_description(desk):
    if desk['desk_description'] == "":
        desk['trust_status_for_description'] = "Untrusted! The desk has no proper description."
    else:
        desk['trust_status_for_description'] = "Trusted! The desk has a proper description."

def trust_filter_price_for_city(desk):
    city_price_mapping = {
        'essen': 50,
        'frankfurt': 100,
        'berlin': 200,
        'düsseldorf': 150,
        'munich': 300,
        'köln': 250,
        'bamberg': 30,
        'potsdam': 60,
    }
    city = desk['city_name'].lower()
    price = float(desk['price'])

    if city in city_price_mapping:
        if price >= city_price_mapping[city]:
            desk['trust_status_price'] = "Trusted! The price is appropriate for " + city.capitalize() + "."
        else:
            desk['trust_status_price'] = "Untrusted! The price is too low for " + city.capitalize() + "."
    else:
        desk['trust_status_price'] = "No price standard for " + city.capitalize() + "."

def calculate_overall_trust(desk):
    decisions = [
        desk.get('trust_status'),
        desk.get('trust_status_Country'),
        desk.get('trust_status_capacity'),
        desk.get('trust_status_postcode'),
        desk.get('trust_status_for_description'),
        desk.get('trust_status_price'),
    ]

    trusted_count = sum(decision.startswith("Trusted") for decision in decisions if decision is not None)

    if trusted_count == len(decisions):
        desk['overall_trust_status'] = 'green'
    elif trusted_count == 0:
        desk['overall_trust_status'] = 'red'
    else:
        desk['overall_trust_status'] = 'yellow'

def apply_trust_filters_to_single_desk(desk):
    # Convert the Desk object to a dictionary if it's not already
    desk_dict = vars(desk) if not isinstance(desk, dict) else desk
    
    # Apply each trust filter to the single desk dictionary
    trust_filter_desk_amenity(desk_dict)
    trust_filter_country(desk_dict)
    trust_filter_capacity(desk_dict)
    trust_filter_postcode(desk_dict)
    trust_filter_desk_description(desk_dict)
    trust_filter_price_for_city(desk_dict)
    calculate_overall_trust(desk_dict)
    
    return desk_dict
