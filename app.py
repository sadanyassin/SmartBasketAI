"""SmartBasket AI - נקודת כניסה. הרצה: streamlit run app.py"""
import streamlit as st

from ui import ai_tab, build_basket, components, home, results

st.set_page_config(page_title="SmartBasket AI", page_icon="🧺", layout="wide")
components.inject_css()

tab_home, tab_build, tab_results, tab_ai = st.tabs(
    ["דף ראשי", "בניית סל", "תוצאות וסימולציה", "הסבר AI"]
)

with tab_home:
    home.render()
with tab_build:
    basket, errors = build_basket.render()
with tab_results:
    results.render(basket, errors)
with tab_ai:
    ai_tab.render()
