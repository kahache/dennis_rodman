"""
test_nba_client.py — Unit tests for nba_client.py

Covers: mock loading, normalisation, rank injection, fallback behaviour,
        is_rodman detection, Rodman-is-first contract.
"""

import json
import os
import pytest
import nba_client
import feats as feats_catalog

BACKEND_DIR = os.path.dirname(os.path.abspath(nba_client.__file__))
MOCKS_DIR   = os.path.join(BACKEND_DIR, "mocks")

ALL_MOCK_FILES = [
    "rebounding_titles.json",
    "season_rpg.json",
    "offensive_rebounds_season.json",
    "consecutive_titles.json",
    "chaos_index.json",
]

REQUIRED_RANKING_KEYS = {"rank", "player", "value", "is_rodman"}


# ---------------------------------------------------------------------------
# Mock file integrity
# ---------------------------------------------------------------------------

class TestMockFiles:
    def test_all_mock_files_exist(self):
        for filename in ALL_MOCK_FILES:
            path = os.path.join(MOCKS_DIR, filename)
            assert os.path.isfile(path), f"Missing mock: {filename}"

    def test_all_mock_files_are_valid_json(self):
        for filename in ALL_MOCK_FILES:
            path = os.path.join(MOCKS_DIR, filename)
            with open(path) as f:
                data = json.load(f)
            assert isinstance(data, dict), f"{filename} must be a JSON object"

    def test_all_mock_files_have_ranking_key(self):
        for filename in ALL_MOCK_FILES:
            path = os.path.join(MOCKS_DIR, filename)
            with open(path) as f:
                data = json.load(f)
            assert "ranking" in data, f"{filename} missing 'ranking'"
            assert isinstance(data["ranking"], list)
            assert len(data["ranking"]) >= 1

    def test_all_ranking_entries_have_required_fields(self):
        for filename in ALL_MOCK_FILES:
            path = os.path.join(MOCKS_DIR, filename)
            with open(path) as f:
                data = json.load(f)
            for i, entry in enumerate(data["ranking"]):
                missing = {"player", "value", "is_rodman"} - entry.keys()
                assert not missing, f"{filename}[{i}] missing: {missing}"

    def test_is_rodman_field_is_boolean(self):
        for filename in ALL_MOCK_FILES:
            path = os.path.join(MOCKS_DIR, filename)
            with open(path) as f:
                data = json.load(f)
            for i, entry in enumerate(data["ranking"]):
                assert isinstance(entry["is_rodman"], bool), (
                    f"{filename}[{i}] is_rodman must be bool"
                )

    def test_rodman_is_rank_1_in_every_mock(self):
        """Core contract: The Worm must be #1 in every feat."""
        for filename in ALL_MOCK_FILES:
            path = os.path.join(MOCKS_DIR, filename)
            with open(path) as f:
                data = json.load(f)
            first = data["ranking"][0]
            assert first["is_rodman"] is True, (
                f"{filename}: first entry is '{first['player']}', not Rodman"
            )


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------

class TestNormalise:
    def test_normalise_adds_all_required_fields(self):
        raw = {"player": "Dennis Rodman", "value": 7, "is_rodman": True}
        result = nba_client._normalise(raw)
        assert REQUIRED_RANKING_KEYS.issubset(result.keys())

    def test_normalise_defaults_team_to_none(self):
        raw = {"player": "X", "value": 1, "is_rodman": False}
        result = nba_client._normalise(raw)
        assert result["team"] is None

    def test_normalise_preserves_team(self):
        raw = {"player": "X", "team": "CHI", "value": 1, "is_rodman": False}
        result = nba_client._normalise(raw)
        assert result["team"] == "CHI"

    def test_normalise_casts_is_rodman_to_bool(self):
        raw = {"player": "X", "value": 1, "is_rodman": 1}
        result = nba_client._normalise(raw)
        assert result["is_rodman"] is True

    def test_normalise_passes_through_season_field(self):
        raw = {"player": "Rodman", "value": 18.7, "is_rodman": True, "season": "1991-92"}
        result = nba_client._normalise(raw)
        assert result.get("season") == "1991-92"


# ---------------------------------------------------------------------------
# Rank injection
# ---------------------------------------------------------------------------

