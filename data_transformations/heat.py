import polars as pl

def calc_heat_wave_alerts(df: pl.DataFrame) -> dict[str, list[str]]:
    # Quick no-op path
    if df.is_empty():
        return {"warning": [], "alert": []}

    required = {"label", "temp_max_3d"}
    missing = required.difference(set(df.columns))
    if missing:
        raise ValueError(f"calc_heat_wave_alerts: missing required columns: {sorted(missing)}")

    # Aggregate per stage to know whether each threshold was ever crossed within the stage
    per_stage = (
        df
        .group_by("label")
        .agg([
            (pl.col("temp_max_3d") > pl.col("warn_temp")).any().alias("exceeds_warning"),
            (pl.col("temp_max_3d") > pl.col("alert_temp")).any().alias("exceeds_alert"),
        ])
    )

    # Extract unique labels for each category
    warning_labels = (
        per_stage
        .filter(pl.col("exceeds_warning"))
        .filter(~pl.col("exceeds_alert"))
        .get_column("label")
        .to_list()
    )
    alert_labels = (
        per_stage
        .filter(pl.col("exceeds_alert"))
        .get_column("label")
        .to_list()
    )

    return {"warning": warning_labels, "alert": alert_labels}