from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Job Search Assistance",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

HTML_PATH = Path(__file__).parent / "design.html"
html = HTML_PATH.read_text(encoding="utf-8")

# Preserve the original standalone premium dark interface, including its
# responsive navigation, animated 3D orb/rings, cards, and styling.
components.html(html, height=1900, scrolling=True)
