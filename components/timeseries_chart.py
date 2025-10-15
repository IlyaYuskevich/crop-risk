import typing as t
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app_types.types import CropToStages, PlotThresholdsConfig
from constants.crops import CropSpecies
from constants.utils import stage_bands_daily


class BandsConfig(t.TypedDict):
    lo: str | int | float | None
    hi: str | int | float | None
    fill: str
    line: str
    
class ChartConfig(t.TypedDict):
    hovertemplate: str
    y_title: str | None
    chart_title: str
    line_legend_label: str


def add_timeseries_chart(
    ts: pd.Series,
    crop_sel: CropSpecies,
    region_sel: str,
    year_sel: int,
    x_range: tuple[date, date],
    y_range: tuple[int | float, int | float],
    bands: PlotThresholdsConfig,
    crop_stages: CropToStages,
    chart_config: ChartConfig
) -> None:
    fig = go.Figure()

    threshold_df = stage_bands_daily(ts.index, crop_stages[crop_sel])

    thresholds_t = threshold_df["time"].to_list()
    cols = set(threshold_df.columns)

    def thresholds(bound):
        if isinstance(bound, (int, float)):  # constant baseline
            return [float(bound)] * len(thresholds_t)
        if bound in cols:
            return threshold_df[bound].to_list()
        return None  # missing metric -> skip band

    for name, cfg in bands.items():
        ylo, yhi = thresholds(cfg["lo"]), thresholds(cfg["hi"])
        if ylo is None or yhi is None:
            continue
        # lower (invisible) → upper (filled to previous)
        fig.add_trace(
            go.Scatter(
                x=thresholds_t,
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
                x=thresholds_t,
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
            name=chart_config["line_legend_label"],
            x=ts.index,
            y=ts.values,
            mode="lines",
            line=dict(color="black", width=2),
            hovertemplate=chart_config["hovertemplate"],
        )
    )
    # dummy trace for legend
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color="#D6F5E8", width=7),
            name="Suitable",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color="rgba(255, 193, 7, 0.5)", width=7),
            name="Concerning",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color="rgba(220, 53, 69, 0.5)", width=7),
            name="Critical",
        )
    )
    fig.update_layout(
        title=dict(
            text=f"{region_sel} | {chart_config['chart_title']} <br><span style='font-weight:normal; font-size:0.8em;'>(Crop year {year_sel})</span>",
            x=0.5,
            xanchor="center",
        ),
        height=600,
        width=1000,
        margin=dict(l=60, r=40, t=90, b=60),
        yaxis=dict(title=""),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )
    fig.update_xaxes(
        range=x_range,
        dtick="M1",
        showgrid=True,
        showline=True,
        tickformat="%b %y",
    )
    fig.update_yaxes(range=y_range, showline=True, title=dict(font=dict(size=20)))

    if chart_config["y_title"]:
        fig.update_layout(
            annotations=[
                dict(
                    text=chart_config["y_title"],
                    xref="paper", yref="paper",
                    x=-0.05, y=1.01,
                    showarrow=False,
                    font=dict(size=20),
                    align="left"
                    ),
            ])

    annotation_y = y_range[1] - 1
    year_flipped = False
    prev_stage_month: int = 0
    for stage in crop_stages[crop_sel]:
        if prev_stage_month > stage["start_month"]:
            year_flipped = True
        prev_stage_month = stage["start_month"]
        stage_year = x_range[1].year if year_flipped else x_range[0].year
        stage_date = date(stage_year, stage["start_month"], stage["start_day"])
        if (
            x_range[0]
            <= stage_date
            <= x_range[1]
        ):
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
                yshift=-390,
            )
    # Add a year changing grid line
    jan1 = date(year_sel, 1, 1)
    fig.add_vline(x=jan1, line_width=2, line_color="#aeaeae")

    st.plotly_chart(fig, use_container_width=True)
