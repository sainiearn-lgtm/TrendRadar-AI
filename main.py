import os, re, asyncio
from datetime import datetime, timezone
from typing import Optional
import httpx
import feedparser
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

APP_NAME = "TrendRadar AI"
app = FastAPI(title=APP_NAME, version="0.1.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

GOOGLE_TRENDS_RSS = "https://trends.google.com/trending/rss?geo={geo}"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
REDDIT_RSS = "https://www.reddit.com/r/{subreddit}/hot.rss"

def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()

async def fetch_feed(url, limit=15):
    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True, headers={"User-Agent":"TrendRadarAI/0.1"}) as client:
            r = await client.get(url)
            r.raise_for_status()
        parsed = feedparser.parse(r.text)
        out = []
        for entry in parsed.entries[:limit]:
            title = clean(entry.get("title", ""))
            link = entry.get("link", "")
            summary = clean(entry.get("summary", ""))[:500]
            if title:
                out.append({
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "published": entry.get("published", ""),
                    "source": clean(entry.get("source", {}).get("title", "")) or "Public RSS"
                })
        return out
    except Exception as e:
        return []

def score_item(item, source):
    # Transparent heuristic score, not a measured virality prediction.
    title = item["title"].lower()
    score = 55
    if source == "Google Trends": score += 28
    elif source == "Google News": score += 12
    elif source == "Reddit": score += 10
    if any(k in title for k in ["breaking", "launch", "launches", "live", "latest", "new", "update"]):
        score += 7
    return min(score, 98)

@app.get("/")
async def home():
    return FileResponse("static/index.html")

@app.get("/api/health")
async def health():
    return {"ok": True, "app": APP_NAME, "time": datetime.now(timezone.utc).isoformat()}

@app.get("/api/trends")
async def trends(region: str = Query("IN", pattern="^(IN|US|GB|CA|AU|DE)$"),
                 category: str = "all"):
    jobs = [
        fetch_feed(GOOGLE_TRENDS_RSS.format(geo=region), 20),
        fetch_feed(GOOGLE_NEWS_RSS.format(query="India trending news OR technology OR science OR entertainment"), 20),
        fetch_feed(REDDIT_RSS.format(subreddit=" popular"), 0)
    ]
    # Correct Reddit endpoints are queried separately to avoid relying on a single subreddit.
    jobs[2] = fetch_feed(REDDIT_RSS.format(subreddit="india"), 10)
    results = await asyncio.gather(*jobs)
    merged, seen = [], set()
    for source, entries in zip(["Google Trends", "Google News", "Reddit"], results):
        for entry in entries:
            key = entry["title"].lower()
            if key in seen: continue
            seen.add(key)
            entry["source"] = source
            entry["score"] = score_item(entry, source)
            entry["score_note"] = "Heuristic indicator based on source and headline signals; not a measured viral probability."
            entry["category"] = "General"
            merged.append(entry)
    merged.sort(key=lambda x: x["score"], reverse=True)
    return {
        "region": region,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(merged),
        "notice": "Trend availability depends on public RSS feeds. Scores are indicative heuristics, not official platform metrics.",
        "trends": merged[:40]
    }

class ScriptRequest(BaseModel):
    topic: str
    language: str = "Hinglish"
    format: str = "Shorts (60 seconds)"

@app.post("/api/script")
async def make_script(req: ScriptRequest):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return {
            "configured": False,
            "message": "AI script generation ke liye Render Environment mein GEMINI_API_KEY add karein.",
            "prompt": f"Create a {req.format} video script in {req.language} about: {req.topic}"
        }
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    prompt = f"""You are a careful YouTube research and script assistant. Write a {req.format} script in {req.language} about: {req.topic}.
Use a strong but honest opening hook, simple spoken language, clear structure, and a closing CTA.
Do not invent facts, statistics, dates, quotes, or claims. Mark anything that needs fact-checking as [VERIFY].
Return: Hook, Script, Suggested title, Thumbnail text, Description, Hashtags."""
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                json={"contents":[{"parts":[{"text":prompt}]}]}
            )
        data = r.json()
        if r.status_code >= 400:
            return {"configured": True, "error": data.get("error", {}).get("message", "Gemini API error")}
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return {"configured": True, "script": text}
    except Exception as e:
        return {"configured": True, "error": str(e)}
