# 🐛 Rodman Historic Feats

A tribute app for Dennis Rodman — browse all-time NBA rankings and find out where **The Worm** stands in basketball history.

Built as an AI-assisted full-stack development demo using **FastAPI + nba_api + vanilla HTML/CSS/JS**.

---

## Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Backend  | Python 3.9+, FastAPI, Uvicorn                   |
| NBA Data | `nba_api` (live) with JSON mock fallback        |
| Frontend | HTML + CSS + Vanilla JS (no build step needed)  |

---

## Project Structure

```
rodman-historic-feats/
├── backend/
│   ├── app.py            # FastAPI app, routes, static file serving
│   ├── feats.py          # Feat catalog (metadata + query strategy)
│   ├── nba_client.py     # nba_api live queries + mock fallback logic
│   ├── cache.py          # In-memory TTL cache
│   ├── requirements.txt
│   └── mocks/            # Fallback JSON data (one file per feat)
├── frontend/
│   ├── index.html        # Feat selection page
│   ├── ranking.html      # Ranking results page
│   ├── style.css
│   └── app.js
├── test_mock_fallback.py # pytest suite
└── README.md
```

---

## Quick Start

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the backend

```bash
uvicorn app:app --port 8000 --reload
```

### 3. Open the app

Visit **http://localhost:8000** in your browser.

The backend serves the frontend at the root URL — no separate web server needed.

---

## Available Feats (v1)

| ID                | Title                          | Data Source      |
|-------------------|-------------------------------|------------------|
| `rebounds`        | All-Time Rebounds Leaders      | nba_api → mock   |
| `defensive_teams` | All-Defensive Team Selections  | Mock             |
| `championships`   | Most Championship Rings        | Mock             |
| `steals`          | All-Time Steals Leaders        | nba_api → mock   |
| `intensity`       | The Chaos Leaderboard          | Mock (flavour)   |

> **Live vs Mock:** `nba_api` queries stats.nba.com in real time. If the request fails (timeout, rate-limit, API change), the app automatically falls back to the local mock JSON. A small badge on the ranking page tells you which source was used.

---

## API Endpoints

Once running, interactive docs are available at **http://localhost:8000/docs**.

| Method | Path                             | Description                     |
|--------|----------------------------------|---------------------------------|
| GET    | `/api/feats`                     | List all feats                  |
| GET    | `/api/feats/{feat_id}`           | Get a single feat's metadata    |
| GET    | `/api/feats/{feat_id}/ranking`   | Get the top-10 ranking          |
| GET    | `/api/health`                    | Health check                    |

---

## Running Tests

From the project root:

```bash
pip install pytest httpx
pytest test_mock_fallback.py -v
```

Tests cover:
- All mock JSON files are valid and well-shaped
- `nba_client` falls back to mock when the live fetcher raises
- Mock-strategy feats never attempt a live fetch
- `rank` fields are correctly injected
- Cache set/get/expiry/clear behaviour
- FastAPI endpoint smoke tests (200s, 404s, correct shapes)

---

## Notes

- **stats.nba.com can be slow or flaky.** The backend has a built-in fallback — the app always works even if the NBA API is down.
- **No database.** Results are cached in memory for 10 minutes, then re-fetched.
- **No authentication required** for v1 local development.
- Photos in the header are placeholder emojis for v1. Replace `rodman-photo-placeholder` divs in `index.html` with `<img>` tags pointing to public domain images from Wikimedia Commons if desired.
# dennis_rodman
