import requests 
import streamlit as st
from datetime import datetime

from taxipred.utils.constants import API_BASE_URL


def get_api_data(endpoint):
    """Simple GET request to API endpoint."""
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    response = requests.get(url)
    return response


def post_api_data(endpoint, data):
    """Simple POST request to API endpoint with JSON data."""
    url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
    response = requests.post(url, json=data)
    return response

# Build dict and make API request --------------------
def call_prediction_api(distance, passenger_count, pickup_date, pickup_time):
    """Build request data and call the API."""

    pickup_datetime = datetime.combine(pickup_date, pickup_time)
    user_input_dict = {
        'trip_distance_km': distance,
        'passenger_count': passenger_count,
        'pickup_datetime': pickup_datetime.strftime("%Y-%m-%dT%H:%M"),
    }

    # Make the API call and return response
    response = post_api_data("predict", user_input_dict)
    return response


# Call endpoint for Google Places API --------------------
def call_address_suggestions_api(query):
    """Get address suggestions via backend API."""
    response = post_api_data("suggestion", {"query": query})
    processed_data = handle_api_response(response)
    if processed_data:
        return processed_data.get("suggestions", [])
    return []


# Call endpoint for Google Distance Matrix API --------------------
def call_distance_api(origin, destination):
    """Calculate distance via backend API."""
    response = post_api_data("distance", {"origin": origin, "destination": destination})
    processed_data = handle_api_response(response)
    if processed_data:
        return processed_data.get("distance_km")
    return None


# Handle API response and extract JSON --------------------
def handle_api_response(response):
    """Process API response and handle errors."""
    # Check response status
    if response.status_code != 200:
        st.error(f"API Error: {response.status_code}")
        return None
    
    # Extract JSON data and return it
    try:
        api_data = response.json()
        return api_data
    except Exception as e:
        st.error(f"Failed to parse response: {e}")
        return None


# Format data and prepare for display --------------------
def format_trip_data_for_display(api_response, pickup_address, destination_address, distance, passenger_count):
    """Transform API response + user inputs into display format."""
    return {
        'pickup': pickup_address,
        'destination': destination_address,
        'distance': distance,
        'pickup_time': api_response['trip_details']['pickup_time'],
        'passenger_count': passenger_count,
        'estimated_price': api_response['estimated_price']
    }