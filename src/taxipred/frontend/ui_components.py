import streamlit as st
from datetime import datetime
import time

from taxipred.utils.api_helpers import call_address_suggestions_api, call_distance_api, call_prediction_api, handle_api_response, format_trip_data_for_display
from taxipred.frontend.ui_helpers import round_to_quarter, smooth_progress, handle_processing_error


# Form rendering
def render_trip_form():
    """
    Render the trip details input form.
    
    Returns:
        dict: Form data if submitted and valid, None otherwise
    """
    st.subheader("🚕 Trip Details", anchor=False)
    st.text("Fill out the form below to get your estimated price. The app uses a ML model to make predictions based on taxi fare patterns.")
    
    # Address inputs
    col1, col2 = st.columns([1, 1])
    
    with col1:
        pickup_address = address_input_with_suggestions("📍 Pickup Location", "pickup")
    
    with col2:
        destination_address = address_input_with_suggestions("🎯 Destination", "destination")
    
    # Trip details inputs
    col3, col4, col5 = st.columns([1, 1, 1])
    with col3:
        pickup_date = st.date_input("📅 Pickup Date", min_value="today")
    with col4:
        now = datetime.now().time()
        default_time = round_to_quarter(now, up=True)
        pickup_time = st.time_input("🕐 Pickup Time", value=default_time, step=900)
    with col5:
        passenger_count = st.selectbox("🙋 Number of Passengers", options=[1, 2, 3, 4])

    if st.button("Get Price Estimate", type="primary", use_container_width=True):
        if pickup_address and destination_address:
            form_data = {
                'pickup': pickup_address,
                'destination': destination_address,
                'pickup_date': pickup_date,
                'pickup_time': pickup_time,
                'passenger_count': passenger_count
            }
            st.session_state.form_data = form_data
            return form_data
        else:
            st.error("Please enter both pickup and destination addresses")
    
    return None


# Processing workflow
def render_prediction_workflow(form_data: dict):
    """
    Handle the prediction workflow with animated progress tracking.
    
    Args:
        form_data: User input data from the form
    """
    st.subheader("Processing Your Request")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Calculate distance
    smooth_progress(progress_bar, status_text, 0, 25, "Calculating distance...", 0.8)
    distance = get_distance_via_api(form_data['pickup'], form_data['destination'])
    
    if not distance:
        handle_processing_error(progress_bar, status_text, 
                                "Could not calculate distance between the provided addresses")
        return
    
    # Step 2: Get ML prediction
    smooth_progress(progress_bar, status_text, 25, 50, "Making ML prediction...", 1.0)
    response = call_prediction_api(distance, form_data['passenger_count'], 
                                   form_data['pickup_date'], form_data['pickup_time'])
    
    # Step 3: Process response
    smooth_progress(progress_bar, status_text, 50, 75, "Processing results...", 0.6)
    processed_data = handle_api_response(response)
    
    if not processed_data:
        handle_processing_error(progress_bar, status_text, 
                                "Failed to process prediction. Please try again.")
        return
    
    # Step 4: Format and complete
    formatted_data = format_trip_data_for_display(
        processed_data, form_data['pickup'], form_data['destination'], 
        distance, form_data['passenger_count']
    )
    
    smooth_progress(progress_bar, status_text, 75, 100, "Finalizing...", 0.8)
    status_text.text("Complete!")
    time.sleep(0.5)
    
    # Transition to results
    st.session_state.trip_data = formatted_data
    st.session_state.prediction_complete = True
    st.session_state.processing = False
    
    progress_bar.empty()
    status_text.empty()
    st.rerun()


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


# Results display
def render_trip_summary(trip_data: dict):
    """
    Display trip results and price estimate.
    
    Args:
        trip_data: Formatted trip and prediction data
    """
    st.success("Price Estimate Complete!")
    st.subheader("Trip Summary")

    col1, col2 = st.columns([2, 1])
    
    with col1:        
        st.markdown(f"""
        📍 **Pickup Address:** {trip_data['pickup']}
        
        🎯 **Destination Address:** {trip_data['destination']}
        
        **Distance:** {trip_data['distance']} km
        
        **Pickup Time:** {trip_data['pickup_time']}
        
        **Passengers:** {trip_data['passenger_count']}
        """)
    
    with col2:
        estimated_price = trip_data['estimated_price']
        
        st.metric(
            label="Estimated Price", 
            value=f"${estimated_price:.2f}",
            help="ML prediction based on multiple factors"
        )
        
        st.markdown("**Factors Considered:**")
        st.markdown(f"""
        - Distance: {trip_data['distance']} km
        - Passengers: {trip_data['passenger_count']}
        - Pickup time: {trip_data['pickup_time']}
        - Weather conditions
        - Traffic patterns
        - Time of day factors
        """)