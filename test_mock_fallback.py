"""
test_mock_fallback.py

Tests that:
1. All mocks are valid JSON and have the expected shape.
2. nba_client falls back to mock when the live fetcher raises.
3. The cache stores and retrieves values correctly.
4. FastAPI endpoints return expected status codes.
"""

import json
import os
import sys
import pytest

# Make sure backend/ is on the path when running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# ── Helpers ───────────────────────────────────────────────────────────────

MOCKS_DIR = os.path.join(os.path.dirname(__file__), "backend", "mocks")

EXPECTED_MOCKS = [
    "rebounds_leaders.json",
    "defensive_teams.json",
    "championships.json",
    "steals_leaders.json",
    "intensity.json",
]

REQUIRED_PLAYER_KEYS = {"player", "value", "is_rodman"}


# ── Mock file tests ────────────────────────────────────────────────────────

class TestMockFiles:
    def test_all_mock_files_exist(self):
        for filename in EXPECTED_MOCKS:
            path = os.path.join(MOCKS_DIR, filename)
            assert os.path.isfile(path), f"Missing mock file: {filename}"

    def test_mock_files_are_valid_json(self):
        for filename in EXPECTED_MOCKS:
            path = os.path.join(MOCKS_DIR, filename)
            with open(path) as f:
                data = json.load(f)
            assert isinstance(data, dict), f"{filename} should be a JSON object"

    def test_mock_files_have_ranking_key(self):
        for filename in EXPECTED_MOCKS:
            path = os.path.join(MOCKS_DIR, filename)
            with open(path) as f:
                data = json.load(f)
            assert "ranking" in data, f"{filename} missing 'ranking' key"
            assert isinstance(data["ranking"], list), f"{filename} 'ranking' should be a list"
            assert len(data["ranking"]) > 0, f"{filename} 'ranking' is empty"

    def test_ranking_entries_have_required_fields(self):
        for filename in EXPECTED_MOCKS:
            path = os.path.join(MOCKS_DIR, filename)
            with open(path) as f:
                data = json.load(f)
            for i, entry in enumerate(data["ranking"]):
                missing = REQUIRED_PLAYER_KEYS - entry.keys()
                assert not missing, (
                    f"{filename} entry[{i}] missing fields: {missing}"
                )

    def test_is_rodman_flag_is_boolean(self):
        for filename in EXPECTED_MOCKS:
            path = os.path.join(MOCKS_DIR, filename)
            with open(path) as f:
                data = json.load(f)
            for i, entry in enumerate(data["ranking"]):
                assert isinstance(entry["is_rodman"], bool), (
                    f"{filename} entry[{i}]['is_rodman'] must be bool, got {type(entry['is_rodman'])}"
                )


# ── nba_client fallback test ───────────────────────────────────────────────

class TestNbaClientFallback:
    def test_falls_back_to_mock_on_live_failure(self, monkeypatch):
        """
        If the live fetcher raises any exception, fetch_ranking() must
        return mock data and source == 'mock'.
        """
        import nba_client

        def exploding_fetcher(top_n=10):
            raise ConnectionError("Simulated stats.nba.com timeout")

        # Patch the live fetchers dict
        monkeypatch.setitem(nba_client.LIVE_FETCHERS, "rebounds", exploding_fetcher)

        import feats as feats_catalog
        feat = feats_catalog.get_feat("rebounds")
        feat_with_live = {**feat, "source_strategy": "live"}

        ranking, source = nba_client.fetch_ranking(feat_with_live, top_n=10)

        assert source == "mock", "Expected 'mock' source after live failure"
        assert isinstance(ranking, list), "Ranking should be a list"
        assert len(ranking) > 0, "Fallback ranking should not be empty"

    def test_mock_strategy_skips_live(self, monkeypatch):
        """
        If source_strategy is 'mock', never attempt live fetch.
        """
        import nba_client

        called = {"yes": False}

        def should_not_be_called(top_n=10):
            called["yes"] = True
            return []

        monkeypatch.setitem(nba_client.LIVE_FETCHERS, "championships", should_not_be_called)

        import feats as feats_catalog
        feat = feats_catalog.get_feat("championships")  # strategy == "mock"
        ranking, source = nba_client.fetch_ranking(feat, top_n=10)

        assert not called["yes"], "Live fetcher should NOT be called for mock-strategy feats"
        assert source == "mock"

    def test_rank_field_added_to_mock_results(self):
        """
        fetch_ranking() should inject 'rank' into every entry.
        """
        import nba_client
        import feats as feats_catalog

        feat = feats_catalog.get_feat("intensity")  # always mock
        ranking, _ = nba_client.fetch_ranking(feat, top_n=5)

        for i, entry in enumerate(ranking):
            assert "rank" in entry, f"Entry {i} missing 'rank'"
            assert entry["rank"] == i + 1, f"Entry {i} has wrong rank {entry['rank']}"


# ── Cache tests ────────────────────────────────────────────────────────────

class TestCache:
    def setup_method(self):
        import cache
        cache.clear()

    def test_set_and_get(self):
        import cache
        cache.set("test_key", {"hello": "world"})
        result = cache.get("test_key")
        assert result == {"hello": "world"}

    def test_missing_key_returns_none(self):
        import cache
        assert cache.get("nonexistent_key") is None

    def test_expired_key_returns_none(self):
        import cache
        cache.set("short_lived", "value", ttl=0)  # expires immediately
        import time; time.sleep(0.01)
        assert cache.get("short_lived") is None

    def test_clear_wipes_all_keys(self):
        import cache
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None


# ── FastAPI endpoint smoke tests ───────────────────────────────────────────

class TestAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app import app
        return TestClient(app)

    def test_health_endpoint(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    def test_feats_list_returns_all_feats(self, client):
        res = client.get("/api/feats")
        assert res.status_code == 200
        data = res.json()
        assert "feats" in data
        assert data["total"] == 5  # rebounds, defensive_teams, championships, steals, intensity
        ids = [f["id"] for f in data["feats"]]
        assert "rebounds" in ids
        assert "intensity" in ids

    def test_ranking_returns_top_10(self, client):
        res = client.get("/api/feats/rebounds/ranking")
        assert res.status_code == 200
        data = res.json()
        assert "ranking" in data
        assert len(data["ranking"]) <= 10
        assert "source" in data
        assert data["source"] in ("live", "mock")

    def test_unknown_feat_returns_404(self, client):
        res = client.get("/api/feats/does_not_exist/ranking")
        assert res.status_code == 404

    def test_rodman_flag_in_rankings(self, client):
        """At least one of our feats should surface Rodman."""
        feat_ids = ["rebounds", "defensive_teams", "championships", "steals", "intensity"]
        found_rodman = False
        for fid in feat_ids:
            res = client.get(f"/api/feats/{fid}/ranking")
            data = res.json()
            if data.get("rodman_in_ranking"):
                found_rodman = True
                break
        assert found_rodman, "Rodman should appear in at least one ranking"
