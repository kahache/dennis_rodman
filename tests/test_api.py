"""
test_api.py — Integration tests for FastAPI endpoints.

Uses FastAPI's TestClient (wraps httpx) — no real server needed.
"""

import pytest
from fastapi.testclient import TestClient

# app.py imports cache, feats, nba_client — all resolved via tests/__init__.py
from app import app
import cache


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_returns_200(self, client):
        res = client.get("/api/health")
        assert res.status_code == 200

    def test_body_has_status_ok(self, client):
        data = client.get("/api/health").json()
        assert data["status"] == "ok"

    def test_body_has_message(self, client):
        data = client.get("/api/health").json()
        assert "message" in data


# ---------------------------------------------------------------------------
# GET /api/feats
# ---------------------------------------------------------------------------

class TestListFeats:
    def test_returns_200(self, client):
        assert client.get("/api/feats").status_code == 200

    def test_returns_feats_list(self, client):
        data = client.get("/api/feats").json()
        assert "feats" in data
        assert isinstance(data["feats"], list)

    def test_total_field_matches_list_length(self, client):
        data = client.get("/api/feats").json()
        assert data["total"] == len(data["feats"])

    def test_returns_five_feats(self, client):
        data = client.get("/api/feats").json()
        assert data["total"] == 5

    def test_expected_feat_ids_present(self, client):
        data  = client.get("/api/feats").json()
        ids   = {f["id"] for f in data["feats"]}
        expected = {
            "rebounding_titles", "season_rpg",
            "offensive_rebounds_season", "consecutive_titles", "chaos_index",
        }
        assert expected == ids

    def test_no_internal_fields_leaked(self, client):
        data = client.get("/api/feats").json()
        internal = {"source_strategy", "mock_file"}
        for feat in data["feats"]:
            leaked = internal & feat.keys()
            assert not leaked, f"Internal fields leaked: {leaked}"


# ---------------------------------------------------------------------------
# GET /api/feats/{feat_id}
# ---------------------------------------------------------------------------

class TestGetFeatMeta:
    def test_valid_feat_returns_200(self, client):
        assert client.get("/api/feats/chaos_index").status_code == 200

    def test_unknown_feat_returns_404(self, client):
        assert client.get("/api/feats/does_not_exist").status_code == 404

    def test_returned_feat_has_id(self, client):
        data = client.get("/api/feats/chaos_index").json()
        assert data["id"] == "chaos_index"

    def test_no_internal_fields_in_response(self, client):
        data = client.get("/api/feats/chaos_index").json()
        assert "source_strategy" not in data
        assert "mock_file" not in data


# ---------------------------------------------------------------------------
# GET /api/feats/{feat_id}/ranking
# ---------------------------------------------------------------------------

class TestGetRanking:
    def test_valid_feat_returns_200(self, client):
        assert client.get("/api/feats/rebounding_titles/ranking").status_code == 200

    def test_unknown_feat_returns_404(self, client):
        assert client.get("/api/feats/unknown/ranking").status_code == 404

    def test_response_has_required_fields(self, client):
        data = client.get("/api/feats/chaos_index/ranking").json()
        for field in ("feat_id", "title", "subtitle", "unit", "source", "ranking",
                      "rodman_in_ranking", "rodman_is_first"):
            assert field in data, f"Missing field: {field}"

    def test_ranking_is_list(self, client):
        data = client.get("/api/feats/chaos_index/ranking").json()
        assert isinstance(data["ranking"], list)

    def test_default_top_n_is_10(self, client):
        data = client.get("/api/feats/chaos_index/ranking").json()
        assert len(data["ranking"]) <= 10

    def test_custom_top_n_respected(self, client):
        data = client.get("/api/feats/chaos_index/ranking?top_n=3").json()
        assert len(data["ranking"]) <= 3

    def test_top_n_clamped_at_25(self, client):
        data = client.get("/api/feats/chaos_index/ranking?top_n=999").json()
        assert len(data["ranking"]) <= 25

    def test_source_is_live_or_mock(self, client):
        data = client.get("/api/feats/chaos_index/ranking").json()
        assert data["source"] in ("live", "mock")

    def test_ranking_entries_have_required_fields(self, client):
        data    = client.get("/api/feats/rebounding_titles/ranking").json()
        required = {"rank", "player", "value", "is_rodman"}
        for entry in data["ranking"]:
            missing = required - entry.keys()
            assert not missing, f"Entry missing fields: {missing}"

    def test_ranks_are_sequential_from_one(self, client):
        data  = client.get("/api/feats/rebounding_titles/ranking").json()
        ranks = [e["rank"] for e in data["ranking"]]
        assert ranks == list(range(1, len(ranks) + 1))

    def test_rodman_is_first_flag_true_for_all_feats(self, client):
        feat_ids = [
            "rebounding_titles", "season_rpg",
            "offensive_rebounds_season", "consecutive_titles", "chaos_index",
        ]
        for feat_id in feat_ids:
            data = client.get(f"/api/feats/{feat_id}/ranking").json()
            assert data["rodman_is_first"] is True, (
                f"Feat '{feat_id}': rodman_is_first is False — "
                f"rank #1 is '{data['ranking'][0]['player']}'"
            )

    def test_rodman_in_ranking_is_true_for_all_feats(self, client):
        feat_ids = [
            "rebounding_titles", "season_rpg",
            "offensive_rebounds_season", "consecutive_titles", "chaos_index",
        ]
        for feat_id in feat_ids:
            data = client.get(f"/api/feats/{feat_id}/ranking").json()
            assert data["rodman_in_ranking"] is True, (
                f"Feat '{feat_id}': Rodman not found in ranking at all"
            )


# ---------------------------------------------------------------------------
# Caching behaviour
# ---------------------------------------------------------------------------

class TestCachingBehaviour:
    def test_second_request_uses_cache(self, client, monkeypatch):
        call_count = {"n": 0}
        original_fetch = __import__("nba_client").fetch_ranking

        def counting_fetch(feat, top_n=10):
            call_count["n"] += 1
            return original_fetch(feat, top_n)

        monkeypatch.setattr("nba_client.fetch_ranking", counting_fetch)

        client.get("/api/feats/chaos_index/ranking")
        client.get("/api/feats/chaos_index/ranking")

        assert call_count["n"] == 1, (
            "fetch_ranking should only be called once; second request should hit cache"
        )
