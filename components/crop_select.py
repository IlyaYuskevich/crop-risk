import streamlit as st

from app_types.types import CropSpecies
from constants.crops import CROP_SPECIES


def add_crop_select() -> CropSpecies:
    params = st.query_params
    raw_crop = (
        st.session_state.get("prev_crop")
        if st.session_state.get("prev_crop")
        else params.get("crop")
    )

    crop_options = CROP_SPECIES
    default_crop = raw_crop if raw_crop in crop_options else crop_options[0]

    crop_sel = st.sidebar.selectbox(
        "Crop species", crop_options, index=crop_options.index(default_crop), key="crop"
    )
    params["crop"] = st.session_state.get("crop")
    st.session_state["prev_crop"] = crop_sel
    return crop_sel
