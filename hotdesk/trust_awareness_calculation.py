def trust_filter_desk_amenity(desks):
    for desk in desks:
        if desk['desk_number'] == desk['ergonomic_chair_number'] and desk['desk_monitor_number'] == desk['ergonomic_chair_number']:
            desk['trust_status'] = "Trusted desk! Desk amenities is properly distributed "
        else:
            desk['trust_status'] = "Desk amenities is not properly distributed"  
    return desks
              
            
    
def trust_filter_country(desks):
    for desk in desks:
        if desk['country'] == "Germany"  or desk['country'] == "germany":
            desk['trust_status_Country']= "Trusted! desk can be trused for booking according to expected country (Germany)" 
        else:
            desk['trust_status_Country']= "Untrusted! expected country should be Germany"   
    return desks

def trust_filter_capacity(desks):
    for desk in desks:
        # Ensure the values are integers
        try:
            capacity = int(desk['capacity'])
            desk_number = int(desk['desk_number'])
            ergonomic_chair_number= int(desk['ergonomic_chair_number'])
            desk_monitor_number= int(desk['desk_monitor_number'])
            amenities_average= (desk_number+desk_monitor_number+ergonomic_chair_number)/3
        except ValueError:
            # Handle the case where the conversion fails
            desk['trust_status_capacity'] = "Invalid data for capacity or desk number"
            continue

        if capacity <= amenities_average and capacity>= (amenities_average*.5):
            desk['trust_status_capacity'] = "Trusted! Because the information of the capacity for this desk is fine."
        elif capacity> amenities_average:
            desk['trust_status_capacity'] = "Untrusted! the capacity for desk is high comparing of desk amenities"
        else:    
            desk['trust_status_capacity'] = "Untrusted! the capacity for desk is low comparing of desk amenities"
    return desks

def trust_filter_postcode(desks):
    city_postcode_mapping = {
        'essen': '45',  # Example: Chemnitz postcodes start with '09'
        'frankfurt': '60',
        'berlin': '10',
        'düsseldorf': '40',
        'munich': '80',
        'köln': '50',
        'bamberg': '96',
        'potsdam': '14',
    }

    for desk in desks:
        city = desk['city_name'].lower()
        postcode = desk['post_code']

        # Check if the city is in the mapping and if the postcode matches the expected format
        if city in city_postcode_mapping and postcode.startswith(city_postcode_mapping[city]):
            desk['trust_status_postcode'] = "Trusted! Postcode matches the expected format for " + city.capitalize()
        else:
            desk['trust_status_postcode'] = "Untrusted! Postcode does not match the expected format for " + city.capitalize()

    return desks

def trust_filter_desk_description(desks):
    for desk in desks:
        if desk['desk_description'] == "":
            desk['trust_status_for_description'] = "Untrusted! the desk has no proper description."
        else:
            desk['trust_status_for_description'] = "Trusted! the desk has  proper description."  
    return desks

def trust_filter_desk_timedetails(desks):
    for desk in desks:
        # Check if start_time or end_time are either None or empty strings
        if not desk['start_time'] or not desk['end_time']:
            desk['trust_status_for_timedetails'] = "Untrusted! The desk has no proper time details of availability."
        else:
            desk['trust_status_for_timedetails'] = "Trusted! The desk has proper time details of availability."
    return desks



def trust_filter_price_for_city(desks):
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

    for desk in desks:
        city = desk['city_name'].lower()  # Ensure city names are compared in lowercase
        price = float(desk['price'])  # Convert price to float for comparison

        # Check if the price is trusted for the city
        if city in city_price_mapping:
            if price >= city_price_mapping[city]:
                desk['trust_status_price'] = "Trusted! The price is appropriate for " + city.capitalize()
            else:
                desk['trust_status_price'] = "Untrusted! The price is too low for " + city.capitalize()
        else:
            desk['trust_status_price'] = "No price standard for " + city.capitalize()

    return desks