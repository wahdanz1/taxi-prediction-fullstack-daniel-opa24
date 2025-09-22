import streamlit as st
import requests
import os

def autocomplete_address(input_text, api_key):
    """Get address suggestions from Google Places API."""
    if not input_text:
        return []

    url = "https://places.googleapis.com/v1/places:autocomplete"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key}
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


def address_input_with_suggestions(label, key, api_key):
    """Create address input with autocomplete suggestions."""
    user_input = st.text_input(label, key=f"{key}_search", help="Enter an address and press enter to get suggestions.")
    
    if user_input:
        suggestions = autocomplete_address(user_input, api_key)
        
        if suggestions:
            suggestion_texts = ["Select an address..."] + [
                s['placePrediction']['text']['text'] for s in suggestions[:5]
            ]
            
            selected = st.selectbox(
                "Choose from suggestions:", 
                suggestion_texts,
                key=f"{key}_select"
            )
            
            if selected != "Select an address...":
                return selected, None
    
    return user_input, None


def get_place_details(place_id, api_key):
    """Get detailed place information from place ID."""
    url = f"https://places.googleapis.com/v1/places/{place_id}"
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": api_key}
    params = {"fields": "location,displayName"}
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()


def get_distance(origin, destination, api_key):
    """Calculate road distance using Google Distance Matrix API."""
    if not origin or not destination:
        return None
        
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            'origins': origin,
            'destinations': destination,
            'units': 'metric',
            'mode': 'driving',
            'key': api_key
        }
        
        response = requests.get(url, params=params)
        result = response.json()
        
        if result['rows'][0]['elements'][0]['status'] == 'OK':
            distance_km = result['rows'][0]['elements'][0]['distance']['value'] / 1000
            return round(distance_km, 2)
        else:
            return None
            
    except Exception as e:
        st.error(f"Error calculating distance: {e}")
        return None