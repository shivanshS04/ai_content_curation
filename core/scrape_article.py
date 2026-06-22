import requests
from bs4 import BeautifulSoup

def scrape_article(url : str) -> str | None:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        all_text = soup.get_text(separator="\n", strip=True)

        return all_text

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None