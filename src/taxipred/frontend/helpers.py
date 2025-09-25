import streamlit as st
import time
from pathlib import Path
from datetime import datetime, time as time_type

from taxipred.utils.helpers import get_api_data, post_api_data

# Load and inject CSS --------------------
def load_css():
    css_file = Path(__file__).parent / "styles.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Rounds time in st.time_input to nearest quarter --------------------
def round_to_quarter(t: time_type, up: bool = False) -> time_type:
    total = t.hour * 60 + t.minute
    if up:
        minutes = ((total + 14) // 15) * 15  # ceiling
    else:
        minutes = (total // 15) * 15         # floor
    h = (minutes // 60) % 24
    m = minutes % 60
    return time_type(hour=h, minute=m)


# Smooth progress bar (Streamlit UI component) --------------------
def smooth_progress(progress_bar, status_text, start, end, message, duration=1.0):
    """Animate progress bar smoothly from start to end percentage."""
    status_text.text(message)
    steps = end - start
    delay = duration / steps if steps > 0 else 0
    
    for i in range(start, end + 1):
        progress_bar.progress(i)
        time.sleep(delay)
