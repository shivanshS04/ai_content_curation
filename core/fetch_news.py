from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import http.client , urllib.parse,json
load_dotenv()


# init
conn = http.client.HTTPSConnection('api.thenewsapi.com')

def fetch_top_results(topic: str) -> list[str]:
    if not topic:
        return []
    last_week = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    params = urllib.parse.urlencode({
        'api_token': os.getenv('NEWS_API_KEY'),
        'limit' : 3, # free tier only allows 3 results per request
        'search' : topic,
        'locale':'in,us,uk',
        'language':'en',
        'published_after': last_week
    })
    conn.request("GET", f"/v1/news/all?{params}")
    response = conn.getresponse()
    data = response.read()
    articles = json.loads(data).get("data", [])
    print(f"Fetched {len(articles)} articles for topic '{topic}'")
    return articles
