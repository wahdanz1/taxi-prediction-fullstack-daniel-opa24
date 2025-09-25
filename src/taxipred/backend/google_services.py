import requests
import os
from dotenv import load_dotenv

# Load environment variables once at module level
load_dotenv()
GMAPS_API_KEY = os.getenv('GMAPS_API_KEY')

def suggest_address(input_text):
    """Get address suggestions from Google Places API."""
    if not input_text:
        return []

    url = "https://places.googleapis.com/v1/places:autocomplete"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": GMAPS_API_KEY}
    data = {
        "input": input_text,
        "locationBias": {
            "rectangle": {
                "low": {"latitude": 55.0, "longitude": 10.0},  # SW Sweden
                "high": {"latitude": 69.1, "longitude": 24.2}  # NE Sweden
            }
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json().get("suggestions", [])


# Function for calculating distance between location A and B
def get_distance(origin, destination):
    """Calculate road distance using Google Distance Matrix API."""
    # Return None immediately if either address is missing
    if not origin or not destination:
        return None
        
    try:
        # Google Distance Matrix API endpoint
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        
        # Set up API parameters for driving distance in metric units
        params = {
            'origins': origin,
            'destinations': destination,
            'units': 'metric',        # Get distance in kilometers, not miles
            'mode': 'driving',        # Calculate actual road distance, not bird path
            'key': GMAPS_API_KEY
        }
        
        # Make API call
        response = requests.get(url, params=params)
        result = response.json()
        
        # Check if API call was successful and route was found
        if result['rows'][0]['elements'][0]['status'] == 'OK':
            # Extract distance in meters and convert to kilometers
            distance_km = result['rows'][0]['elements'][0]['distance']['value'] / 1000
            return round(distance_km, 2)  # Round to 2 decimal places
        else:
            # API returned an error (e.g., no route found between addresses)
            return None
            
    except Exception as e:
        # Log the error for debugging
        print(f"Distance calculation error: {e}")  # Consider using proper logging framework
        return None
