"""
nba_client.py — All NBA data fetching lives here.

Strategy per feat:
  "live"  → attempt nba_api query with timeout; fall back to mock on any error
  "mock"  → skip live attempt, load mock directly

Normalised ranking item shape:
  {
    "rank":      int,
    "player":    str,
    "team":      str | None,
    "value":     int | float,
    "is_rodman": bool,
  }
"""

import json
import os
import time
from typing import Any

RODMAN_NAMES = {"dennis rodman", "rodman"}

_HERE = os.path.dirname(os.path.abspath(__file__))
_MOCKS_SUB = os.path.join(_HERE, "mocks")
MOCKS_DIR = _MOCKS_SUB if os.path.isdir(_MOCKS_SUB) else _HERE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_mock(filename: str) -> dict:
    path = os.path.join(MOCKS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _is_rodman(name: str) -> bool:
    return "rodman" in name.lower()


def _add_ranks(players: list[dict]) -> list[dict]:
    """Assign 1-indexed rank field based on current list order."""
    for i, p in enumerate(players):
        p["rank"] = i + 1
    return players


def _normalise(player: dict) -> dict:
    """Ensure every ranking entry has the required public fields."""
    return {
        "rank":      player.get("rank", 0),
        "player":    player.get("player", "Unknown"),
        "team":      player.get("team"),
        "value":     player.get("value", 0),
        "is_rodman": bool(player.get("is_rodman", False)),
        # Pass through optional display fields when present
        **{k: player[k] for k in ("season", "seasons") if k in player},
    }


# ---------------------------------------------------------------------------
# Live fetchers — one per feat that uses source_strategy = "live"
# ---------------------------------------------------------------------------

def _fetch_season_rpg_live(top_n: int = 10) -> list[dict]:
    """
    Fetch top single-season RPG averages (post-1980) using PlayerSeasonStats.
    We iterate multiple seasons and keep the overall leaders.
    NOTE: This is an expensive call — cache is essential.
    """
    from nba_api.stats.endpoints import leagueleaders

    all_rows = []
    # Sample key seasons covering Rodman's peak and competitors
    seasons = [
        "1991-92", "1992-93", "1993-94", "1994-95",
        "1995-96", "1996-97", "1997-98",
        "1981-82", "1982-83", "1986-87", "1989-90",
        "2003-04", "2009-10",
    ]

    for season in seasons:
        try:
            resp = leagueleaders.LeagueLeaders(
                league_id="00",
                season=season,
                season_type_all_star="Regular Season",
                per_mode48="PerGame",
                scope="S",
                stat_category_abbreviation="REB",
            )
            df = resp.get_data_frames()[0]
            for _, row in df.head(5).iterrows():
                name = str(row.get("PLAYER", "Unknown"))
                reb = float(row.get("REB", 0))
                all_rows.append({
                    "player":    name,
                    "team":      str(row.get("TEAM", "")),
                    "value":     round(reb, 1),
                    "is_rodman": _is_rodman(name),
                    "season":    season,
                })
        except Exception:
            continue

    if not all_rows:
        raise RuntimeError("No live data retrieved for season_rpg")

    # Sort by value descending, deduplicate keeping best season per player
    all_rows.sort(key=lambda x: x["value"], reverse=True)
    seen: set[str] = set()
    unique: list[dict] = []
    for row in all_rows:
        if row["player"] not in seen:
            seen.add(row["player"])
            unique.append(row)
        if len(unique) >= top_n:
            break

    return _add_ranks(unique)


def _fetch_offensive_rebounds_season_live(top_n: int = 10) -> list[dict]:
    """
    Fetch top single-season offensive rebound totals (post-1980).
    """
    from nba_api.stats.endpoints import leagueleaders

    all_rows = []
    seasons = [
        "1991-92", "1992-93", "1993-94", "1994-95",
        "1995-96", "1981-82", "1982-83", "1986-87",
        "1989-90", "2007-08",
    ]

    for season in seasons:
        try:
            resp = leagueleaders.LeagueLeaders(
                league_id="00",
                season=season,
                season_type_all_star="Regular Season",
                per_mode48="Totals",
                scope="S",
                stat_category_abbreviation="OREB",
            )
            df = resp.get_data_frames()[0]
            for _, row in df.head(3).iterrows():
                name = str(row.get("PLAYER", "Unknown"))
                oreb = int(row.get("OREB", 0))
                all_rows.append({
                    "player":    name,
                    "team":      str(row.get("TEAM", "")),
                    "value":     oreb,
                    "is_rodman": _is_rodman(name),
                    "season":    season,
                })
        except Exception:
            continue

    if not all_rows:
        raise RuntimeError("No live data retrieved for offensive_rebounds_season")

    all_rows.sort(key=lambda x: x["value"], reverse=True)
    seen: set[str] = set()
    unique: list[dict] = []
    for row in all_rows:
        if row["player"] not in seen:
            seen.add(row["player"])
            unique.append(row)
        if len(unique) >= top_n:
            break

    return _add_ranks(unique)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

LIVE_FETCHERS: dict[str, Any] = {
    "season_rpg":                  _fetch_season_rpg_live,
    "offensive_rebounds_season":   _fetch_offensive_rebounds_season_live,
}


def fetch_ranking(feat: dict, top_n: int = 10) -> tuple[list[dict], str]:
    """
    Fetch ranking for a feat. Returns (ranking, source).
    source is "live" or "mock". Never raises — always falls back to mock.
    """
    feat_id  = feat["id"]
    strategy = feat["source_strategy"]
    mock_file = feat["mock_file"]

    if strategy == "live" and feat_id in LIVE_FETCHERS:
        try:
            start   = time.time()
            ranking = LIVE_FETCHERS[feat_id](top_n=top_n)
            elapsed = round(time.time() - start, 2)
            print(f"[nba_client] Live OK  '{feat_id}' in {elapsed}s")
            return [_normalise(p) for p in ranking], "live"
        except Exception as exc:
            print(f"[nba_client] Live FAIL '{feat_id}': {exc} — using mock")

    # Load mock fallback
    raw = _load_mock(mock_file)
    ranking = [_normalise(p) for p in raw.get("ranking", [])[:top_n]]
    _add_ranks(ranking)
    return ranking, "mock"
