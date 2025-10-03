import requests 
import streamlit as st
from datetime import datetime
from taxipred.utils.constants import API_BASE_URL


def get_api_data(endpoint: str):
    """Make GET request to API endpoint."""
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    response = requests.get(url)
    return response


def post_api_data(endpoint: str, data: dict):
    """Make POST request to API endpoint with JSON data."""
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    response = requests.post(url, json=data)
    return response


# Cleaned dataset call
def get_dataset():
    response = get_api_data("taxi")
    processed_data = handle_api_response(response)
    if processed_data:
        return processed_data
    return []


# Dataset statistics call
def get_stats():
    response = get_api_data("taxi/stats")
    processed_data = handle_api_response(response)
    if processed_data:
        return processed_data
    return []


# Prediction API calls
def call_prediction_api(distance: float, passenger_count: int, pickup_date, pickup_time, 
                        weather: str, traffic_conditions: str):
    """
    Build prediction request and call ML prediction API.
    
    Args:
        distance: Trip distance in kilometers
        passenger_count: Number of passengers
        pickup_date: Date object for pickup
        pickup_time: Time object for pickup
        weather: Weather condition ("Clear", "Rain", "Snow")
        traffic_conditions: Traffic level ("Low", "Medium", "High")
        
    Returns:
        Response object from prediction API
    """
    pickup_datetime = datetime.combine(pickup_date, pickup_time)
    user_input_dict = {
        'trip_distance_km': distance,
        'passenger_count': passenger_count,
        'pickup_datetime': pickup_datetime.strftime("%Y-%m-%dT%H:%M"),
        'weather': weather,
        'traffic_conditions': traffic_conditions
    }

    return post_api_data("predict", user_input_dict)


# Google Services API calls
def call_address_suggestions_api(query: str) -> list:
    """
    Get address suggestions via backend Google Places API.
    
    Args:
        query: Address search string
        
    Returns:
        List of address suggestions, empty list if error
    """
    response = post_api_data("suggestion", {"query": query})
    processed_data = handle_api_response(response)
    if processed_data:
        return processed_data.get("suggestions", [])
    return []


def call_distance_api(origin: str, destination: str, pickup_datetime: datetime) -> dict | None:
    """
    Calculate distance and traffic conditions via backend API.
    
    Args:
        origin: Starting address
        destination: Destination address
        pickup_datetime: Pickup date and time for traffic prediction
        
    Returns:
        Dict with distance_km and traffic_conditions, None if fails
    """
    response = post_api_data("distance", {
        "origin": origin,
        "destination": destination,
        "pickup_datetime": pickup_datetime.strftime("%Y-%m-%dT%H:%M")
        }
    )
    processed_data = handle_api_response(response)
    if processed_data:
        return processed_data
    return None


# Response handling
def handle_api_response(response):
    """
    Process API response and handle errors with Streamlit feedback.
    
    Args:
        response: Response object from API call
        
    Returns:
        Parsed JSON data or None if error
    """
    if response.status_code != 200:
        st.error(f"API Error: {response.status_code}")
        return None
    
    try:
        return response.json()
    except Exception as e:
        st.error(f"Failed to parse response: {e}")
        return None


# Data formatting
def format_trip_data_for_display(api_response: dict, pickup_address: str, 
                                destination_address: str, distance: float, 
                                passenger_count: int, weather: str,
                                traffic_conditions: str) -> dict:
    """
    Transform API response and user inputs into display-ready format.
    
    Args:
        api_response: Response from prediction API
        pickup_address: User-entered pickup address
        destination_address: User-entered destination address  
        distance: Calculated trip distance
        passenger_count: Number of passengers
        weather: Weather condition used for prediction
        traffic_conditions: Traffic condition used for prediction
        
    Returns:
        Dictionary formatted for UI display
    """
    return {
        'pickup': pickup_address,
        'destination': destination_address,
        'distance': distance,
        'pickup_time': api_response['trip_details']['pickup_time'],
        'passenger_count': passenger_count,
        'estimated_price': api_response['estimated_price'],
        'weather': weather,
        'traffic_conditions': traffic_conditions
    }
