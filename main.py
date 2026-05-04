from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import time
import os
import google.generativeai as genai

app = FastAPI(title="ResearchDaily API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_api_key = os.getenv("GEMINI_API")
ss_api_key = os.getenv("SEMANTIC_SCHOLAR_API")

if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')


class SearchRequest(BaseModel):
    query: str
    limit: int = 3
    tone: str = "professional"  # professional | conversational | bold | creative


TONE_MAP = {
    "professional": {
        "instruction": "Use a formal academic tone with precise, structured language.",
        "temperature": 0.3,
        "top_k": 20,
        "top_p": 0.7,
    },
    "conversational": {
        "instruction": "Explain clearly in a friendly way.",
        "temperature": 0.6,
        "top_k": 40,
        "top_p": 0.8,
    },
    "bold": {
        "instruction": "Be assertive and highlight key insights.",
        "temperature": 0.9,
        "top_k": 50,
        "top_p": 0.9,
    },
    "creative": {
        "instruction": "Use engaging and imaginative perspectives.",
        "temperature": 1.0,
        "top_k": 80,
        "top_p": 0.95,
    },
}


def fetch_papers(query: str, limit: int, retries: int = 3, delay: int = 5):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,abstract",
    }
    headers = {"x-api-key": ss_api_key} if ss_api_key else {}

    for attempt in range(retries):
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            time.sleep(delay * (attempt + 1))
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Semantic Scholar error: {response.status_code}")

    raise HTTPException(status_code=429, detail="Rate limited by Semantic Scholar. Please try again later.")


def generate_summary(title: str, abstract: str, tone: str) -> str:
    if not abstract:
        return "No abstract available."

    if not gemini_api_key:
        return "Gemini API key not configured."

    tone_config = TONE_MAP.get(tone, TONE_MAP["professional"])

    prompt = f"""You are an AI-powered research assistant.

Summarize this research paper in 150–200 words.

Title: {title}
Abstract: {abstract}

Tone: {tone_config['instruction']}"""

    try:
        time.sleep(1)
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": tone_config["temperature"],
                "top_k": tone_config["top_k"],
                "top_p": tone_config["top_p"],
                "max_output_tokens": 600,
            },
        )
        return response.text
    except Exception as e:
        return f"Error generating summary: {e}"


@app.get("/health")
def health():
    return {
        "status": "ok",
        "gemini_configured": bool(gemini_api_key),
        "semantic_scholar_configured": bool(ss_api_key),
    }


@app.post("/search")
def search_papers(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if req.tone not in TONE_MAP:
        raise HTTPException(status_code=400, detail=f"Invalid tone. Choose from: {list(TONE_MAP.keys())}")

    # Fetch extra papers to account for those without abstracts
    raw_data = fetch_papers(req.query, req.limit + 5)
    all_papers = raw_data.get("data", [])

    # Filter to papers with abstracts and cap to requested limit
    papers_with_abstracts = [p for p in all_papers if p.get("abstract")][:req.limit]

    if not papers_with_abstracts:
        raise HTTPException(status_code=404, detail="No papers with abstracts found for this query.")

    results = []
    for paper in papers_with_abstracts:
        title = paper.get("title", "Untitled")
        authors = ", ".join(
            [a.get("name") for a in paper.get("authors", []) if a.get("name")]
        )
        year = paper.get("year")
        abstract = paper.get("abstract", "")
        summary = generate_summary(title, abstract, req.tone)

        results.append({
            "title": title,
            "authors": authors,
            "year": year,
            "abstract": abstract,
            "summary": summary,
        })

    return {"papers": results, "total": len(results)}
