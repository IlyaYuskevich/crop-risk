from datetime import datetime

import streamlit as st

from components.crop_select import add_crop_select
from components.region_select import add_region_select
from components.timeseries_chart import add_timeseries_chart
from components.year_select import add_year_select
from constants.soil_moisture import BANDS, STAGE_MARKERS
from dal.fetch_data import fetch_data

st.set_page_config(
    layout="wide", initial_sidebar_state="expanded", page_title="Soil Moisture 3"
)

region_sel, locations_hashmap = add_region_select()
year_sel = add_year_select()
crop_sel = add_crop_select()

ts = fetch_data(
    year_sel,
    crop_sel,
    locations_hashmap[region_sel]["lat"],
    locations_hashmap[region_sel]["lon"],
    "volumetric_soil_water_3",
)

x_range = (
    datetime.fromisoformat(str(ts.index[0])).date(),
    datetime.fromisoformat(str(ts.index[-1])).date(),
)
y_range = (0, 1)

# ---- Plot ----
add_timeseries_chart(
    ts,
    crop_sel,
    region_sel,
    year_sel,
    x_range,
    y_range,
    BANDS,
    STAGE_MARKERS,
    {
        "y_title": None,
        "chart_title": "Soil moisture (28 - 100cm)",
        "hovertemplate": "Date: %{x|%Y-%m-%d}<br>swvl3: %{y:.2f}<extra></extra>",
        "line_legend_label": "Volumetric soil water layer 3",
    },
)


st.dataframe(ts, use_container_width=True)
