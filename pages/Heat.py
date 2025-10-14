from datetime import date
import xarray as xr
import fsspec
import streamlit as st
import plotly.graph_objects as go

from constants.heat import STAGE_MARKERS
from constants.locations import LOCATIONS
from data_transformations.heat import calc_heat_wave_alerts
import streamlit.components.v1 as components

from constants.utils import stage_bands_daily

BUCKET = "nala-crop-risks"
storage = {
    "anon": False,
    "key": st.secrets.get("AWS_ACCESS_KEY_ID"),
    "secret": st.secrets.get("AWS_SECRET_ACCESS_KEY"),
    "client_kwargs": {"region_name": "eu-central-1"},
}


locations_hashmap: dict[str, dict[str, float]] = {
    l["label"]: {k: l[k] for k in ("lat", "lon")} for l in LOCATIONS
}
region_options: list[str] = list(locations_hashmap.keys())

params = st.query_params
raw_region = params.get("region")

default_region = raw_region if raw_region in region_options else region_options[0]

region_sel = st.sidebar.selectbox(
    "Region",
    region_options,
    index=region_options.index(region_options[0]),
)

st.set_page_config(f"{default_region} | Air Temp", layout="wide")

if region_sel != raw_region:
    try:
        params["region"] = region_sel
    except TypeError:
        st.experimental_set_query_params(region=region_sel)


agri_years: list[int] = list(range(2023, 2027))
year_sel = int(st.sidebar.selectbox("Crop year", agri_years, index=len(agri_years) - 1))

season_start = f"{year_sel - 1}-09-01"
season_end = f"{year_sel}-09-01"
# Open previous + current crop-year Zarrs and concatenate along time (graceful if one is missing)
years = [year_sel - 1, year_sel]
dss: list[xr.Dataset] = []
for y in years:
    mapper = fsspec.get_mapper(
        f"s3://{BUCKET}/era5-land/2m_temperature_max_{y}.zarr", s3=storage
    )
    try:
        dss.append(xr.open_zarr(mapper, consolidated=True))
    except Exception as e:
        print(f"[heat] missing or unreadable store for {y}: {e}")
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
print(ds)
pt = (
    ds["t2m"]
    .sel(locations_hashmap[region_sel], method="nearest")
    .sel(time=slice(season_start, season_end))
)
ts = pt.to_series()
ts = ts - 273.15

# ---- Plot ----
y_range = [-10, 40]
fig = go.Figure()

threshold_cols = ["dry_critical", "dry_warn", "wet_warn", "wet_critical"]
threshold_cols.reverse()
threshold_df = stage_bands_daily(ts.index, STAGE_MARKERS)

wide = threshold_df.pivot(index="time", on="metric", values="value").sort("time")

x = wide["time"].to_list()
cols = set(wide.columns)


def y(bound):
    if isinstance(bound, (int, float)):  # constant baseline
        return [float(bound)] * len(x)
    if bound in cols:
        return wide[bound].to_list()
    return None  # missing metric -> skip band


# heat_waves = calc_heat_wave_alerts(ts, threshold_df)

# if heat_waves.get("warning"):
#     components.html(f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="LemonChiffon" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-triangle-alert-icon lucide-triangle-alert"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg><div style="color: coral;font-weight: bold;font-family: sans-serif;display:inline;margin-left:5px;position:relative;bottom:5px">Heat Stress during {", ".join(heat_waves.get("warning", []))}</div>', height=40)
# if heat_waves.get("alert"):
#     components.html(f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="LemonChiffon" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-triangle-alert-icon lucide-triangle-alert"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg><div style="color: red;font-weight: bold;font-family: sans-serif;display:inline;margin-left:5px;position:relative;bottom:5px">Extreme Heat Stress during {", ".join(heat_waves.get("alert", []))}</div>', height=40)


# Band configuration (hashmap). Order matters for correct tonexty fills.
BANDS = {
    "low_temp": {"lo": y_range[0], "hi": "low_temp", "fill": "rgba(0, 0, 0, 0)", "line": None},
    "suitable": {
        "lo": "low_temp",
        "hi": "warn_temp",
        "fill": "rgba(109, 215, 193, 0.25)",
        "line": "rgba(255, 193, 7, 0.9)",
    },
    "warn_temp": {
        "lo": "warn_temp",
        "hi": "alert_temp",
        "fill": "rgba(255, 193, 7, 0.20)",
        "line": "rgba(220, 53, 69, 0.9)",
    },
    "alert_temp": {
        "lo": "alert_temp",
        "hi": y_range[1],
        "fill": "rgba(220, 53, 69, 0.20)",
        "line": None,
    },
}

for name, cfg in BANDS.items():
    ylo, yhi = y(cfg["lo"]), y(cfg["hi"])
    if ylo is None or yhi is None:
        continue
    # lower (invisible) → upper (filled to previous)
    fig.add_trace(
        go.Scatter(
            x=x,
            y=ylo,
            mode="lines",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    line_style = (
        dict(color=cfg["line"], width=1, dash="dot")
        if cfg.get("line")
        else dict(width=0)
    )
    fig.add_trace(
        go.Scatter(
            name=name,
            x=x,
            y=yhi,
            mode="lines",
            line=line_style,
            fill="tonexty",
            fillcolor=cfg["fill"],
            hoverinfo="skip",
            showlegend=False,
        )
    )

fig.add_trace(
    go.Scatter(
        name="Max air temperature (3-day mean)",
        x=ts.index,
        y=ts.values,
        mode="lines",
        line=dict(color="black", width=2),
        hovertemplate="Date: %{x|%Y-%m-%d}<br>Temperature: %{y:.1f}°C<extra></extra>",
    )
)
# dummy trace for legend
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="lines",
        line=dict(color="#D6F5E8", width=7),
        name="Suitable Temperature",
    )
)
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="lines",
        line=dict(color="rgba(255, 193, 7, 0.5)", width=7),
        name="Concerning Temperature",
    )
)
fig.add_trace(
    go.Scatter(
        x=[None],
        y=[None],
        mode="lines",
        line=dict(color="rgba(220, 53, 69, 0.5)", width=7),
        name="Critical Temperature",
    )
)
fig.update_layout(
    title=dict(
        text=f"{region_sel} | Heat Stress <br><span style='font-weight:normal; font-size:0.8em;'>(Crop year {year_sel})</span>",
        x=0.5,
        xanchor="center",
    ),
    height=600,
    margin=dict(l=60, r=40, t=90, b=60),
    yaxis=dict(title=""),
    legend=dict(orientation="h", yanchor="bottom", y=-0.15),
)
fig.update_yaxes(range=y_range, showline=True, title=dict(font=dict(size=20)))

fig.update_layout(
    annotations=[
        dict(
            text="°C",
            xref="paper",
            yref="paper",
            x=-0.05,
            y=1.01,
            showarrow=False,
            font=dict(size=20),
            align="left",
        ),
    ]
)

annotation_y = y_range[1] - 1
for stage in STAGE_MARKERS:
    stage_year = year_sel + stage["year_offset"]
    stage_date = date(stage_year, stage["start_month"], stage["start_day"])
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
        yshift=-420
    )
# Add a year changing grid line
jan1 = date(year_sel, 1, 1)
fig.add_vline(
    x=jan1,
    line_width=2,
    line_color="#aeaeae"
)
fig.update_xaxes(
    range=[season_start, season_end],
    dtick="M1",
    showgrid=True,
    showline=True,
    tickformat="%b %y",
)


st.plotly_chart(fig, use_container_width=True)
