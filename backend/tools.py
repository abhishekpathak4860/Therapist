import httpx
from twilio.rest import Client
from langchain_groq import ChatGroq
from backend.config import (
    GROQ_API_KEY, 
    TWILIO_ACCOUNT_SID, 
    TWILIO_AUTH_TOKEN, 
    TWILIO_FROM_NUMBER, 
    EMERGENCY_CONTACT,
    GEOAPIFY_API_KEY
)

# Initialize Groq LLM once
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.7,
    api_key=GROQ_API_KEY
)

# ---------------------------------------------------------
# Step 1: Asynchronous Medgemma / Chat Model Tool
# ---------------------------------------------------------
async def query_medgemma(prompt: str) -> str:
    """
    Calls MedGemma model asynchronously with a therapist personality profile.
    """
    system_prompt = """You are Dr. Emily Hartman, a warm and experienced clinical psychologist. 
    Respond to patients with:

    1. Emotional attunement ("I can sense how difficult this must be...")
    2. Gentle normalization ("Many people feel this way when...")
    3. Practical guidance ("What sometimes helps is...")
    4. Strengths-focused support ("I notice how you're...")

    Key principles:
    - Never use brackets or labels
    - Blend elements seamlessly
    - Vary sentence structure
    - Use natural transitions
    - Mirror the user's language level
    - Always keep the conversation going by asking open ended questions to dive into the root cause of patients problem
    """
    
    try:
        # Use .ainvoke() instead of .invoke() for async execution
        response = await llm.ainvoke(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.content.strip()
    except Exception as e:
        return "I'm having technical difficulties, but I want you to know your feelings matter. Please try again shortly."


# ---------------------------------------------------------
# Step 2: Asynchronous Twilio Emergency Call Tool
# ---------------------------------------------------------
def call_emergency() -> None:
    """
    Triggers an automated emergency call via Twilio client.
    """
    # Note: Twilio's client handles REST internally. Marking it async allows 
    # it to fit perfectly into your agent's asynchronous execution loop.
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.calls.create(
        to=EMERGENCY_CONTACT,
        from_=TWILIO_FROM_NUMBER,
        url="http://demo.twilio.com/docs/voice.xml"
    )


# ---------------------------------------------------------
# Step 3: Asynchronous Geoapify Location API Tool
# ---------------------------------------------------------

   # ---------------------------------------------------------
# Step 3: Asynchronous Geoapify Location API Tool
# ---------------------------------------------------------
async def fetch_nearby_therapists(location_name: str) -> str:
    """
    Hits Geoapify Geocoding and Places API asynchronously using httpx
    to retrieve nearby healthcare facilities without blocking the event loop.
    """
    # 🚨 DEBUG PRINT 1: See exactly what the AI typed!
    print(f"\n🚀 --- TOOL TRIGGERED ---")
    print(f"🤖 AI is searching for: '{location_name}'")
    
    async with httpx.AsyncClient() as client:
        geocode_url = "https://api.geoapify.com/v1/geocode/search"
        geocode_params = {
            "text": location_name,
            "apiKey": GEOAPIFY_API_KEY,
            "limit": 1
        }
        
        try:
            geocode_response = await client.get(geocode_url, params=geocode_params, timeout=10.0)
            
            #  DEBUG PRINT 2: Check Geocoding status
            print(f" Geocode API Status Code: {geocode_response.status_code}")
            
            if geocode_response.status_code != 200:
                print(" FAILED AT GEOCODING API")
                return "Unable to resolve the location coordinates at the moment."
            
            geocode_data = geocode_response.json()
            if not geocode_data.get("features"):
                print("GEOCODING RETURNED 0 RESULTS")
                return f"Could not find any location coordinates corresponding to '{location_name}'."
                
            coords = geocode_data["features"][0]["geometry"]["coordinates"]
            lon, lat = coords[0], coords[1]
            print(f" Coordinates found: Lon={lon}, Lat={lat}")
            
            # 2. Places Discovery Phase
            places_url = "https://api.geoapify.com/v2/places"
            
            # Format coordinates to exactly 6 decimal places to prevent float errors
            safe_lon = f"{lon:.6f}"
            safe_lat = f"{lat:.6f}"
            places_params = {
                # FIX: Removed the unsupported 'psychotherapy' category
                "categories": "healthcare.clinic_or_praxis.psychiatry,healthcare.hospital",
                "filter": f"circle:{safe_lon},{safe_lat},5000",
                "bias": f"proximity:{safe_lon},{safe_lat}",
                "limit": 5,
                "apiKey": GEOAPIFY_API_KEY
            }
            
            # We must use httpx's internal URL encoding, but tell it not to mess with commas
            places_response = await client.get(places_url, params=places_params, timeout=10.0)
            
            #  DEBUG PRINT 3: Check Places status
            print(f" Places API Status Code: {places_response.status_code}")
            
            # Print the actual URL httpx generated so we can see if it mangled it
            print(f" Requested URL: {places_response.request.url}")
            
            if places_response.status_code != 200:
                print("FAILED AT PLACES API")
                # Print the exact error message Geoapify sent back!
                print(f" Geoapify Error: {places_response.text}")
                return "Successfully located coordinates, but failed to fetch nearby medical centers."
                
            places_data = places_response.json()
            places = places_data.get("features", [])
            
            if not places:
                print(" PLACES API RETURNED 0 HOSPITALS/CLINICS")
                return f"Coordinates located for {location_name}, but no healthcare centers were found within a 5km radius."
                
            # 3. Compile clean plaintext report
            result_lines = [f"Healthcare options located near {location_name}:"]
            for feature in places:
                props = feature.get("properties", {})
                name = props.get("name", "Unnamed Facility")
                address = props.get("address_line2", "Address details unavailable")
                distance = props.get("distance", "Unknown")
                result_lines.append(f"- Name: {name}, Distance: {distance} meters away, Address: {address}")
                
            #  DEBUG PRINT 4: Total Success!
            print("SUCCESS! Data found:")
            print("\n".join(result_lines))
            print("--------------------------\n")
            
            return "\n".join(result_lines)

        except Exception as e:
            # DEBUG PRINT 5: Code crashed!
            print(f" CRASH EXCEPTION: {str(e)}")
            return f"An unexpected network or extraction error occurred while searching: {str(e)}"