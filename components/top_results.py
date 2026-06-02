import streamlit as st
from core.fetch_news import fetch_top_results
from components.article import article_component
def top_results_component(topic :str):
    news_container = st.container()
    if topic:
        articles = fetch_top_results(topic)

        if len(articles) ==0 :
            news_container.error(f"No news found for '{topic}'.")
            return
        news_container.header(f"Top news on '{topic}':")
        for article in articles:
            article_component(article)
    else:
        st.error("Failed to generate content.")