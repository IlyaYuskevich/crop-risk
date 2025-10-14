from constants.locations import LOCATIONS
import streamlit as st

def add_region_select() -> tuple[str, dict[str, dict[str, float]]]:
    params = st.query_params
    raw_region = params.get("region")
    region_options = [l["label"] for l in LOCATIONS]
    
    default_region = raw_region if raw_region in region_options else region_options[0]
    
    def format_option(opt):
        if opt.startswith("====="):
            # stylize category label visually
            return f"{opt.replace("=====", '').strip().upper()}"
        return f" {opt}"  # adds indentation using Unicode space

    region_sel = str(st.sidebar.selectbox(
        "Region",
        region_options,
        format_func=format_option,
        index=region_options.index(default_region)
    ))
    if region_sel != raw_region:
        params["region"] = region_sel
    if region_sel.startswith("====="):
        st.write("Please pick a country, not a region header")
    locations_hashmap: dict[str, dict[str, float]] = {l["label"]: {k: l[k] for k in ("lat", "lon")} for l in LOCATIONS if not l["label"].startswith("=====")}
    return region_sel, locations_hashmap