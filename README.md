# TrendRadar AI – Personal MVP

A mobile-friendly personal trend discovery dashboard. Backend uses public RSS feeds:
- Google Trends RSS (region-based)
- Google News RSS
- Reddit India RSS

The score is a transparent heuristic indicator, NOT an official trend velocity or probability of going viral. Public feeds may be unavailable, delayed, or incomplete.

## Run locally
1. Install Python 3.10+
2. `pip install -r requirements.txt`
3. `uvicorn main:app --reload`
4. Open http://127.0.0.1:8000

## Optional AI scripts
Set `GEMINI_API_KEY` in your environment. On Render, add it under Environment. Keep the key private; never put it in frontend code.

## Deploy to Render
1. Upload this project to a GitHub repository.
2. In Render choose New > Web Service and connect the repository.
3. Render can use `render.yaml`, or set:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy and open the generated URL.

## MVP limitations / next phase
- This MVP does not scrape private social media data.
- YouTube trending is not included yet; YouTube Data API can be added with an API key.
- Category classification, deduplication across sources, trend history, scheduled reports and email/WhatsApp notifications are Phase 2.
