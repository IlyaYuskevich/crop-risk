from datetime import date

import fsspec
import streamlit as st
import xarray as xr

from components.crop_select import add_crop_select
from components.region_select import add_region_select
from components.timeseries_chart import add_timeseries_chart
from components.year_select import add_year_select
from constants.crops import SEASON_BOUNDARIES
from constants.drought import BANDS, STAGE_MARKERS

st.set_page_config(
    layout="wide", initial_sidebar_state="expanded", page_title="Drought"
)

BUCKET = "nala-crop-risks"
ZARR = "era5-drought/spei_1-3-6_2023-2025.zarr"
storage = {
    "anon": False,
    "key": st.secrets.get("AWS_ACCESS_KEY_ID"),
    "secret": st.secrets.get("AWS_SECRET_ACCESS_KEY"),
    "client_kwargs": {"region_name": "eu-central-1"},
}

mapper = fsspec.get_mapper(f"s3://{BUCKET}/{ZARR}", s3=storage)

ds = xr.open_zarr(mapper, consolidated=True)

region_sel, locations_hashmap = add_region_select()
year_sel = add_year_select(list(range(2023, 2026)))
crop_sel = add_crop_select()

season = SEASON_BOUNDARIES[crop_sel]
season_start = date(year_sel - 1, season["start_month"], season["start_day"])
season_end = date(year_sel, season["end_month"], season["end_day"])

x_range = (season_start, season_end)
y_range = (-5, 5)
pt = (
    ds["SPEI1"]
    .sel(locations_hashmap[region_sel], method="nearest")
    .sel(time=slice(season_start, season_end))
)
ts = pt.to_series()

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
        "hovertemplate": "Date: %{x|%Y-%m-%d}<br>SPEI: %{y:.1f}<extra></extra>",
        "y_title": None,
        "chart_title": "Drought Index - SPEI (Standardized Precipitation Evapotranspiration Index)",
        "line_legend_label": "SPEI(1-mo)"
    },
)

st.dataframe(ts, use_container_width=True)

# small readout for the latest value
if len(ts) > 0:
    st.metric(
        "Latest SPEI(1-mo)",
        f"{ts.iloc[-1]:.2f}",
        help="Standardized anomaly; <0 dry, >0 wet",
    )
