import streamlit as st

def search_component():

    search_container = st.container(
        horizontal_alignment="center",
        vertical_alignment="center",
        border=True,
    )
    search_container.title("AI Agency",text_alignment="center")
    topic = search_container.text_input("",placeholder="Enter your topic here",icon="🔍",type="default")

    return topic