"""
nba_client.py — All NBA data fetching lives here.

Strategy per feat:
  - "live"  → attempt nba_api query; fall back to mock on any error
  - "mock"  → skip live attempt entirely

Normalised ranking item shape:
  {
    "rank":       int,
    "player":     str,
    "team":       str | None,
    "value":      int | float,
    "is_rodman":  bool,
  }
"""

import json
import os
import time
from typing import Any

RODMAN_NAMES = {"dennis rodman", "rodman"}
_HERE_NBC = os.path.dirname(os.path.abspath(__file__))
_MOCKS_SUB = os.path.join(_HERE_NBC, "mocks")
MOCKS_DIR = _MOCKS_SUB if os.path.isdir(_MOCKS_SUB) else _HERE_NBC


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_mock(filename: str) -> dict:
    path = os.path.join(MOCKS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _is_rodman(name: str) -> bool:
    return name.lower() in RODMAN_NAMES or "rodman" in name.lower()


def _add_ranks(players: list[dict]) -> list[dict]:
    """Add rank field based on list position (1-indexed)."""
    for i, p in enumerate(players):
        p["rank"] = i + 1
    return players


# ---------------------------------------------------------------------------
# Live fetchers (one per feat that uses "live" strategy)
# ---------------------------------------------------------------------------

def _fetch_rebounds_live(top_n: int = 10) -> list[dict]:
    """
    Fetch all-time career rebounds leaders from stats.nba.com.
    Uses AllTimeLeadersGrids endpoint.
    """
    from nba_api.stats.endpoints import alltimeleadersgrids  # lazy import

    response = alltimeleadersgrids.AllTimeLeadersGrids(
        league_id="00",
        per_mode_simple="Totals",
        season_type="Regular Season",
        topx=top_n,
    )
    df = response.get_data_frames()[6]  # index 6 = REB leaders grid

    players = []
    for _, row in df.iterrows():
        name = str(row.get("PLAYER_NAME") or row.get("PLAYER") or "Unknown")
        value = int(row.get("REB") or row.get("REBOUNDS") or 0)
        players.append({
            "player": name,
            "team": None,
            "value": value,
            "is_rodman": _is_rodman(name),
        })

    # Sort descending by value, take top_n
    players.sort(key=lambda x: x["value"], reverse=True)
    return _add_ranks(players[:top_n])


def _fetch_steals_live(top_n: int = 10) -> list[dict]:
    """
    Fetch all-time career steals leaders from stats.nba.com.
    Uses AllTimeLeadersGrids endpoint.
    """
    from nba_api.stats.endpoints import alltimeleadersgrids  # lazy import

    response = alltimeleadersgrids.AllTimeLeadersGrids(
        league_id="00",
        per_mode_simple="Totals",
        season_type="Regular Season",
        topx=top_n,
    )
    df = response.get_data_frames()[8]  # index 8 = STL leaders grid

    players = []
    for _, row in df.iterrows():
        name = str(row.get("PLAYER_NAME") or row.get("PLAYER") or "Unknown")
        value = int(row.get("STL") or row.get("STEALS") or 0)
        players.append({
            "player": name,
            "team": None,
            "value": value,
            "is_rodman": _is_rodman(name),
        })

    players.sort(key=lambda x: x["value"], reverse=True)
    return _add_ranks(players[:top_n])


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------

LIVE_FETCHERS = {
    "rebounds": _fetch_rebounds_live,
    "steals": _fetch_steals_live,
}


def fetch_ranking(feat: dict, top_n: int = 10) -> tuple[list[dict], str]:
    """
    Fetch ranking for a feat.
    Returns (ranking_list, source) where source is "live" or "mock".

    Never raises — always falls back to mock on error.
    """
    feat_id = feat["id"]
    strategy = feat["source_strategy"]
    mock_file = feat["mock_file"]

    if strategy == "live" and feat_id in LIVE_FETCHERS:
        try:
            start = time.time()
            ranking = LIVE_FETCHERS[feat_id](top_n=top_n)
            elapsed = round(time.time() - start, 2)
            print(f"[nba_client] Live fetch OK for '{feat_id}' in {elapsed}s")
            return ranking, "live"
        except Exception as exc:
            print(f"[nba_client] Live fetch FAILED for '{feat_id}': {exc}. Using mock.")

    # Fallback: load mock
    mock_data = _load_mock(mock_file)
    ranking = mock_data.get("ranking", [])[:top_n]
    _add_ranks(ranking)
    return ranking, "mock"
