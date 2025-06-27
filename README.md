# AI Web Scraper

A small Streamlit app that scrapes any web page (including content inside
`<iframe>`s) with Selenium, strips it down to clean text, and then uses an LLM to
extract exactly the information you describe in plain language.

## How it works

```
Streamlit UI (main.py)
      │  URL
      ▼
scrape.py ── Selenium/Chrome ──► loads the page, waits, also walks every iframe
      │                          and dumps its page_source
      ▼
extract_body_content / clean_body_content (BeautifulSoup)
      │  scripts & styles removed, collapsed to non-empty text lines
      ▼
split_dom_content  ──► ~6k-char chunks
      │
      ▼
parse.py ── LangChain + ChatOpenAI (OpenRouter) ──► per chunk: "extract only what
      │                                             matches this description"
      ▼
results joined and shown in the UI
```

The LLM call goes through any OpenAI-compatible endpoint. It defaults to
OpenRouter with the free `deepseek/deepseek-chat-v3-0324` model, but you can point
`OPENROUTER_BASE_URL` / `OPENROUTER_MODEL` at LM Studio, Ollama, etc.

## Requirements

- Python 3.10+
- Google Chrome installed (Selenium Manager fetches the matching driver
  automatically — no `chromedriver.exe` needed)
- An OpenRouter API key: https://openrouter.ai/keys

## Setup

```bash
git clone https://github.com/jjvelezo/scraperIA.git
cd scraperIA

python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env          # then edit .env and paste your API key
```

## Run

```bash
streamlit run main.py
```

1. Paste a URL and click **Scrape Website**.
2. Expand **View DOM Content** to check the cleaned text.
3. Describe what you want (e.g. "all product names and prices") and click
   **Parse Content**.

## Project layout

| File | Purpose |
|---|---|
| `main.py` | Streamlit UI and flow control |
| `scrape.py` | Selenium scraping, iframe walking, BeautifulSoup cleaning, chunking |
| `parse.py` | LLM prompt template and per-chunk extraction |
| `.env.example` | Template for the required environment variables |

## Notes

- Some sites block automated browsers or require login; results vary.
- `--disable-web-security` is passed to Chrome to reach cross-origin iframes. Only
  run this against sites you trust.
