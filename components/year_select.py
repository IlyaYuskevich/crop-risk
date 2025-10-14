import streamlit as st
from datetime import datetime

def add_year_select(year_options: list[int] = list(range(2023, 2027))) -> int:
    params = st.query_params
    raw_year = params.get("year")
    
    default_year = raw_year if raw_year in year_options else datetime.now().year

    year_sel = int(st.sidebar.selectbox("Crop year", year_options, index=year_options.index(default_year)))
    if year_sel != raw_year:
        params["year"] = year_sel
    return year_sel