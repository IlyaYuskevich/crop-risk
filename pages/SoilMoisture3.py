from datetime import date
import xarray as xr
import streamlit as st
import fsspec
from components.crop_select import add_crop_select
from components.region_select import add_region_select
from components.year_select import add_year_select
from constants.soil_moisture import STAGE_MARKERS
import plotly.graph_objects as go

from constants.utils import stage_bands_daily

st.set_page_config(layout="wide", initial_sidebar_state="expanded", page_title="Drought")

BUCKET = "nala-crop-risks"
ZARR   = "era5-drought/spei_1-3-6_2023-2025.zarr"
storage = {"anon": False, "key": st.secrets.get("AWS_ACCESS_KEY_ID"), 
           "secret": st.secrets.get("AWS_SECRET_ACCESS_KEY"), 
           "client_kwargs": {"region_name": "eu-central-1"}}

mapper = fsspec.get_mapper(f"s3://{BUCKET}/{ZARR}", s3=storage)

ds = xr.open_zarr(mapper, consolidated=True)

region_sel, locations_hashmap = add_region_select()
year_sel = add_year_select() 
crop_sel = add_crop_select()

season_start = f"{year_sel - 1}-09-01"
season_end = f"{year_sel}-09-01"
# Open previous + current crop-year Zarrs and concatenate along time (graceful if one is missing)
years = [year_sel - 1, year_sel]
dss: list[xr.Dataset] = []
for yr in years:
    mapper = fsspec.get_mapper(
        f"s3://{BUCKET}/era5-land/volumetric_soil_water_3_{yr}.zarr", s3=storage
    )
    try:
        dss.append(xr.open_zarr(mapper, consolidated=True))
    except Exception as e:
        print(f"[soil moisture-3] missing or unreadable store for {yr}: {e}")
        continue

if not dss:
    st.warning("No ERA5-Land soil moisture (Level 3) data found for the selected crop year(s).")
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
    ds["swvl3"]
    .sel(locations_hashmap[region_sel], method="nearest")
    .sel(time=slice(season_start, season_end))
)
ts = pt.to_series()

# ---- Plot ----
y_range = [0, 1]
fig = go.Figure()

threshold_cols = ["dry_critical", "dry_warn", "wet_warn", "wet_critical"]
threshold_cols.reverse()
threshold_df = stage_bands_daily(ts.index, STAGE_MARKERS[crop_sel]) 

thresholds_t = threshold_df["time"].to_list()
cols = set(threshold_df.columns)

def thresholds(bound):
    if isinstance(bound, (int, float)):  # constant baseline
        return [float(bound)] * len(thresholds_t)
    if bound in cols:
        return threshold_df[bound].to_list()
    return None  # missing metric -> skip band

# Band configuration (hashmap). Order matters for correct tonexty fills.
BANDS = {
    "dry_critical": {"lo": 0,            "hi": "dry_critical", "fill": "rgba(220, 53, 69, 0.25)", "line": "rgba(220, 53, 69, 0.9)"},
    "dry_warn":     {"lo": "dry_critical","hi": "dry_warn",     "fill": "rgba(255, 193, 7, 0.20)", "line": "rgba(255, 193, 7, 0.9)"},
    "suitable":     {"lo": "dry_warn",    "hi": "wet_warn",     "fill": "rgba(109, 215, 193, 0.25)", "line": "rgba(255, 193, 7, 0.9)"},
    "wet_warn":     {"lo": "wet_warn",    "hi": "wet_critical", "fill": "rgba(255, 193, 7, 0.20)", "line": "rgba(220, 53, 69, 0.9)"},
    "wet_critical": {"lo": "wet_critical","hi": 1,              "fill": "rgba(220, 53, 69, 0.20)", "line": None},
}

for name, cfg in BANDS.items():
    ylo, yhi = thresholds(cfg["lo"]), thresholds(cfg["hi"])
    if ylo is None or yhi is None:
        continue
    # lower (invisible) → upper (filled to previous)
    fig.add_trace(go.Scatter(x=thresholds_t, y=ylo, mode="lines",
                             line=dict(width=0), hoverinfo="skip", showlegend=False))
    line_style = dict(color=cfg["line"], width=1, dash="dot") if cfg.get("line") else dict(width=0)
    fig.add_trace(go.Scatter(
        name=name,
        x=thresholds_t, y=yhi, mode="lines",
        line=line_style,
        fill="tonexty", fillcolor=cfg["fill"],
        hoverinfo="skip", showlegend=False
    ))

fig.add_trace(
    go.Scatter(
        name="Volumetric soil water layer 3",
        x=ts.index,
        y=ts.values,
        mode="lines",
        line=dict(color="black", width=2),
        hovertemplate="Date: %{x|%Y-%m-%d}<br>swvl3: %{y:.2f}<extra></extra>",
    )
)
# dummy trace for legend
fig.add_trace(
    go.Scatter(
        x=[None], y=[None],
        mode="lines",
        line=dict(color="#D6F5E8", width=7),
        name="Suitable"
    )
)
fig.add_trace(
    go.Scatter(
        x=[None], y=[None],
        mode="lines",
        line=dict(color="rgba(255, 193, 7, 0.5)", width=7),
        name="Concerning"
    )
)
fig.add_trace(
    go.Scatter(
        x=[None], y=[None],
        mode="lines",
        line=dict(color="rgba(220, 53, 69, 0.5)", width=7),
        name="Critical"
        )
)
fig.update_layout(
    title=dict(
        text=f"{region_sel} | Volumetric soil water layer 3 (28 - 100cm) <br><span style='font-weight:normal; font-size:0.8em;'>(Crop year {year_sel})</span>",
        x=0.5,
        xanchor="center"
    ),
        height=600,
        width=1000,
        margin=dict(l=60, r=40, t=90, b=60),
        yaxis=dict(title=""),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15)
    )
fig.update_xaxes(range=[season_start, season_end],         
                 dtick="M1",
                 showgrid=True,
                 showline=True,
                 tickformat="%b %y")
fig.update_yaxes(range=y_range, showline=True, title=dict(font=dict(size=20)))

# fig.update_layout(
#     annotations=[
#         dict(
#             text="°C",
#             xref="paper", yref="paper",
#             x=-0.05, y=1.01,
#             showarrow=False,
#             font=dict(size=20),
#             align="left"
#             ),
#     ])


annotation_y = y_range[1] - 1
for stage in STAGE_MARKERS[crop_sel]:
    stage_year = year_sel + stage["year_offset"]
    stage_date = date(stage_year, stage["start_month"], stage["start_day"])
    if date.fromisoformat(season_start) <= stage_date <= date.fromisoformat(season_end):
        fig.add_vline(
            x=stage_date,
            line_width=1,
            line_dash="dash",
            line_color=stage["color"],
        )
        fig.add_annotation(
            x=stage_date,
            y=annotation_y,
            text=stage["label"].replace("\n", "<br>"),
            showarrow=False,
            yanchor="bottom",
            xanchor="left",
            align="left",
            textangle=-90,
            font=dict(size=14, color=stage["color"]),
            xshift=4,
        )
# Add a year changing grid line
jan1 = date(year_sel, 1, 1)
fig.add_vline(
    x=jan1,
    line_width=2,
    line_color="#aeaeae"
)

st.plotly_chart(fig, use_container_width=True)
st.dataframe(ts, use_container_width=True)
