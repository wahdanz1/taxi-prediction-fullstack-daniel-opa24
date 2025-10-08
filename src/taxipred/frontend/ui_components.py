import streamlit as st
import pandas as pd
from datetime import datetime
import time

from taxipred.utils.api_helpers import call_address_suggestions_api, call_distance_api, call_prediction_api, handle_api_response, format_trip_data_for_display, get_model_metrics, get_feature_importance
from taxipred.frontend.ui_helpers import round_to_quarter, smooth_progress, handle_processing_error
from taxipred.frontend.ml_glossary import MODEL_DESCRIPTIONS, GLOSSARY_TERMS


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
        passenger_count = st.number_input("🙋 Number of Passengers", min_value=1, max_value=4, step=1)

    if st.button("Get Price Estimate", type="primary", width="stretch"):
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
    # Clear lingering elements when button is clicked
    st.empty() 

    st.subheader("Processing Your Request")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Calculate distance
    smooth_progress(progress_bar, status_text, 0, 25, "Calculating distance and traffic...", 0.8)
    
    # Combine pickup date and time
    pickup_datetime = datetime.combine(form_data['pickup_date'], form_data['pickup_time'])
    route_data = call_distance_api(form_data['pickup'], form_data['destination'], pickup_datetime)
    
    if not route_data:
        handle_processing_error(progress_bar, status_text, 
                                "Could not calculate distance between the provided addresses")
        return
    
    distance = route_data['distance_km']
    traffic_conditions = route_data['traffic_conditions']
    
    # Step 2: Get ML prediction
    smooth_progress(progress_bar, status_text, 25, 50, "Making ML prediction...", 1.0)
    response = call_prediction_api(
        distance,
        form_data['passenger_count'], 
        form_data['pickup_date'],
        form_data['pickup_time'],
        weather=form_data.get('weather', 'Clear'),
        traffic_conditions=traffic_conditions
    )
    
    # Step 3: Process response
    smooth_progress(progress_bar, status_text, 50, 75, "Processing results...", 0.6)
    processed_data = handle_api_response(response)
    
    if not processed_data:
        handle_processing_error(progress_bar, status_text, 
                                "Failed to process prediction. Please try again.")
        return
    
    # Step 4: Format and complete
    formatted_data = format_trip_data_for_display(
        processed_data,
        form_data['pickup'],
        form_data['destination'], 
        distance,
        form_data['passenger_count'],
        form_data.get('weather', 'Clear'),
        traffic_conditions
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
        # Cache the suggestions in session state to avoid repeated API calls
        cache_key = f"{key}_suggestions_cache"
        cached_input_key = f"{key}_cached_input"
        
        # Only call API if input has changed
        if (cache_key not in st.session_state or 
            st.session_state.get(cached_input_key) != user_input):
            
            suggestions = call_address_suggestions_api(user_input)
            st.session_state[cache_key] = suggestions
            st.session_state[cached_input_key] = user_input
        else:
            suggestions = st.session_state[cache_key]
        
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
                return selected
    
    return user_input


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
        - Weather: {trip_data.get('weather', 'N/A')}
        - Traffic: {trip_data.get('traffic_conditions', 'N/A')}
        """)


def render_metrics_section():
    """Display model performance metrics."""
    st.subheader("Model Comparison")

    with st.spinner("Loading model metrics..."):
        metrics = get_model_metrics()
    
    if not metrics:
        st.error("Unable to load model metrics")
        return
    
    # Display best model info at the top
    best_model = min(metrics.keys(), key=lambda k: metrics[k]['mae'])
    st.info(f"**Best Performing Model:** {best_model}")
    
    # Create comparison table
    comparison_data = []
    for model_name, scores in metrics.items():
        comparison_data.append({
            "Model": model_name,
            "MAE ($)": f"${scores['mae']:.2f}",
            "RMSE ($)": f"${scores['rmse']:.2f}",
            "R² Score": f"{scores['r2']:.3f}"
        })
    
    st.dataframe(comparison_data, hide_index=True, width="stretch")
    
    # Add metric explanations
    with st.expander("📖 Understanding the Metrics"):
        st.markdown("""
        **MAE (Mean Absolute Error)**: Average prediction error in dollars. Lower is better.
        
        **RMSE (Root Mean Squared Error)**: Emphasizes larger errors more than MAE. Lower is better.
        
        **R² Score**: Proportion of variance explained by the model (0-1). Higher is better.
        """)


def render_feature_importance_section():
    """Display feature importance visualization."""
    st.subheader("Feature Importance Analysis")

    with st.spinner("Loading feature importance data..."):
        importance = get_feature_importance()
    
    if not importance:
        st.error("Unable to load feature importance data")
        return
    
    # Convert to displayable format
    df_importance = pd.DataFrame(importance, columns=['Feature', 'Importance'])
    df_importance['Importance (%)'] = (df_importance['Importance'] * 100).round(1)
    df_importance = df_importance.sort_values('Importance', ascending=False)
    
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        # Bar chart
        st.bar_chart(df_importance.set_index('Feature')['Importance'])
    
    with col2:
        # Table with percentages
        display_df = df_importance[['Feature', 'Importance (%)']].copy()
        st.dataframe(display_df, hide_index=True, width="stretch")
    
    # Key insights
    top_3_importance = df_importance.head(3)['Importance'].sum()
    st.success(f"**Top 3 features explain {top_3_importance*100:.1f}% of predictions**")
    
    with st.expander("💡 Feature Descriptions"):
        st.markdown("""
        **trip_distance_km**: Distance of the trip in kilometers
        
        **distance_x_conditions**: Interaction between distance and weather/traffic conditions
        
        **passenger_count**: Number of passengers
        
        **traffic_multiplier**: Impact of traffic level (Low/Medium/High)
        
        **weather_impact**: Impact of weather conditions (Clear/Rain/Snow)
        """)


def render_glossary_section():
    """Display ML concepts and terminology."""
    st.subheader("Model Algorithms Explained")
    st.text("Below you can find explanations of the three different Machine Learning-models that was trained/tested on our dataset.")
    
    # Model descriptions as expandable cards
    for model, description in MODEL_DESCRIPTIONS.items():
        with st.expander(f"**{model}**"):
            st.write(description)
    
    st.subheader("Technical Terms Glossary")
    
    # Convert glossary to dataframe
    glossary_df = pd.DataFrame([
        {"Term": term, "Definition": definition} 
        for term, definition in GLOSSARY_TERMS.items()
    ])
    
    st.dataframe(glossary_df, hide_index=True, width="stretch")
    