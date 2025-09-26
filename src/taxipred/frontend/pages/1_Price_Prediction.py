import streamlit as st

from taxipred.frontend.ui_helpers import load_css, initialize_prediction_state, reset_prediction_state
from taxipred.frontend.ui_components import render_trip_form, render_prediction_workflow, render_trip_summary



def main():
    """Main page controller for taxi price prediction."""
    st.set_page_config(page_title="TaxiPred 1.0", layout="wide")
    st.title("Taxi Price Prediction", anchor=False)

    initialize_prediction_state()

    if not st.session_state.processing and not st.session_state.prediction_complete:
        # State 1: Input form
        form_submitted = render_trip_form()
        if form_submitted:
            st.session_state.processing = True
            st.rerun()
    
    elif st.session_state.processing:
        # State 2: Processing with progress
        render_prediction_workflow(st.session_state.get('form_data'))
    
    elif st.session_state.prediction_complete:
        # State 3: Results display
        render_trip_summary(st.session_state.trip_data)
        
        if st.button("New Trip Prediction", type="primary", use_container_width=True):
            reset_prediction_state()
            st.rerun()


if __name__ == "__main__":
    main()
