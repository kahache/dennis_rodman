"""
feats.py — Catalog of Dennis Rodman historic feats.

Rule for v2: every feat must have Rodman ranked #1.
All stats are post-1980 (modern NBA era) unless noted.
Sources: Basketball-Reference, NBA official records.
"""

FEATS: dict[str, dict] = {
    "rebounding_titles": {
        "id": "rebounding_titles",
        "title": "Most Rebounding Titles",
        "subtitle": "Players with the most NBA rebounding crowns — modern era (post-1973)",
        "description": (
            "Rodman won the rebounding title 7 consecutive seasons (1991–1998). "
            "No player in the modern era comes close."
        ),
        "icon": "👑",
        "unit": "rebounding titles",
        "source_strategy": "mock",
        "mock_file": "rebounding_titles.json",
    },
    "season_rpg": {
        "id": "season_rpg",
        "title": "Highest Single-Season RPG",
        "subtitle": "Best rebounds-per-game average in a single season — post-1980",
        "description": (
            "In 1991–92, Rodman averaged 18.7 RPG — the highest single-season "
            "rebounding average in the post-1980 era."
        ),
        "icon": "📈",
        "unit": "rebounds per game",
        "source_strategy": "live",
        "mock_file": "season_rpg.json",
    },
    "offensive_rebounds_season": {
        "id": "offensive_rebounds_season",
        "title": "Most Offensive Rebounds in a Season",
        "subtitle": "Single-season offensive rebound leaders — post-1980",
        "description": (
            "Rodman's relentless positioning and timing made him the king of "
            "second-chance opportunities. He holds the post-1980 record."
        ),
        "icon": "💥",
        "unit": "offensive rebounds",
        "source_strategy": "live",
        "mock_file": "offensive_rebounds_season.json",
    },
    "consecutive_titles": {
        "id": "consecutive_titles",
        "title": "Most Consecutive Rebounding Titles",
        "subtitle": "Longest streak of consecutive NBA rebounding crowns",
        "description": (
            "Seven straight. No player in NBA history has ever won the rebounding "
            "title more consecutively than Dennis Rodman."
        ),
        "icon": "🔗",
        "unit": "consecutive titles",
        "source_strategy": "mock",
        "mock_file": "consecutive_titles.json",
    },
    "chaos_index": {
        "id": "chaos_index",
        "title": "The Worm's Chaos Index",
        "subtitle": "All-time intensity leaderboard — technical fouls, flagrants & ejections",
        "description": (
            "Pure, unfiltered chaos. Rodman's on-court mayhem was legendary and "
            "completely unmatched. This is his most dominant stat of all."
        ),
        "icon": "🔥",
        "unit": "chaos points",
        "source_strategy": "mock",
        "mock_file": "chaos_index.json",
    },
}


def get_all_feats() -> list[dict]:
    """Return feat summaries for the index page (no internal fields)."""
    return [
        {
            "id": f["id"],
            "title": f["title"],
            "subtitle": f["subtitle"],
            "description": f["description"],
            "icon": f["icon"],
            "unit": f["unit"],
        }
        for f in FEATS.values()
    ]


def get_feat(feat_id: str) -> dict | None:
    """Return full feat config or None if not found."""
    return FEATS.get(feat_id)


# Convenience set for tests
FEAT_IDS = set(FEATS.keys())
