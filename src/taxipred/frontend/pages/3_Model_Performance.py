import streamlit as st

from taxipred.frontend.ui_helpers import load_css
from taxipred.frontend.ui_components import (
    render_metrics_section,
    render_feature_importance_section,
    render_glossary_section
)

load_css()

def main():
    """Page controller for model performance info."""
    st.set_page_config(page_title="TaxiPred 1.0 - Model Performance", layout="wide")
    st.title("Model Performance", anchor=False)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📊 Performance Metrics", "🎯 Feature Importance", "📚 ML Glossary"])
    
    with tab1:
        render_metrics_section()
    
    with tab2:
        render_feature_importance_section()
    
    with tab3:
        render_glossary_section()


if __name__ == "__main__":
    main()
