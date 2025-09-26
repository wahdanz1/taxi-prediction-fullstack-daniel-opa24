import streamlit as st

from taxipred.frontend.ui_helpers import load_css, initialize_prediction_state, reset_prediction_state
from taxipred.frontend.ui_components import render_trip_form, render_prediction_workflow, render_trip_summary



def main():
    """Page controller for model performance info."""
    st.set_page_config(page_title="TaxiPred 1.0", layout="wide")
    st.title("Model Performance", anchor=False)


if __name__ == "__main__":
    main()
