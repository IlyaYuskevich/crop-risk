import streamlit as st

from constants.locations import LOCATIONS


def add_region_select() -> tuple[str, dict[str, dict[str, float]]]:
    params = st.query_params
    raw_region = params.get("region")
    region_options = [loc["label"] for loc in LOCATIONS]

    default_region = raw_region if raw_region in region_options else region_options[1]

    def format_option(opt):
        if opt.startswith("====="):
            # stylize category label visually
            return f"{opt.replace('=====', '').strip().upper()}"
        return f" {opt}"  # adds indentation using Unicode space

    region_sel = str(
        st.sidebar.selectbox(
            "Region",
            region_options,
            format_func=format_option,
            index=region_options.index(default_region),
        )
    )
    if region_sel != raw_region:
        params["region"] = region_sel
    if region_sel.startswith("====="):
        st.write("Please pick a country, not a region header")
    locations_hashmap: dict[str, dict[str, float]] = {
        loc["label"]: {k: loc[k] for k in ("lat", "lon")}
        for loc in LOCATIONS
        if not loc["label"].startswith("=====")
    }
    return region_sel, locations_hashmap
