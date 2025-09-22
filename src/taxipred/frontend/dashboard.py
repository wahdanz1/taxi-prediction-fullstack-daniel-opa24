import streamlit as st
from taxipred.frontend.helpers import load_css

# Load CSS
load_css()

def main():
    st.set_page_config(
        layout="wide", 
        page_title="TaxiPred 1.0",
        page_icon="🚕",
        initial_sidebar_state="expanded"
    )

    # Define pages structure
    pages = {
        "TaxiPred 1.0": [
            st.Page("pages/1_Price_Prediction.py", title="Price Prediction", icon="🤑"),
            st.Page("pages/2_Model_Performance.py", title="Model Performance", icon="🤖"),
            st.Page("pages/3_Data_Explorer.py", title="Data Explorer", icon="📊"),
        ],
    }

    # Add navigation
    pg = st.navigation(pages)

    # Run the selected page
    pg.run()

if __name__ == "__main__":
    main()