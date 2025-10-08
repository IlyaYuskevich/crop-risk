import streamlit as st

# Hide the "App" menu title in the sidebar
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"]::before {
            content: "";
        }
        [data-testid="stSidebarNav"] > div:first-child {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)