import requests
import os
from dotenv import load_dotenv

load_dotenv()
GMAPS_API_KEY = os.getenv('GMAPS_API_KEY')


def suggest_address(input_text: str) -> list:
    """
    Get address suggestions from Google Places API.
    
    Searches for addresses within Sweden using Google Places autocomplete
    with location bias to improve relevance of results.
    
    Args:
        input_text: Address search query
        
    Returns:
        List of address suggestions from Google Places API
    """
    if not input_text:
        return []

    url = "https://places.googleapis.com/v1/places:autocomplete"
    headers = {
        "Content-Type": "application/json", 
        "X-Goog-Api-Key": GMAPS_API_KEY
    }
    data = {
        "input": input_text,
        "locationBias": {
            "rectangle": {
                "low": {"latitude": 55.0, "longitude": 10.0},   # Southwest Sweden
                "high": {"latitude": 69.1, "longitude": 24.2}   # Northeast Sweden
            }
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json().get("suggestions", [])


def get_distance(origin: str, destination: str) -> float | None:
    """
    Calculate driving distance between two addresses using Google Distance Matrix API.
    
    Returns the actual road distance in kilometers, not straight-line distance.
    Handles API errors gracefully by returning None.
    
    Args:
        origin: Starting address
        destination: Destination address
        
    Returns:
        Distance in kilometers rounded to 2 decimal places, or None if calculation fails
    """
    if not origin or not destination:
        return None
        
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            'origins': origin,
            'destinations': destination,
            'units': 'metric',
            'mode': 'driving',
            'key': GMAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        result = response.json()
        
        # Check if route calculation was successful
        if result['rows'][0]['elements'][0]['status'] == 'OK':
            distance_meters = result['rows'][0]['elements'][0]['distance']['value']
            distance_km = distance_meters / 1000
            return round(distance_km, 2)
        else:
            return None
            
    except Exception as e:
        print(f"Distance calculation error: {e}")
        return None
