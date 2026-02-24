"""
app.py — Rodman Historic Feats API
FastAPI backend serving feat metadata and live/mock NBA rankings.

Run with:
    uvicorn app:app --port 8000 --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

import cache
import feats as feats_catalog
import nba_client

app = FastAPI(
    title="Rodman Historic Feats API",
    description="Backend for the Dennis Rodman tribute app — because The Worm deserves an API.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — allow all origins in development
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Serve frontend static files
# All files are flat in the same directory as app.py
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = _HERE

print(f"[startup] Script location   : {_HERE}")
print(f"[startup] index.html found  : {os.path.isfile(os.path.join(FRONTEND_DIR, 'index.html'))}")

@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/ranking", include_in_schema=False)
def serve_ranking():
    return FileResponse(os.path.join(FRONTEND_DIR, "ranking.html"))

@app.get("/style.css", include_in_schema=False)
def serve_css():
    return FileResponse(os.path.join(FRONTEND_DIR, "style.css"))

@app.get("/app.js", include_in_schema=False)
def serve_js():
    return FileResponse(os.path.join(FRONTEND_DIR, "app.js"))


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/api/feats", summary="List all historic feats")
def list_feats():
    return {
        "feats": feats_catalog.get_all_feats(),
        "total": len(feats_catalog.FEATS),
    }


@app.get("/api/feats/{feat_id}", summary="Get feat metadata")
def get_feat(feat_id: str):
    feat = feats_catalog.get_feat(feat_id)
    if not feat:
        raise HTTPException(status_code=404, detail=f"Feat '{feat_id}' not found.")
    return {k: v for k, v in feat.items() if k not in ("source_strategy", "mock_file")}


@app.get("/api/feats/{feat_id}/ranking", summary="Get ranking for a feat")
def get_ranking(feat_id: str, top_n: int = 10):
    feat = feats_catalog.get_feat(feat_id)
    if not feat:
        raise HTTPException(status_code=404, detail=f"Feat '{feat_id}' not found.")

    top_n = max(1, min(top_n, 25))

    cache_key = f"ranking:{feat_id}:{top_n}"
    cached = cache.get(cache_key)
    if cached:
        print(f"[cache] HIT for '{cache_key}'")
        return cached

    ranking, source = nba_client.fetch_ranking(feat, top_n=top_n)

    response = {
        "feat_id": feat_id,
        "title": feat["title"],
        "subtitle": feat["subtitle"],
        "unit": feat["unit"],
        "source": source,
        "ranking": ranking,
        "rodman_in_ranking": any(p["is_rodman"] for p in ranking),
    }

    cache.set(cache_key, response)
    return response


@app.get("/api/cache/stats", include_in_schema=False)
def cache_stats():
    return cache.stats()


@app.get("/api/health", summary="Health check")
def health():
    return {"status": "ok", "message": "The Worm is alive 🐛"}
