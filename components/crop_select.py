import streamlit as st

from constants.crops import CROP_SPECIES

def add_crop_select() -> str:
    params = st.query_params
    raw_crop = params.get("crop")
    
    crop_options: list[str] = CROP_SPECIES
    default_crop = raw_crop if raw_crop in crop_options else crop_options[0]

    crop_sel = st.sidebar.selectbox("Crop species", crop_options, index=crop_options.index(default_crop)).lower()
    if crop_sel != raw_crop:
        params["crop"] = crop_sel
    return crop_sel