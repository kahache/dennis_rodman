"""
Catalog of Dennis Rodman historic feats.
Each feat defines metadata and the query strategy for nba_client.
"""

FEATS = {
    "rebounds": {
        "id": "rebounds",
        "title": "All-Time Rebounds Leaders",
        "subtitle": "Career regular season total rebounds",
        "description": "Rodman led the NBA in rebounding for 7 consecutive seasons (1991–1998), a feat unmatched in the modern era.",
        "icon": "🏀",
        "unit": "total rebounds",
        "source_strategy": "live",   # will attempt nba_api
        "mock_file": "rebounds_leaders.json",
    },
    "defensive_teams": {
        "id": "defensive_teams",
        "title": "All-Defensive Team Selections",
        "subtitle": "Most NBA All-Defensive Team nominations in history",
        "description": "Rodman earned 8 All-Defensive First Team selections — the most in NBA history alongside Gary Payton and Kevin Garnett.",
        "icon": "🛡️",
        "unit": "selections",
        "source_strategy": "mock",   # not reliably queryable via nba_api
        "mock_file": "defensive_teams.json",
    },
    "championships": {
        "id": "championships",
        "title": "Most Championship Rings",
        "subtitle": "Players with the most NBA titles in history",
        "description": "Rodman won 5 NBA championships across three franchises — a testament to his impact on winning culture.",
        "icon": "💍",
        "unit": "championships",
        "source_strategy": "mock",
        "mock_file": "championships.json",
    },
    "steals": {
        "id": "steals",
        "title": "All-Time Steals Leaders",
        "subtitle": "Career regular season total steals",
        "description": "Despite being known for defense and rebounding, Rodman accumulated significant steals across his career.",
        "icon": "🕵️",
        "unit": "total steals",
        "source_strategy": "live",
        "mock_file": "steals_leaders.json",
    },
    "intensity": {
        "id": "intensity",
        "title": "The Chaos Leaderboard",
        "subtitle": "Most technical fouls & flagrant fouls — all-time intensity index",
        "description": "Pure chaos metric. Rodman's on-court intensity was legendary — ejections, technicals, and pure mayhem.",
        "icon": "🔥",
        "unit": "intensity points",
        "source_strategy": "mock",
        "mock_file": "intensity.json",
    },
}


def get_all_feats():
    """Return a list of feat summaries for the index page."""
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


def get_feat(feat_id: str):
    """Return full feat config or None."""
    return FEATS.get(feat_id)
