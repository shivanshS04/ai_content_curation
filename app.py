import streamlit as st
from components.search import search_component
from components.top_results import top_results_component

st.set_page_config(
    page_title="AI Agency",
    page_icon="📰",
    layout="centered",
    initial_sidebar_state="collapsed",
)

topic = search_component()
if topic:
    with st.spinner("Fetching news...",show_time=True):
        top_results_component(topic)

