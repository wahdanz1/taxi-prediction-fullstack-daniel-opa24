import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()
GMAPS_API_KEY = os.getenv('GMAPS_API_KEY')

# Set up logger
logger = logging.getLogger("uvicorn.error")


def suggest_address(input_text: str) -> list:
    """
    Get address suggestions from Google Places API (New).
    
    Searches for addresses within Sweden using Google Places autocomplete
    with location bias to improve relevance of results.
    
    Args:
        input_text: Address search query
        
    Returns:
        List of address suggestions from Google Places API (New)
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


def get_distance_and_traffic(origin: str, destination: str, pickup_datetime) -> dict | None:
    """
    Calculate driving distance and traffic conditions using Google Routes API.
    
    Returns both distance and estimated traffic level based on predicted conditions
    at the specified departure time versus free-flow traffic.
    
    Args:
        origin: Starting address
        destination: Destination address
        pickup_datetime: Scheduled departure time for traffic prediction
        
    Returns:
        Dict with distance_km and traffic_conditions, or None if calculation fails
    """

    if not origin or not destination:
        return None
        
    try:
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GMAPS_API_KEY,
            "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.staticDuration"
        }
        
        data = {
            "origin": {"address": origin},
            "destination": {"address": destination},
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_AWARE",
            "departureTime": pickup_datetime.isoformat() + "Z",
            "computeAlternativeRoutes": False
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            return None
            
        result = response.json()
        
        if not result.get('routes'):
            return None
        
        route = result['routes'][0]
        
        # Extract distance
        distance_meters = route.get('distanceMeters', 0)
        distance_km = round(distance_meters / 1000, 2)
        
        # Calculate traffic conditions
        duration_str = route.get('duration', '0s')
        static_duration_str = route.get('staticDuration', '0s')
        
        # Parse duration strings (format: "123s")
        duration_seconds = int(duration_str.rstrip('s'))
        static_duration_seconds = int(static_duration_str.rstrip('s'))
        
        # Calculate traffic impact ratio
        if static_duration_seconds > 0:
            traffic_ratio = duration_seconds / static_duration_seconds
            
            # Check if pickup time is during rush hour
            hour = pickup_datetime.hour
            weekday = pickup_datetime.weekday()
            is_rush_hour = (6 <= hour <= 9 or 16 <= hour <= 19) and weekday < 5
            
            # Categorize with adjusted thresholds
            if traffic_ratio < 1.05:
                traffic_conditions = "Low"
            elif traffic_ratio < 1.15:
                traffic_conditions = "Medium"
            else:
                traffic_conditions = "High"
            
            # Override if API suggests low traffic during known rush hours
            if is_rush_hour and traffic_conditions == "Low":
                traffic_conditions = "Medium"
            
        else:
            traffic_conditions = "Medium"
        
        return {
            "distance_km": distance_km,
            "traffic_conditions": traffic_conditions
        }
            
    except Exception as e:
        print(f"Routes API error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def get_weather(latitude: float, longitude: float) -> str:
    """
    Get current weather conditions from Google Weather API.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        
    Returns:
        Weather condition string ("Clear", "Rain", "Snow")
    """
    try:
        url = "https://weather.googleapis.com/v1/currentConditions:lookup"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GMAPS_API_KEY
        }

        # Request body format from API docs
        data = {
            "location": {
                "latitude": latitude,
                "longitude": longitude
            }
        }

        response = requests.post(url, json=data, headers=headers)
        result = response.json()

        weather_code = result.get('currentConditions', {}).get('weatherCode', 0)

        # Map weather codes to your model's categories
        # Some codes might be wrong - update if needed
        if weather_code in [0, 1, 2]:  # Clear/Sunny
            return "Clear"
        elif weather_code in [45, 48, 51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]:  # Rain variants
            return "Rain"
        elif weather_code in [71, 73, 75, 77, 85, 86]:  # Snow variants
            return "Snow"
        else:
            return "Clear"  # Default fallback

    except Exception as e:
        print(f"Weather API error: {e}")
        return "Clear" # Fallback to default value
