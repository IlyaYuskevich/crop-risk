from datetime import datetime

import streamlit as st


def add_year_select(year_options: list[int] = list(range(2023, 2027))) -> int:
    params = st.query_params
    print(st.session_state)
    raw_year = (
        st.session_state.get("prev_year")
        if st.session_state.get("prev_year")
        else params.get("year")
    )

    default_year = raw_year if raw_year in year_options else datetime.now().year

    year_sel = int(
        st.sidebar.selectbox(
            "Crop year",
            year_options,
            index=year_options.index(default_year),
            key="year",
        )
    )
    params["year"] = st.session_state.get("year")
    st.session_state["prev_year"] = st.session_state.get("year")
    return year_sel
