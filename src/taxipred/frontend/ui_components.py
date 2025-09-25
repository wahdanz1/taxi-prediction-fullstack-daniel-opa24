import streamlit as st
from taxipred.utils.helpers import call_address_suggestions_api, call_distance_api

def address_input_with_suggestions(label, key):
    """Create address input with autocomplete suggestions."""
    # Create text input field for user to type address
    user_input = st.text_input(label, key=f"{key}_search", help="Enter an address and press enter to get suggestions.", placeholder="Enter an address...")
    
    # Only show suggestions if user has entered something
    if user_input:
        # Get address suggestions from Google Places API
        suggestions = call_address_suggestions_api(user_input)
        
        if suggestions:
            # Extract readable address text from API response, limit to 5 suggestions
            suggestion_texts = ["Select an address..."] + [
                s['placePrediction']['text']['text'] for s in suggestions[:5]
            ]
            
            # Dropdown with suggestions
            selected = st.selectbox(
                "Choose from suggestions:", 
                suggestion_texts,
                key=f"{key}_select"
            )
            
            # If user selected a real address (not the placeholder), return it
            if selected != "Select an address...":
                return selected
    
    # Return whatever user typed manually (or empty string if nothing)
    return user_input

def get_distance_via_api(origin, destination):
    """Get distance via backend API instead of direct call."""
    return call_distance_api(origin, destination)