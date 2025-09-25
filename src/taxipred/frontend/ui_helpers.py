import streamlit as st
import time
from pathlib import Path
from datetime import time as time_type


# CSS and styling
def load_css():
    """Load and inject custom CSS styles into Streamlit app."""
    css_file = Path(__file__).parent / "styles.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Session state management
def initialize_prediction_state():
    """Initialize session state variables for the prediction workflow."""
    if "prediction_complete" not in st.session_state:
        st.session_state.prediction_complete = False
    if "trip_data" not in st.session_state:
        st.session_state.trip_data = None
    if "processing" not in st.session_state:
        st.session_state.processing = False

def reset_prediction_state():
    """Reset all session state for new prediction."""
    st.session_state.prediction_complete = False
    st.session_state.processing = False
    st.session_state.trip_data = None
    if 'form_data' in st.session_state:
        del st.session_state.form_data

def handle_processing_error(progress_bar, status_text, error_message: str):
    """Handle processing errors with user feedback and state reset."""
    progress_bar.progress(100)
    status_text.text("Processing failed")
    time.sleep(1)
    progress_bar.empty()
    status_text.empty()
    st.error(error_message)
    
    st.session_state.processing = False
    time.sleep(2)
    st.rerun()


# Time utilities
def round_to_quarter(t: time_type, up: bool = False) -> time_type:
    """
    Round time to nearest quarter hour for cleaner user input.
    
    Args:
        t: Time object to round
        up: If True, round up (ceiling), otherwise round down (floor)
        
    Returns:
        Time object rounded to nearest quarter hour
    """
    total_minutes = t.hour * 60 + t.minute
    
    if up:
        rounded_minutes = ((total_minutes + 14) // 15) * 15  # Round up
    else:
        rounded_minutes = (total_minutes // 15) * 15  # Round down
    
    hours = (rounded_minutes // 60) % 24
    minutes = rounded_minutes % 60
    
    return time_type(hour=hours, minute=minutes)


# UI animations  
def smooth_progress(progress_bar, status_text, start: int, end: int, 
                    message: str, duration: float = 1.0):
    """
    Animate progress bar smoothly from start to end percentage.
    
    Args:
        progress_bar: Streamlit progress bar object
        status_text: Streamlit text object for status messages
        start: Starting percentage (0-100)
        end: Ending percentage (0-100)  
        message: Status message to display
        duration: Animation duration in seconds
    """
    status_text.text(message)
    steps = end - start
    delay = duration / steps if steps > 0 else 0
    
    for i in range(start, end + 1):
        progress_bar.progress(i)
        time.sleep(delay)