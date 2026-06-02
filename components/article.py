import streamlit as st

def handleButtonClick(url):
    st.session_state['selected_article_url'] = url
    st.switch_page("pages/generate_content.py")

def article_component(article):
    article_container = st.container(
        horizontal_alignment="center",
        vertical_alignment="center",
        border=True,
    )
    article_container.image(article['image_url'], width="stretch")
    article_container.subheader(article['title'])
    article_container.caption(article['description'])
    if article_container.button("Select topic",width="stretch",use_container_width=True,key=article['uuid']):
        handleButtonClick(article['url'])