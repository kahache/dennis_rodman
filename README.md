# 🐛 Rodman Historic Feats — v2

A tribute app for Dennis Rodman. Every feat shown is one where **The Worm ranks #1**.

---

## Project Structure

```
rodman-historic-feats/
├── backend/
│   ├── app.py                        # FastAPI app + static file serving
│   ├── feats.py                      # Feat catalog (5 feats, all Rodman #1)
│   ├── nba_client.py                 # nba_api live queries + mock fallback
│   ├── cache.py                      # In-memory TTL cache (10 min)
│   ├── requirements.txt
│   └── mocks/
│       ├── rebounding_titles.json
│       ├── season_rpg.json
│       ├── offensive_rebounds_season.json
│       ├── consecutive_titles.json
│       └── chaos_index.json
├── frontend/
│   ├── index.html
│   ├── ranking.html
│   ├── style.css
│   └── app.js
├── tests/
│   ├── __init__.py                   # sys.path bootstrap
│   ├── test_cache.py                 # 17 tests — cache set/get/TTL/clear/stats
│   ├── test_feats.py                 # 16 tests — catalog shape, contracts
│   ├── test_nba_client.py            # 22 tests — mocks, normalise, fallback, Rodman #1
│   └── test_api.py                   # 24 tests — endpoints, caching, rankings
├── pytest.ini
└── README.md
```

---

## Quick Start

```bash
# 1 — Install dependencies
cd backend && pip install -r requirements.txt

# 2 — Start the server (from inside backend/)
uvicorn app:app --port 8000 --reload

# 3 — Open the app
open http://localhost:8000
```

---

## Run Tests

```bash
# From the project root
pip install pytest pytest-cov
pytest

# With coverage report
pytest --cov=backend --cov-report=term-missing
```

---

## The 5 Feats (all Rodman #1)

| Feat | Rodman's Record | Data |
|------|----------------|------|
| Most Rebounding Titles (modern era) | 7 titles | Mock |
| Highest Single-Season RPG (post-1980) | 18.7 RPG in 1991–92 | nba_api → mock |
| Most Offensive Rebounds in a Season (post-1980) | 523 in 1991–92 | nba_api → mock |
| Most Consecutive Rebounding Titles | 7 straight (1991–98) | Mock |
| The Worm's Chaos Index | 312 chaos points | Mock |

> **Live vs Mock:** Feats marked `nba_api → mock` attempt a real query to stats.nba.com first. On failure (timeout, rate-limit, etc.) the app falls back silently to local JSON. A badge on the ranking page shows which source was used.
