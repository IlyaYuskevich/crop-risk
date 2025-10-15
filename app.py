import streamlit as st

# Hide the "App" menu title in the sidebar
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"]::before {
            content: "";
        }
        [data-testid="stSidebarNav"] > div:first-child {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Weather conditions")
frost = st.Page("pages/frost.py", title="Frost")
heat = st.Page("pages/heat.py", title="Heat")
precipitation = st.Page("pages/precipitation.py", title="Precipitation")
soil_moisture_2 = st.Page("pages/soil_moisture_2.py", title="Soil Moisture 2")
soil_moisture_3 = st.Page("pages/soil_moisture_3.py", title="Soil Moisture 3")
spei = st.Page("pages/spei.py", title="SPEI")

pg = st.navigation([frost, heat, precipitation, soil_moisture_2, soil_moisture_3, spei])
pg.run()
