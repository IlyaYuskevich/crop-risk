from datetime import date

import fsspec
import streamlit as st
import xarray as xr

from components.crop_select import add_crop_select
from components.region_select import add_region_select
from components.timeseries_chart import add_timeseries_chart
from components.year_select import add_year_select
from constants.crops import SEASON_BOUNDARIES
from constants.frost import BANDS, STAGE_MARKERS

BUCKET = "nala-crop-risks"
storage = {
    "anon": False,
    "key": st.secrets.get("AWS_ACCESS_KEY_ID"),
    "secret": st.secrets.get("AWS_SECRET_ACCESS_KEY"),
    "client_kwargs": {"region_name": "eu-central-1"},
}

region_sel, locations_hashmap = add_region_select()
year_sel = add_year_select()
crop_sel = add_crop_select()

st.set_page_config(f"{region_sel} | Low Temperatures", layout="wide")

season = SEASON_BOUNDARIES[crop_sel]
season_start = date(year_sel - 1, season["start_month"], season["start_day"])
season_end = date(year_sel, season["end_month"], season["end_day"])
# Open previous + current crop-year Zarrs and concatenate along time (graceful if one is missing)
years = [year_sel - 1, year_sel]
dss: list[xr.Dataset] = []
for yr in years:
    mapper = fsspec.get_mapper(
        f"s3://{BUCKET}/era5-land/2m_temperature_min_{yr}.zarr", s3=storage
    )
    try:
        dss.append(xr.open_zarr(mapper, consolidated=True))
    except Exception as e:
        print(f"[heat] missing or unreadable store for {yr}: {e}")
        continue

if not dss:
    st.warning("No ERA5-Land temperature data found for the selected crop year(s).")
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
    ds["t2m"]
    .sel(locations_hashmap[region_sel], method="nearest")
    .sel(time=slice(season_start, season_end))
)
ts = pt.to_series()
ts = ts - 273.15
x_range = (season_start, season_end)
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
