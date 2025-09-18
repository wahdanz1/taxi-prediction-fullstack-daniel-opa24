import streamlit as st
from taxipred.utils.helpers import read_api_endpoint
from taxipred.frontend.helpers import set_background, load_css
import pandas as pd
from pathlib import Path

# Load CSS first
load_css()

data = read_api_endpoint("taxi")

df = pd.DataFrame(data.json())


def main():
    st.set_page_config(layout="wide", page_title="🚕 TaxiPred 1.0")
    st.header("TaxiPred 1.0")
    with st.expander(expanded=True, label="Dev"):
        st.subheader("Dataframe for full dataset")
        st.dataframe(df)



if __name__ == "__main__":
    main()
