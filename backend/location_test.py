import requests

def find_nearby_therapists_by_location(location: str) -> str:
    # Your API Key from config
    api_key = "339d0e9e69454311bb8d1be8fb7aef1e"
    
    # ---------------------------------------------------------
    # STEP 1: Geocoding API - Convert "Lucknow" to Coordinates
    # ---------------------------------------------------------
    print(f"--- STEP 1: Finding coordinates for '{location}' ---")
    geocode_url = f"https://api.geoapify.com/v1/geocode/search?text={location}&apiKey={api_key}"
    
    geocode_response = requests.get(geocode_url)
    
    if geocode_response.status_code != 200:
        return f"Error: Geocoding failed (Status {geocode_response.status_code})"
        
    geocode_data = geocode_response.json()
   
    if not geocode_data.get("features"):
        return f"Error: Could not resolve location '{location}'"
        
    # Geoapify returns coordinates in [Longitude, Latitude] format
    coords = geocode_data["features"][0]["geometry"]["coordinates"]
    
    lon, lat = coords[0], coords[1]
    
    print(f"Success! Extracted Coordinates -> Latitude: {lat}, Longitude: {lon}\n")
    
    # ---------------------------------------------------------
    # STEP 2: Places API - Find Therapists near Coordinates
    # ---------------------------------------------------------
    print(f"--- STEP 2: Searching Places API for therapists nearby ---")
    
    # We use 'healthcare' category and a 5000m (5km) circle filter
    # Format: filter=circle:longitude,latitude,radius_in_meters
    places_url = f"https://api.geoapify.com/v2/places?categories=healthcare.hospital&filter=circle:{lon},{lat},5000&bias=proximity:{lon},{lat}&limit=5&apiKey={api_key}"
    
    places_response = requests.get(places_url)
    
    if places_response.status_code != 200:
        return f"Error: Places search failed (Status {places_response.status_code})"
        
    places_data = places_response.json()
    
    # ---------------------------------------------------------
    # STEP 3: Format the Output for testing
    # ---------------------------------------------------------
    result_text = f"\n=== Healthcare/Therapists found near {location} ===\n"
    
    places = places_data.get("features", [])
    if not places:
        return result_text + "No facilities found within the radius."
        
    for feature in places:
        props = feature.get("properties", {})
        name = props.get("name", "Unnamed Facility")
        address = props.get("address_line2", "No detailed address")
        distance = props.get("distance", "Unknown")
        
        result_text += f"- {name} ({distance} meters away)\n  Address: {address}\n"
        
    return result_text

# Run the test
if __name__ == "__main__":
    # Test with Lucknow as requested
    output = find_nearby_therapists_by_location("Dalibagh, Lucknow")
    print(output)