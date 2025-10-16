from datetime import datetime

import streamlit as st

from components.crop_select import add_crop_select
from components.region_select import add_region_select
from components.timeseries_chart import add_timeseries_chart
from components.year_select import add_year_select
from constants.frost import BANDS, STAGE_MARKERS
from dal.fetch_data import fetch_data

region_sel, locations_hashmap = add_region_select()
year_sel = add_year_select()
crop_sel = add_crop_select()

st.set_page_config(f"{region_sel} | Low Temperatures", layout="wide")

ts = fetch_data(
    year_sel,
    crop_sel,
    locations_hashmap[region_sel]["lat"],
    locations_hashmap[region_sel]["lon"],
    "2m_temperature_min",
)

ts = ts - 273.15
x_range = (
    datetime.fromisoformat(str(ts.index[0])).date(),
    datetime.fromisoformat(str(ts.index[-1])).date(),
)
y_range = (-30, 40)

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
        "y_title": "°C",
        "chart_title": "Frost",
        "hovertemplate": "Date: %{x|%Y-%m-%d}<br>Temperature: %{y:.1f}°C<extra></extra>",
        "line_legend_label": "Min air temperature (3-day mean)",
    },
)

# heat_waves = calc_heat_wave_alerts(ts, threshold_df)

# if heat_waves.get("warning"):
#     components.html(f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="LemonChiffon" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-triangle-alert-icon lucide-triangle-alert"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg><div style="color: coral;font-weight: bold;font-family: sans-serif;display:inline;margin-left:5px;position:relative;bottom:5px">Heat Stress during {", ".join(heat_waves.get("warning", []))}</div>', height=40)
# if heat_waves.get("alert"):
#     components.html(f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="LemonChiffon" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-triangle-alert-icon lucide-triangle-alert"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg><div style="color: red;font-weight: bold;font-family: sans-serif;display:inline;margin-left:5px;position:relative;bottom:5px">Extreme Heat Stress during {", ".join(heat_waves.get("alert", []))}</div>', height=40)


st.dataframe(ts, use_container_width=True)
