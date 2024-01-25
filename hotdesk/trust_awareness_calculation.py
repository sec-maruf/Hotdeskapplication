def calculate_trust_score_and_sort(desks, trust_factors):
    trust_threshold =3.5 
    for desk in desks:
        trust_score = 0
        trust_score += float(desk['user_ratings']) * trust_factors['user_ratings']
        trust_score += float(desk['frequency_of_bookings']) * trust_factors['frequency_of_bookings']
        trust_score += float(desk['feedback']) * trust_factors['feedback']
        trust_score += float(desk['accuracy_of_description']) * trust_factors['accuracy_of_description']
        
        desk['trust_score'] = round(trust_score, 3)
        desk['recommendation'] = "Recommended" if desk['trust_score'] >= trust_threshold else "Not Recommended"
    return sorted(desks, key=lambda d: d['trust_score'], reverse=True)