import streamlit as st
from taxipred.utils.api_helpers import call_address_suggestions_api, call_distance_api


# Address input components
def address_input_with_suggestions(label: str, key: str) -> str:
    """
    Create address input field with Google Places autocomplete suggestions.
    
    Provides a text input followed by a dropdown of address suggestions
    from Google Places API to improve user experience and accuracy.
    
    Args:
        label: Display label for the input field
        key: Unique key for Streamlit state management
        
    Returns:
        Selected or manually entered address string
    """
    user_input = st.text_input(
        label, 
        key=f"{key}_search", 
        help="Enter an address and press enter to get suggestions.", 
        placeholder="Enter an address..."
    )
    
    if user_input:
        suggestions = call_address_suggestions_api(user_input)
        
        if suggestions:
            # Create dropdown with suggestions, limit to 5 for usability
            suggestion_texts = ["Select an address..."] + [
                s['placePrediction']['text']['text'] for s in suggestions[:5]
            ]
            
            selected = st.selectbox(
                "Choose from suggestions:", 
                suggestion_texts,
                key=f"{key}_select"
            )
            
            # Return selected address if user chose one
            if selected != "Select an address...":
                return selected
    
    # Return manual input if no suggestion selected
    return user_input


# Distance calculation components  
def get_distance_via_api(origin: str, destination: str) -> float | None:
    """
    Calculate distance between two addresses using backend API.
    
    Wrapper function for consistent distance calculation throughout the app.
    
    Args:
        origin: Starting address
        destination: Destination address
        
    Returns:
        Distance in kilometers, None if calculation fails
    """
    return call_distance_api(origin, destination)