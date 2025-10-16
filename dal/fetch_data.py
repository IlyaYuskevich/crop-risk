import typing as t
from datetime import date

import fsspec
import pandas as pd
import streamlit as st
import xarray as xr

from app_types.types import CropSpecies, WeatherIndicator
from constants.crops import SEASON_BOUNDARIES
from constants.s3 import BUCKET
from ingestion.configs import INDICATOR_NAME_TO_CONFIG

storage = {
    "anon": False,
    "key": st.secrets.get("AWS_ACCESS_KEY_ID"),
    "secret": st.secrets.get("AWS_SECRET_ACCESS_KEY"),
    "client_kwargs": {"region_name": "eu-central-1"},
}

@st.cache_data
def fetch_data(
    year_sel: int,
    crop_sel: CropSpecies,
    lat: float,
    lon: float,
    indicator_name: WeatherIndicator,
) -> pd.Series:
    config = INDICATOR_NAME_TO_CONFIG[indicator_name]
    season = SEASON_BOUNDARIES[crop_sel]
    season_start = date(year_sel - 1, season["start_month"], season["start_day"])
    season_end = date(year_sel, season["end_month"], season["end_day"])
    # Open previous + current crop-year Zarrs and concatenate along time (graceful if one is missing)
    years = [year_sel - 1, year_sel]
    dss: list[xr.Dataset] = []
    for yr in years:
        mapper = fsspec.get_mapper(
            f"s3://{BUCKET}/{config['path']}{indicator_name}_{yr}.zarr", s3=storage
        )
        try:
            dss.append(xr.open_zarr(mapper, consolidated=True))
        except Exception as e:
            print(f"{indicator_name} missing or unreadable store for {yr}: {e}")
            continue

    if not dss:
        st.warning(f"No {indicator_name} data found for the selected crop year(s).")
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
        ds[config["var_name"]]
        .sel({"lat": lat, "lon": lon}, method="nearest")
        .sel(time=slice(season_start, season_end))
    )
    return pt.to_series()
