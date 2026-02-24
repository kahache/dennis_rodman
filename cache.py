"""
Simple in-memory cache with TTL (time-to-live).
Avoids hammering stats.nba.com on repeated requests.
"""

import time
from typing import Any, Optional

_store: dict[str, dict] = {}
DEFAULT_TTL = 600  # 10 minutes


def get(key: str) -> Optional[Any]:
    """Return cached value if it exists and hasn't expired."""
    entry = _store.get(key)
    if entry is None:
        return None
    if time.time() > entry["expires_at"]:
        del _store[key]
        return None
    return entry["value"]


def set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Store a value with an expiry timestamp."""
    _store[key] = {
        "value": value,
        "expires_at": time.time() + ttl,
    }


def clear() -> None:
    """Wipe the entire cache (useful for testing)."""
    _store.clear()


def stats() -> dict:
    """Return cache diagnostics."""
    now = time.time()
    return {
        "total_keys": len(_store),
        "live_keys": sum(1 for e in _store.values() if e["expires_at"] > now),
    }
