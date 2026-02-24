"""
app.py — Rodman Historic Feats API
FastAPI backend. Frontend is in ../frontend relative to this file.

Run from project root:
    uvicorn backend.app:app --port 8000 --reload

Or from inside backend/:
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
    description="Because The Worm deserves an API.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Frontend path resolution
# backend/app.py lives one level below the project root, so frontend/ is ../frontend
# ---------------------------------------------------------------------------
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_BACKEND_DIR, ".."))
FRONTEND_DIR  = os.path.join(_PROJECT_ROOT, "frontend")

print(f"[startup] Backend dir  : {_BACKEND_DIR}")
print(f"[startup] Frontend dir : {FRONTEND_DIR}")
print(f"[startup] index.html   : {os.path.isfile(os.path.join(FRONTEND_DIR, 'index.html'))}")


@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/timeline", include_in_schema=False)
def serve_timeline():
    return FileResponse(os.path.join(FRONTEND_DIR, "timeline.html"))

@app.get("/career", include_in_schema=False)
def serve_career():
    return FileResponse(os.path.join(FRONTEND_DIR, "career.html"))

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
def get_feat_meta(feat_id: str):
    feat = feats_catalog.get_feat(feat_id)
    if feat is None:
        raise HTTPException(status_code=404, detail=f"Feat '{feat_id}' not found.")
    return {k: v for k, v in feat.items() if k not in ("source_strategy", "mock_file")}


@app.get("/api/feats/{feat_id}/ranking", summary="Get top-N ranking for a feat")
def get_ranking(feat_id: str, top_n: int = 10):
    feat = feats_catalog.get_feat(feat_id)
    if feat is None:
        raise HTTPException(status_code=404, detail=f"Feat '{feat_id}' not found.")

    top_n = max(1, min(top_n, 25))

    cache_key = f"ranking:{feat_id}:{top_n}"
    cached = cache.get(cache_key)
    if cached:
        print(f"[cache] HIT  {cache_key}")
        return cached

    ranking, source = nba_client.fetch_ranking(feat, top_n=top_n)

    response = {
        "feat_id":           feat_id,
        "title":             feat["title"],
        "subtitle":          feat["subtitle"],
        "unit":              feat["unit"],
        "source":            source,
        "ranking":           ranking,
        "rodman_in_ranking": any(p["is_rodman"] for p in ranking),
        "rodman_is_first":   bool(ranking and ranking[0]["is_rodman"]),
    }

    cache.set(cache_key, response)
    return response


@app.get("/api/health", summary="Health check")
def health():
    return {"status": "ok", "message": "The Worm is alive 🐛"}

@app.get("/api/cache/stats", include_in_schema=False)
def cache_stats_route():
    return cache.stats()
