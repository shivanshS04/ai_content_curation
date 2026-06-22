# AI Content Curation 📰

> A multi-platform AI content pipeline that transforms trending news into platform-optimized social media posts and blog content — automatically.

---

## ✨ What It Does

**AI Content Curation** is an end-to-end content automation system built with Streamlit. You search for a topic, pick a news article, choose your target platforms, and the AI does the rest — generating tailored content for each channel in one shot.

```
Topic Search → News Discovery → Article Scraping → Platform Selection → AI Content Generation → Review & Export
```

---

## 🚀 Key Features

### 📡 Real-Time News Discovery
- Fetches the **top 3 most recent articles** on any topic from the last 7 days
- Powered by [The News API](https://www.thenewsapi.com/), filtered for English content across IN, US, and UK locales
- Displays article thumbnails, headlines, and descriptions in a clean card layout

### 🤖 Multi-Platform AI Content Generation
Generate platform-optimized content for **5 channels simultaneously** in a single LLM call:

| Platform | Optimized For |
|---|---|
| 💼 **LinkedIn** | Thought leadership, professional reach, narrative-driven posts |
| 📸 **Instagram** | Scroll-stopping captions, hashtag strategy, engagement hooks |
| 🐦 **Twitter / X** | Punchy single tweets or full threads (auto-decided by the AI) |
| 📘 **Facebook** | Community-oriented storytelling, comment-driving engagement prompts |
| ✍️ **Blog Post** | SEO-optimized long-form articles with H1/H2 structure, meta descriptions, and keyword strategy |

Each platform has its own **expert-level system prompt** with specific tone, structure, length, and formatting rules — the AI respects all of them simultaneously via dynamic structured output schemas.

### 🖼️ AI Image Generation
- On-demand **image generation per platform card** using a Stable Diffusion backend
- A secondary LLM call optimizes the image prompt to the 77-token CLIP limit for SD 1.x
- **Download** generated images as PNG or **regenerate** with one click
- 📓 Backend notebook: [Image Generation Backend (Google Colab / .ipynb)](https://drive.google.com/file/d/1siL0xALH6cNegY-W3lzQUDHHcuw9j4JA/view?usp=sharing)

### 📋 One-Click Copy
- Every generated content card has a floating **Copy** button — click to instantly copy the text to clipboard, no manual selection needed

### 🗺️ Visual Pipeline Progress
- A **step-by-step sidebar timeline** tracks your position in the workflow:
  1. Fetching article content
  2. Select Target Platforms
  3. Generating content
  4. Review & Export

---

## 🏗️ Architecture

```
ai_agency/
│
├── app.py                          # Entry point — topic search & news discovery
│
├── components/
│   ├── search.py                   # Search bar UI component
│   ├── article.py                  # News article card component
│   └── top_results.py              # News results grid component
│
├── core/
│   ├── fetch_news.py               # The News API integration
│   ├── scrape_article.py           # Web scraper for article full-text
│   └── generate_image.py           # Stable Diffusion image backend client
│
├── llm_generators/
│   ├── generator.py                # Core LLM orchestrator (multi-platform, single call)
│   ├── prompts.py                  # Expert system prompts per platform
│   └── img_gen_prompt.py           # SD 1.x image prompt optimizer
│
└── pages/
    └── generate_content.py         # Full content pipeline UI (Steps 0–3)
```

### LLM Architecture Highlights

- **Single LLM call** for all platforms — prompts are merged into one combined system message, and a **dynamically generated Pydantic schema** captures all outputs at once, minimizing latency and API costs.
- **Lazy-loaded LLM clients** — Gemini and Ollama clients are instantiated only on first use, not at import time.
- **Dual LLM support** — toggle between Google Gemini (`gemini-2.0-flash-lite`) and local Ollama (`gemma3:1b`) by commenting/uncommenting a single line in `generator.py`.
- **Structured output** via LangChain's `.with_structured_output()` — guarantees type-safe, parseable JSON from the LLM.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **UI Framework** | [Streamlit](https://streamlit.io/) |
| **LLM Orchestration** | [LangChain](https://www.langchain.com/) |
| **Cloud LLM** | Google Gemini (`gemini-2.0-flash-lite`) via `langchain-google-genai` |
| **Local LLM** | Ollama (`gemma3:1b`) via `langchain-ollama` |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) |
| **News API** | [The News API](https://www.thenewsapi.com/) |
| **Image Generation** | Stable Diffusion 1.x (custom backend, accessed via REST) |
| **Image Processing** | Pillow (PIL) |
| **Config** | python-dotenv |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally (for local LLM mode)
- A Stable Diffusion backend server running and accessible (for image generation)

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd ai_agency
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
NEWS_API_KEY=your_thenewsapi_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here
BACKEND_URL=http://your-stable-diffusion-backend-url
```

| Variable | Description |
|---|---|
| `NEWS_API_KEY` | API key from [thenewsapi.com](https://www.thenewsapi.com/) (free tier available) |
| `GOOGLE_API_KEY` | Google AI Studio API key for Gemini access |
| `BACKEND_URL` | URL of your Stable Diffusion image generation backend |

### 5. Pull the Ollama model (for local LLM mode)
```bash
ollama pull gemma3:1b
```

### 6. Run the app
```bash
streamlit run app.py
```

---

## 🔄 Usage Walkthrough

1. **Search** — Enter any topic (e.g., *"AI regulation"*, *"climate tech"*) in the search box on the home screen.
2. **Discover** — Browse the top 3 recent news articles returned for your topic.
3. **Select** — Click **"Select topic"** on the article you want to base your content on.
4. **Choose platforms** — Pick any combination of LinkedIn, Instagram, Twitter, Facebook, and Blog.
5. **Generate** — The AI scrapes the full article and generates optimized content for every selected platform simultaneously.
6. **Review & Export** — Copy content to clipboard, generate platform-specific visuals, download images, or regenerate any image.

---

## 🔧 Configuration Notes

### Switching LLM backends

In [`llm_generators/generator.py`](./llm_generators/generator.py), toggle between cloud and local:

```python
# Cloud (Gemini) — requires GOOGLE_API_KEY in .env
llm = get_gemini()

# Local (Ollama) — requires Ollama running with gemma3:1b pulled
llm = get_ollama()
```

### News API limits

The free tier of The News API returns a **maximum of 3 articles per request**. Upgrade to a paid plan to increase this limit.

---

## 📁 Key Files Reference

| File | Purpose |
|---|---|
| [`app.py`](./app.py) | Main entry point and home page |
| [`requirements.txt`](./requirements.txt) | All Python dependencies with pinned versions |
| [`llm_generators/generator.py`](./llm_generators/generator.py) | Multi-platform LLM orchestration logic |
| [`llm_generators/prompts.py`](./llm_generators/prompts.py) | Platform-specific expert system prompts |
| [`pages/generate_content.py`](./pages/generate_content.py) | Full 4-step content generation pipeline UI |
| [`core/fetch_news.py`](./core/fetch_news.py) | News API integration |
| [`core/scrape_article.py`](./core/scrape_article.py) | Article full-text scraper |
| [`core/generate_image.py`](./core/generate_image.py) | Image generation backend client |
| [Image Gen Backend Notebook ↗](https://drive.google.com/file/d/1siL0xALH6cNegY-W3lzQUDHHcuw9j4JA/view?usp=sharing) | Stable Diffusion backend `.ipynb` (Google Drive) |

---

## 📄 License

This project is open source. Feel free to fork, extend, and build upon it.
