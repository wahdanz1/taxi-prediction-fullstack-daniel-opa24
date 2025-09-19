import streamlit as st
from pathlib import Path

# Load and inject CSS
def load_css():
    css_file = Path(__file__).parent / "styles.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