class TestAddRanks:
    def test_ranks_start_at_one(self):
        players = [{"player": "A"}, {"player": "B"}, {"player": "C"}]
        nba_client._add_ranks(players)
        assert players[0]["rank"] == 1

    def test_ranks_are_sequential(self):
        players = [{"player": str(i)} for i in range(5)]
        nba_client._add_ranks(players)
        ranks = [p["rank"] for p in players]
        assert ranks == [1, 2, 3, 4, 5]

    def test_returns_same_list(self):
        players = [{"player": "X"}]
        result = nba_client._add_ranks(players)
        assert result is players


# ---------------------------------------------------------------------------
# is_rodman detection
# ---------------------------------------------------------------------------

class TestIsRodman:
    @pytest.mark.parametrize("name", [
        "Dennis Rodman",
        "dennis rodman",
        "DENNIS RODMAN",
        "D. Rodman",
        "rodman",
    ])
    def test_detects_rodman_variations(self, name):
        assert nba_client._is_rodman(name) is True

    @pytest.mark.parametrize("name", [
        "Michael Jordan",
        "Scottie Pippen",
        "Charles Barkley",
        "",
    ])
    def test_does_not_false_positive(self, name):
        assert nba_client._is_rodman(name) is False


# ---------------------------------------------------------------------------
# fetch_ranking — fallback behaviour
# ---------------------------------------------------------------------------

class TestFetchRankingFallback:
    def test_mock_strategy_never_calls_live(self, monkeypatch):
        called = {"count": 0}

        def fake_live(top_n=10):
            called["count"] += 1
            return []

        monkeypatch.setitem(nba_client.LIVE_FETCHERS, "chaos_index", fake_live)
        feat = feats_catalog.get_feat("chaos_index")  # source_strategy = "mock"
        nba_client.fetch_ranking(feat, top_n=5)
        assert called["count"] == 0, "Live fetcher should not be called for mock strategy"

    def test_live_failure_falls_back_to_mock(self, monkeypatch):
        def explode(top_n=10):
            raise ConnectionError("Simulated timeout")

        monkeypatch.setitem(nba_client.LIVE_FETCHERS, "season_rpg", explode)
        feat = feats_catalog.get_feat("season_rpg")
        ranking, source = nba_client.fetch_ranking(feat, top_n=10)

        assert source == "mock"
        assert len(ranking) > 0

    def test_mock_source_label_returned_for_mock_feats(self):
        feat = feats_catalog.get_feat("rebounding_titles")
        _, source = nba_client.fetch_ranking(feat)
        assert source == "mock"

    def test_top_n_is_respected(self):
        feat = feats_catalog.get_feat("chaos_index")
        ranking, _ = nba_client.fetch_ranking(feat, top_n=3)
        assert len(ranking) <= 3

    def test_ranking_entries_are_normalised(self):
        feat = feats_catalog.get_feat("rebounding_titles")
        ranking, _ = nba_client.fetch_ranking(feat)
        for entry in ranking:
            assert REQUIRED_RANKING_KEYS.issubset(entry.keys()), (
                f"Entry missing required keys: {entry}"
            )

    def test_rank_fields_are_sequential(self):
        feat = feats_catalog.get_feat("chaos_index")
        ranking, _ = nba_client.fetch_ranking(feat, top_n=5)
        ranks = [p["rank"] for p in ranking]
        assert ranks == list(range(1, len(ranks) + 1))


# ---------------------------------------------------------------------------
# Rodman-is-first contract (integration with mocks)
# ---------------------------------------------------------------------------

class TestRodmanIsFirst:
    @pytest.mark.parametrize("feat_id", feats_catalog.FEAT_IDS)
    def test_rodman_is_rank_1_for_every_feat(self, feat_id):
        """The most important test in the suite."""
        feat = feats_catalog.get_feat(feat_id)
        ranking, _ = nba_client.fetch_ranking(feat, top_n=10)

        assert ranking, f"Feat '{feat_id}' returned empty ranking"
        first = ranking[0]
        assert first["rank"] == 1, f"First entry has rank {first['rank']}, expected 1"
        assert first["is_rodman"] is True, (
            f"Feat '{feat_id}': rank #1 is '{first['player']}', not Rodman"
        )
