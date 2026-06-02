import streamlit as st

st.title("Content Generation", text_alignment="center")
article_url = st.session_state.get('selected_article_url')
