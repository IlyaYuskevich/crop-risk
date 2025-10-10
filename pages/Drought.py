from datetime import date
import xarray as xr
import streamlit as st
import fsspec
from constants.drought import STAGE_MARKERS
from constants.locations import LOCATIONS
import plotly.graph_objects as go

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

region_sel = st.sidebar.selectbox(
    "Region",
    region_options,
    index=region_options.index(region_options[0]),
)

agri_years: list[int] = list(range(2024, 2026))
year_sel = int(st.sidebar.selectbox("Crop year", agri_years, index=len(agri_years)-1))

season_start = f"{year_sel - 1}-09-01"
season_end = f"{year_sel}-09-01"
pt = ds["SPEI1"].sel(locations_hashmap[region_sel], method="nearest").sel(time=slice(season_start, season_end))

ts = pt.to_series()

# ---- Plot ----
y_range = [-5, 5]
fig = go.Figure()

threshold_cols = {"low_temp", "warn_temp", "alert_temp"}
# threshold_df = threshold_df.sort_values("dt")
# x_vals = threshold_df["dt"]
# low_vals = threshold_df["low_temp"]
# warn_vals = threshold_df["warn_temp"]
# alert_vals = threshold_df["alert_temp"]
# top_vals = [y_range[1]] * len(threshold_df)
        

# fig.add_trace(
#     go.Scatter(
#         name="Low temperature",
#         x=x_vals,
#         y=low_vals,
#         mode="lines",
#         line=dict(color="rgba(46, 125, 50, 0.9)", dash="dot", width=1),
#         hoverinfo="skip",
#         showlegend=False
#     )
# )

# fig.add_trace(
#     go.Scatter(
#         name="Warning threshold",
#         x=x_vals,
#         y=warn_vals,
#         mode="lines",
#         line=dict(color="rgba(255, 193, 7, 0.9)", dash="dot", width=1),
#         fill="tonexty",
#         fillcolor="rgba(109, 215, 193, 0.25)",
#         hoverinfo="skip",
#         showlegend=False
#     )
# )

# fig.add_trace(
#     go.Scatter(
#         name="Alert threshold",
#         x=x_vals,
#         y=alert_vals,
#         mode="lines",
#         line=dict(color="rgba(220, 53, 69, 0.9)", dash="dot", width=1),
#         fill="tonexty",
#         fillcolor="rgba(255, 193, 7, 0.25)",
#         hoverinfo="skip",
#         showlegend=False
#     )
# )

# fig.add_trace(
#     go.Scatter(
#         name="Extreme alert zone",
#         x=x_vals,
#         y=top_vals,
#         mode="lines",
#         line=dict(width=0),
#         fill="tonexty",
#         fillcolor="rgba(220, 53, 69, 0.20)",
#         hoverinfo="skip",
#         showlegend=False,
#             )
#         )

fig.add_trace(
    go.Scatter(
        name="SPEI(1-mo)",
        x=ts.index,
        y=ts.values,
        mode="lines",
        line=dict(color="black", width=2),
        hovertemplate="Date: %{x|%Y-%m-%d}<br>SPEI: %{y:.1f}<extra></extra>",
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
        text=f"{region_sel} | SPEI - Standardized moisture anomaly <br><span style='font-weight:normal; font-size:0.8em;'>(Crop year {year_sel})</span>",
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
for stage in STAGE_MARKERS:
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
            yshift=-390
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

# small readout for the latest value
if len(ts) > 0:
    st.metric("Latest SPEI(1-mo)", f"{ts.iloc[-1]:.2f}", help="Standardized anomaly; <0 dry, >0 wet")