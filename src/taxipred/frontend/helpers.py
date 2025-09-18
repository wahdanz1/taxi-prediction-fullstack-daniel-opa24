import streamlit as st
from pathlib import Path

# Load and inject CSS
def load_css():
    css_file = Path(__file__).parent / "styles.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Function for setting the background on the different pages
def set_background(url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{url}");
            background-attachment: fixed;
            background-size: cover;
            background-repeat: no-repeat;
            background-position: top center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )