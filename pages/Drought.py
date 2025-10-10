import xarray as xr
import streamlit as st
import fsspec
from constants.locations import LOCATIONS

BUCKET = "nala-crop-risks"
ZARR   = "era5-drought/spei_1-3-6_2023-2025.zarr"
storage = {"anon": False, "key": st.secrets.get("AWS_ACCESS_KEY_ID"), 
           "secret": st.secrets.get("AWS_SECRET_ACCESS_KEY"), 
           "client_kwargs": {"region_name": "eu-central-1"}}

mapper = fsspec.get_mapper(f"s3://{BUCKET}/{ZARR}", s3=storage)

@st.cache_data(show_spinner=False)
def open_ds():
    # If you wrote Zarr v2 + consolidated metadata, this is optimal
    return xr.open_zarr(mapper, consolidated=True)

ds = open_ds()

locations_hashmap: dict[str, dict[str, float]] = {l["label"]: {k: l[k] for k in ("lat", "lon")} for l in LOCATIONS}
region_options: list[str] = list(locations_hashmap.keys())

region = st.sidebar.selectbox(
    "Region",
    region_options,
    index=region_options.index(region_options[0]),
)

pt = ds["SPEI1"].sel(locations_hashmap[region], method="nearest").sel(time=slice("2024-09-01", "2025-09-01"))

ts = pt.to_series()

st.line_chart(ts)
st.caption(f"SPEI-1 {region}")

# small readout for the latest value
if len(ts) > 0:
    st.metric("Latest SPEI(1-mo)", f"{ts.iloc[-1]:.2f}", help="Standardized anomaly; <0 dry, >0 wet")