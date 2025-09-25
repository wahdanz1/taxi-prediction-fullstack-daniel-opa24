import streamlit as st
import time
from datetime import datetime

from taxipred.frontend.ui_helpers import load_css, round_to_quarter, smooth_progress
from taxipred.utils.api_helpers import call_prediction_api, handle_api_response, format_trip_data_for_display
from taxipred.frontend.ui_components import address_input_with_suggestions, get_distance_via_api

# Load CSS
load_css()

def main():
    st.set_page_config(page_title="TaxiPred 1.0", layout="wide")
    st.title("Taxi Price Prediction", anchor=False)

    # Initialize session state
    if "prediction_complete" not in st.session_state:
        st.session_state.prediction_complete = False
    if "trip_data" not in st.session_state:
        st.session_state.trip_data = None
    if "processing" not in st.session_state:
        st.session_state.processing = False

    # State 1: Show form (initial state or after user clicks "New Trip Prediction"-button in State 3)
    if not st.session_state.processing and not st.session_state.prediction_complete:
        form_submitted = price_prediction_form()
        
        if form_submitted:
            st.session_state.processing = True
            st.rerun()
    
    # State 2: Show progress bar (processing)
    elif st.session_state.processing:
        handle_prediction_process(st.session_state.get('form_data'))
    
    # State 3: Show results (completed)
    elif st.session_state.prediction_complete:
        display_trip_result(st.session_state.trip_data)
        
        # Reset button
        if st.button("New Trip Prediction", type="primary", use_container_width=True):
            st.session_state.prediction_complete = False
            st.session_state.processing = False
            st.session_state.trip_data = None
            if 'form_data' in st.session_state:
                del st.session_state.form_data
            st.rerun()


def price_prediction_form():
    """Handle UI elements and user input collection only."""
    st.subheader("🚕 Trip Details", anchor=False)
    st.text("Fill out the form below to get your estimated price. The app uses a ML-model to make a prediction based on taxi fare price-patterns.")
    
    # Address inputs
    col1, col2 = st.columns([1, 1])
    
    with col1:
        pickup_address = address_input_with_suggestions(
            "📍 Pickup Location", 
            "pickup"
        )
    
    with col2:
        destination_address = address_input_with_suggestions(
            "🎯 Destination", 
            "destination"
        )
    
    # Pickup date, time and passengers
    col3, col4, col5 = st.columns([1, 1, 1])
    with col3:
        pickup_date = st.date_input("📅 Pickup Date", min_value="today")
    with col4:
        now = datetime.now().time()
        default_time = round_to_quarter(now, up=True)
        pickup_time = st.time_input("🕐 Pickup Time", value=default_time, step=900)
    with col5:
        passenger_count = st.selectbox(
            "🙋 Number of Passengers",
            options=[1, 2, 3, 4]
        )

    if st.button("Get Price Estimate", type="primary", use_container_width=True):
        if pickup_address and destination_address:
            form_data = {
                'pickup': pickup_address,
                'destination': destination_address,
                'pickup_date': pickup_date,
                'pickup_time': pickup_time,
                'passenger_count': passenger_count
            }
            # Store form data in session state for processing
            st.session_state.form_data = form_data
            return form_data
        else:
            st.error("Please enter both pickup and destination addresses")
    return None


def handle_prediction_process(form_data):
    """Handle the prediction process with progress bar."""
    st.subheader("Processing Your Request")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Distance calculation
    smooth_progress(progress_bar, status_text, 0, 25, "Calculating distance...", 0.8)
    
    distance = get_distance_via_api(form_data['pickup'], form_data['destination'])
    
    if distance:
        # Step 2: API prediction
        smooth_progress(progress_bar, status_text, 25, 50, "Making ML prediction...", 1.0)
        
        response = call_prediction_api(distance, form_data['passenger_count'], 
                                        form_data['pickup_date'], form_data['pickup_time'])
        
        # Step 3: Processing results
        smooth_progress(progress_bar, status_text, 50, 75, "Processing results...", 0.6)
        
        processed_data = handle_api_response(response)
        
        if processed_data:
            # Step 4: Formatting data
            formatted_data = format_trip_data_for_display(processed_data, form_data['pickup'], 
                                                        form_data['destination'], distance, form_data['passenger_count'])
            
            # Complete progress
            smooth_progress(progress_bar, status_text, 75, 100, "Finalizing...", 0.8)
            
            status_text.text("✅ Complete!")
            time.sleep(0.5)
            
            # Store results and transition to results state
            st.session_state.trip_data = formatted_data
            st.session_state.prediction_complete = True
            st.session_state.processing = False
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.rerun()
        else:
            # Handle processing error
            progress_bar.progress(100)
            status_text.text("Processing failed")
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            st.error("Failed to process prediction. Please try again.")
            
            # Reset to form state
            st.session_state.processing = False
            time.sleep(2)
            st.rerun()
    else:
        # Handle distance calculation failure
        progress_bar.progress(100)
        status_text.text("Could not calculate distance")
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        st.error("Could not calculate distance between the provided addresses")
        
        # Reset to form state
        st.session_state.processing = False
        time.sleep(2)
        st.rerun()


def display_trip_result(trip_data):
    """Display trip results and price estimate."""
    st.success("Price Estimate Complete!")
    
    # Trip summary
    st.subheader("📋 Trip Summary")

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
        
        # Factors considered
        st.markdown("**Factors Considered:**")
        st.markdown(f"""
        - Distance: {trip_data['distance']} km
        - Passengers: {trip_data['passenger_count']}
        - Pickup time: {trip_data['pickup_time']}
        - Weather conditions
        - Traffic patterns
        - Time of day factors
        """)


if __name__ == "__main__":
    main()