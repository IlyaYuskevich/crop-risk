from datetime import date
import xarray as xr
import streamlit as st
import fsspec
from components.crop_select import add_crop_select
from components.region_select import add_region_select
from components.timeseries_chart import add_timeseries_chart
from components.year_select import add_year_select
from constants.soil_moisture import STAGE_MARKERS, BANDS

from constants.utils import stage_bands_daily

st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="Soil Moisture")

BUCKET = "nala-crop-risks"
ZARR   = "era5-land/volumetric_soil_water_3_2024.zarr"
storage = {"anon": False, "key": st.secrets.get("AWS_ACCESS_KEY_ID"), 
           "secret": st.secrets.get("AWS_SECRET_ACCESS_KEY"), 
           "client_kwargs": {"region_name": "eu-central-1"}}

mapper = fsspec.get_mapper(f"s3://{BUCKET}/{ZARR}", s3=storage)

ds = xr.open_zarr(mapper, consolidated=True)

region_sel, locations_hashmap = add_region_select()
year_sel = add_year_select() 
crop_sel = add_crop_select()

season_start = date(year_sel - 1, 9, 1)
season_end = date(year_sel, 9, 2)
# Open previous + current crop-year Zarrs and concatenate along time (graceful if one is missing)
years = [year_sel - 1, year_sel]
dss: list[xr.Dataset] = []
for yr in years:
    mapper = fsspec.get_mapper(
        f"s3://{BUCKET}/era5-land/volumetric_soil_water_2_{yr}.zarr", s3=storage
    )
    try:
        dss.append(xr.open_zarr(mapper, consolidated=True))
    except Exception as e:
        print(f"[soil moisture-2] missing or unreadable store for {yr}: {e}")
        continue

if not dss:
    st.warning("No ERA5-Land soil moisture (Level 2) data found for the selected crop year(s).")
    st.stop()
elif len(dss) == 1:
    ds = dss[0]
else:
    ds = xr.concat(
        dss,
        dim="valid_time",
        data_vars="minimal",
        coords="minimal",
        compat="override",
        join="override",
    ).sortby("valid_time")
# Dataset or DataArray both work
mapping = {"latitude": "lat", "longitude": "lon", "valid_time": "time"}
ds = ds.rename(
    {
        k: v
        for k, v in mapping.items()
        if k in ds.dims or k in ds.coords or k in ds.variables
    }
)
pt = (
    ds["swvl2"]
    .sel(locations_hashmap[region_sel], method="nearest")
    .sel(time=slice(season_start, season_end))
)
ts = pt.to_series()
x_range = (season_start, season_end)
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
        "chart_title": "Soil moisture (7 - 28cm)",
        "hovertemplate": "Date: %{x|%Y-%m-%d}<br>swvl2: %{y:.2f}<extra></extra>",
        "line_legend_label": "Volumetric soil water layer 2",
    },
)


st.dataframe(ts, use_container_width=True)
