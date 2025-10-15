import pandas as pd
import polars as pl

from app_types.types import CropStage

BASE_KEYS = {"label", "start_month", "start_day", "color"}


def stage_bands_daily(time_coord: pd.Index, markers: list[CropStage]) -> pl.DataFrame:
    """
    Build a daily (1D) long-form frame of thresholds over [t0, t1] from stage markers.
    - Generic: any threshold keys (e.g., dry/wet or temps) are detected automatically.
    - No year offsets; uses actual calendar years from time_coord.
    - No duplicate boundary points: one row per day per metric.
    """
    # Time window (normalize to dates)
    t0 = pd.Timestamp(pd.to_datetime(time_coord.values[0])).normalize()
    t1 = pd.Timestamp(pd.to_datetime(time_coord.values[-1])).normalize()

    # Build stage starts for years spanning the window (pad by one year before to cover pre-t0 stage)
    years = range(
        t0.year - 1, t1.year + 1 + 1
    )  # include t1.year+1 for the final boundary
    starts = [
        (pd.Timestamp(y, m["start_month"], m["start_day"]), m)
        for y in years
        for m in markers
    ]
    starts.sort(key=lambda x: x[0])

    # Keep only intervals that might intersect [t0, t1]
    # Build (start, end, marker) triples
    intervals = []
    for i, (s, m) in enumerate(starts[:-1]):
        e = starts[i + 1][0]
        if e <= t0 or s > t1:  # no overlap
            continue
        s_clip = max(s.normalize(), t0)
        e_clip = min(e.normalize(), t1 + pd.Timedelta(days=1))  # exclusive end
        if s_clip < e_clip:
            intervals.append((s_clip, e_clip, m))

    # Emit one row per DAY per metric (no duplicated boundary timestamps)
    rows = []
    for s, e, m in intervals:
        days = pd.date_range(s, e - pd.Timedelta(days=1), freq="D")
        base = {"stage": m["label"]}
        if "color" in m:
            base["color"] = m["color"]
        for d in days:
            row = {"time": d.to_pydatetime(), **base}
            for k in markers[0]["thresholds"].keys():
                row[k] = m["thresholds"].get(k)
            rows.append(row)

    if not rows:
        return pl.DataFrame({"time": [], "stage": [], "value": []})
    
    return pl.DataFrame(rows)
