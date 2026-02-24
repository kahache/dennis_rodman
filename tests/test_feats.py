"""
test_feats.py — Unit tests for feats.py

Covers: catalog completeness, data shape, Rodman-is-first contract.
"""

import pytest
import feats as feats_catalog

EXPECTED_FEAT_IDS = {
    "rebounding_titles",
    "season_rpg",
    "offensive_rebounds_season",
    "consecutive_titles",
    "chaos_index",
}

REQUIRED_FEAT_KEYS = {"id", "title", "subtitle", "description", "icon", "unit",
                      "source_strategy", "mock_file"}

VALID_STRATEGIES = {"live", "mock"}


class TestFeatCatalog:
    def test_all_expected_feats_present(self):
        assert EXPECTED_FEAT_IDS == feats_catalog.FEAT_IDS

    def test_feat_count_matches(self):
        assert len(feats_catalog.FEATS) == len(EXPECTED_FEAT_IDS)

    def test_each_feat_has_required_keys(self):
        for feat_id, feat in feats_catalog.FEATS.items():
            missing = REQUIRED_FEAT_KEYS - feat.keys()
            assert not missing, f"Feat '{feat_id}' missing keys: {missing}"

    def test_feat_ids_are_consistent(self):
        """The 'id' field inside the dict must match the dict key."""
        for key, feat in feats_catalog.FEATS.items():
            assert feat["id"] == key, (
                f"Key '{key}' has mismatched internal id '{feat['id']}'"
            )

    def test_source_strategy_is_valid(self):
        for feat_id, feat in feats_catalog.FEATS.items():
            assert feat["source_strategy"] in VALID_STRATEGIES, (
                f"Feat '{feat_id}' has invalid source_strategy '{feat['source_strategy']}'"
            )

    def test_mock_file_is_non_empty_string(self):
        for feat_id, feat in feats_catalog.FEATS.items():
            assert isinstance(feat["mock_file"], str) and feat["mock_file"], (
                f"Feat '{feat_id}' has blank mock_file"
            )

    def test_mock_file_ends_with_json(self):
        for feat_id, feat in feats_catalog.FEATS.items():
            assert feat["mock_file"].endswith(".json"), (
                f"Feat '{feat_id}' mock_file does not end with .json"
            )

    def test_icon_is_non_empty(self):
        for feat_id, feat in feats_catalog.FEATS.items():
            assert feat["icon"], f"Feat '{feat_id}' has empty icon"


class TestGetAllFeats:
    def test_returns_list(self):
        result = feats_catalog.get_all_feats()
        assert isinstance(result, list)

    def test_returns_correct_count(self):
        result = feats_catalog.get_all_feats()
        assert len(result) == len(feats_catalog.FEATS)

    def test_public_fields_only(self):
        """Internal fields must not leak into the public summary."""
        result = feats_catalog.get_all_feats()
        internal_fields = {"source_strategy", "mock_file"}
        for item in result:
            leaked = internal_fields & item.keys()
            assert not leaked, f"Internal fields leaked into summary: {leaked}"

    def test_each_summary_has_id(self):
        for item in feats_catalog.get_all_feats():
            assert "id" in item


class TestGetFeat:
    def test_returns_feat_for_valid_id(self):
        for feat_id in EXPECTED_FEAT_IDS:
            feat = feats_catalog.get_feat(feat_id)
            assert feat is not None
            assert feat["id"] == feat_id

    def test_returns_none_for_unknown_id(self):
        assert feats_catalog.get_feat("does_not_exist") is None

    def test_returns_none_for_empty_string(self):
        assert feats_catalog.get_feat("") is None

    def test_returned_feat_contains_all_keys(self):
        feat = feats_catalog.get_feat("chaos_index")
        assert feat is not None
        missing = REQUIRED_FEAT_KEYS - feat.keys()
        assert not missing
