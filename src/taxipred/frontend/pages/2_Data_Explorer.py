import streamlit as st

from taxipred.frontend.ui_helpers import load_css, initialize_prediction_state, reset_prediction_state
from taxipred.frontend.ui_components import render_trip_form, render_prediction_workflow, render_trip_summary
from taxipred.utils.api_helpers import get_dataset, get_stats



def main():
    """Page controller for data exploration."""
    st.set_page_config(page_title="TaxiPred 1.0", layout="wide")
    st.title("Data Explorer", anchor=False)

    df_dataset = get_dataset()
    df_stats = get_stats()


    st.subheader("Dataset Statistics")

    if df_stats:
        dist_stats = df_stats.get('distance_stats', {})
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.metric("Total Records", df_stats.get('total_records', 'N/A'))
        with col2:
            st.metric("Min Distance", f"{dist_stats.get('min', 0):.2f} km")
        with col3:
            st.metric("Max Distance", f"{dist_stats.get('max', 0):.2f} km")
    
        price_stats = df_stats.get('price_stats', {})
        col4, col5, col6, col7 = st.columns(4)
        with col4:
            st.metric("Min Price", f"${price_stats.get('min', 0):.2f}")
        with col5:
            st.metric("Max Price", f"${price_stats.get('max', 0):.2f}")
        with col6:
            st.metric("Mean Price", f"${price_stats.get('mean', 0):.2f}")
        with col7:
            st.metric("Median Price", f"${price_stats.get('median', 0):.2f}")


    with st.expander("Cleaned Dataset"):
        if df_dataset:
            st.dataframe(df_dataset, hide_index=True)


if __name__ == "__main__":
    main()
