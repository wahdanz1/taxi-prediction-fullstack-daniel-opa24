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