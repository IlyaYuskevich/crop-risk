from datetime import date

import streamlit as st
import polars as pl
import plotly.graph_objects as go

from constants.drought import AGRI_MONTHS, STAGE_MARKERS
from data_transformations.heat import calc_heat_wave_alerts

params = st.query_params
raw_region = params.get("region")

lf = pl.scan_parquet("./data/source.parquet").with_columns(
        (pl.col("total_precipitation_sum") * 1e3).alias("precipitation")
    ).with_columns(
    pl.when(pl.col("dt").dt.month().is_in([9, 10, 11, 12]))
      .then(pl.col("dt").dt.year() + 1)
      .otherwise(pl.col("dt").dt.year())
      .alias("agri_year"),
    pl.col("precipitation").rolling_sum_by("dt", window_size="30d").over("name").alias("precipitation_10d")
    )

region_options = (
    lf.select(pl.col("name").unique().sort())
      .collect()
      .to_series()
      .to_list()
)

if not region_options:
    st.error("No regions available in dataset")
    st.stop()

default_region = raw_region if raw_region in region_options else region_options[0]
st.set_page_config(f"{default_region} | Air Temp", layout="wide")

region = st.sidebar.selectbox(
    "Region",
    region_options,
    index=region_options.index(default_region),
)

if region != raw_region:
    try:
        params["region"] = region
    except TypeError:
        st.experimental_set_query_params(region=region)

# ---- Collect available years ----
agri_years: list[int] = (
    lf.filter(pl.col("dt").dt.month().is_in(AGRI_MONTHS))
      .select(pl.col("agri_year").unique().cast(pl.Int32))
      .collect()
      .to_series()
      .sort()
      .to_list()
)
year_sel = int(st.sidebar.selectbox("Crop year", agri_years, index=len(agri_years)-1))

# ---- Filter ----
region_year = (
    lf.filter(
        (pl.col("name") == region)
        & (pl.col("agri_year") == year_sel)
        & (pl.col("dt").dt.month().is_in(AGRI_MONTHS))
    )
      .select(["dt", "precipitation_10d", "agri_year"])
      .sort("dt")
      .collect()
)

# --- Add stage label column (eager) ---
season_start = date(year_sel - 1, 9, 1)
season_end = date(year_sel, 8, 31)

# Build stage intervals for this agri_year
stage_rows = []
for s in STAGE_MARKERS:
    start = date(year_sel + s["year_offset"], s["start_month"], s["start_day"])
    stage_rows.append({"label": s["label"], "stage_start": start, "low_precip": s["low_precip"]})
stage_rows = sorted(stage_rows, key=lambda r: r["stage_start"]) 
for i in range(len(stage_rows)):
    next_start = stage_rows[i + 1]["stage_start"] if i + 1 < len(stage_rows) else season_end
    stage_rows[i]["stage_end"] = next_start

stage_df = pl.DataFrame(stage_rows)

# Map each row to its active stage
region_year = (
    region_year
    .join_asof(stage_df, left_on="dt", right_on="stage_start", strategy="backward")
    .filter(pl.col("dt") < pl.col("stage_end"))
)

# heat_waves = calc_heat_wave_alerts(region_year)

# if heat_waves.get("warning"):
    # components.html(f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="LemonChiffon" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-triangle-alert-icon lucide-triangle-alert"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg><div style="color: coral;font-weight: bold;font-family: sans-serif;display:inline;margin-left:5px;position:relative;bottom:5px">Heat Stress during {", ".join(heat_waves.get("warning", []))}</div>', height=40)
# if heat_waves.get("alert"):
    # components.html(f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="LemonChiffon" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-triangle-alert-icon lucide-triangle-alert"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg><div style="color: red;font-weight: bold;font-family: sans-serif;display:inline;margin-left:5px;position:relative;bottom:5px">Extreme Heat Stress during {", ".join(heat_waves.get("alert", []))}</div>', height=40)

# ---- Plot ----
if region_year.height > 0:
    y_range = [0, 360]
    region_pd = region_year.to_pandas().sort_values("dt")
    fig = go.Figure()

    threshold_cols = {"low_precip"}
    if threshold_cols.issubset(region_pd.columns):
        threshold_df = region_pd.dropna(subset=list(threshold_cols))
        if not threshold_df.empty:
            threshold_df = threshold_df.sort_values("dt")
            x_vals = threshold_df["dt"]
            low_vals = threshold_df["low_precip"]
            zero_precip = [y_range[0]] * len(threshold_df)

            fig.add_trace(
                go.Scatter(
                    name="Warning threshold",
                    x=x_vals,
                    y=low_vals,
                    mode="lines",
                    fill="tonexty",
                     line=dict(color="rgba(220, 53, 69, 0.9)", dash="dash"),
                    fillcolor="rgba(220, 53, 69, 0.20)",
                    hoverinfo="skip",
                    showlegend=False
                )
            )

    fig.add_trace(
        go.Scatter(
            name="Precipitation (30-day rolling sum)",
            x=region_pd["dt"],
            y=region_pd["precipitation_10d"],
            mode="lines",
            line=dict(color="black", width=2),
            hovertemplate="Date: %{x|%Y-%m-%d}<br>Precipitation: %{y:.1f} mm<extra></extra>",
        )
    )
    
    fig.update_layout(
        title=dict(
            text=f"{region} | Precipatation <br><span style='font-weight:normal; font-size:0.8em;'>(Crop year {year_sel})</span>",
            x=0.5,
            xanchor="center"
        ),
        height=600,
        margin=dict(l=60, r=40, t=90, b=60),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15)
        )
    fig.update_xaxes(range=[season_start, season_end],         
                     dtick="M1",
                     showgrid=True,
                     showline=True,
                     tickformat="%b %y")
    fig.update_yaxes(range=y_range, showline=True)
    fig.update_layout(
        annotations=[
            dict(
                text="mm",
                xref="paper", yref="paper",
                x=-0.05, y=0.98,
                showarrow=False,
                font=dict(size=18),
                align="left"
                ),
        ])
    
    annotation_y = y_range[1] - 1
    for stage in STAGE_MARKERS:
        stage_year = year_sel + stage["year_offset"]
        stage_date = date(stage_year, stage["start_month"], stage["start_day"])
        if season_start <= stage_date <= season_end:
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

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(region_pd, use_container_width=True)
else:
    st.warning(f"No data for {region} in crop year {year_sel}")

