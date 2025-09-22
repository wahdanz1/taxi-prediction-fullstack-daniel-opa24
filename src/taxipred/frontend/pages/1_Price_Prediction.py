import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from taxipred.utils.helpers import read_api_endpoint
from taxipred.frontend.helpers import load_css
from taxipred.frontend.components import (
    address_input_with_suggestions, 
    get_distance
)

# Load CSS and environment
load_css()
load_dotenv()

# Page config
st.set_page_config(page_title="TaxiPred 1.0", layout="wide")

GMAPS_API_KEY = os.getenv('GMAPS_API_KEY')

def main():
    st.title("Taxi Price Prediction")
    
    # Main prediction interface
    trip_result = price_prediction_form()
    
    # Results section
    if trip_result:
        display_trip_result(trip_result)
    else:
        st.info("Enter your trip details above to get a price estimate")
    
    # Dev section (optional)
    with st.expander("Developer Info", expanded=False):
        try:
            data = read_api_endpoint("taxi")
            df = pd.DataFrame(data.json())
            st.subheader("Clean Dataset Preview")
            st.dataframe(df.head(10))
            st.write(f"Total records: {len(df)}")
        except Exception as e:
            st.error(f"Could not load dataset: {e}")


def price_prediction_form():
    """Main price prediction form."""
    with st.container():
        st.subheader("🚕 Trip Details")
        
        # Address inputs
        col1, col2 = st.columns([1, 1])
        
        with col1:
            pickup_address, pickup_place_id = address_input_with_suggestions(
                "📍 Pickup Location", 
                "pickup", 
                GMAPS_API_KEY
            )
        
        with col2:
            destination_address, destination_place_id = address_input_with_suggestions(
                "🎯 Destination", 
                "destination", 
                GMAPS_API_KEY
            )
        
        # Additional options
        col3, col4 = st.columns([1, 1])
        with col3:
            pickup_time = st.time_input("🕐 Pickup Time")
        with col4:
            st.write("")  # Spacing
        
        # Calculate button
        if st.button("Get Price Estimate", type="primary", use_container_width=True):
            if pickup_address and destination_address:
                with st.spinner("Calculating distance and price..."):
                    distance = get_distance(pickup_address, destination_address, GMAPS_API_KEY)
                    
                    if distance:
                        return {
                            'pickup': pickup_address,
                            'destination': destination_address,
                            'distance': distance,
                            'pickup_time': pickup_time
                        }
                    else:
                        st.error("Could not calculate distance between addresses. Please check your locations.")
            else:
                st.error("Please enter both pickup and destination addresses")
    
    return None


def display_trip_result(trip_data):
    """Display trip results and price estimate."""
    st.success("Trip Details Calculated!")
    
    # Trip summary
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Trip Summary")
        
        # Trip details in a nice format
        st.markdown(f"""
        📍 **Pickup Address:** {trip_data['pickup']}
        🎯 **Destination Address:** {trip_data['destination']}
        
        **Distance:** {trip_data['distance']} km
        
        **Pickup Time:** {trip_data['pickup_time']}
        """)
    
    with col2:
        # Price estimate (placeholder calculation)
        estimated_price = trip_data['distance'] * 2.5 + 10
        
        st.metric(
            label="Estimated Price", 
            value=f"${estimated_price:.2f}",
            help="Price based on distance and base fare"
        )
        
        # Price breakdown
        st.markdown(f"""
        **Price Breakdown:**
        - Base fare: $10.00
        - Distance ({trip_data['distance']} km): ${trip_data['distance'] * 2.5:.2f}
        """)
    
    # Additional info
    st.info("""
    **Note:** This is a simplified price calculation/placeholder. 
    The actual ML model will consider time of day, traffic conditions, weather, and other factors for more accurate predictions.
    """)


if __name__ == "__main__":
    main()