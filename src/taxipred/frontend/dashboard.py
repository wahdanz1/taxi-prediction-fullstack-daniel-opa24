import streamlit as st
from taxipred.utils.helpers import read_api_endpoint
from taxipred.frontend.helpers import load_css
import pandas as pd
from pathlib import Path

# Load CSS first
load_css()

data = read_api_endpoint("taxi")

df = pd.DataFrame(data.json())


# Main layout
def main():
    st.set_page_config(layout="wide", page_title="🚕 TaxiPred 1.0")

    st.header("TaxiPred 1.0")

    # Columns for search + result
    col1, col2 = st.columns([1,2])

    with col1:
        st.subheader("Your trip")
        your_trip_form()
    with col2:
        st.subheader("Your result")
        if not st.session_state.get("your_trip_form"):
            # RESULT HERE
            st.text("Fel")
        else:
            st.text("Test")

    # Expander containing full, cleaned dataset
    with st.expander(expanded=False, label="Dev"):
        st.subheader("Dataframe for cleaned dataset")
        st.dataframe(df)


def your_trip_form():
    with st.form(key="your_trip_form"):
        st.text_input(label="Where are you going?", placeholder="Enter an address...", width=350)
        st.text_input(label="Where do you want to be picked up?", placeholder="Enter an address...", width=350)
        st.time_input(label="When do you want to be picked up?")
        st.form_submit_button()


if __name__ == "__main__":
    main()
