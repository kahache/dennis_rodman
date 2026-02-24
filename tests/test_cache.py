"""
test_cache.py — Unit tests for cache.py

Covers: set, get, TTL expiry, clear, stats, overwrite behaviour.
"""

import time
import pytest
import cache


@pytest.fixture(autouse=True)
def reset_cache():
    """Wipe cache before every test so tests are fully isolated."""
    cache.clear()
    yield
    cache.clear()


class TestCacheSet:
    def test_set_string_value(self):
        cache.set("key1", "hello")
        assert cache.get("key1") == "hello"

    def test_set_dict_value(self):
        data = {"player": "Rodman", "value": 18.7}
        cache.set("key2", data)
        assert cache.get("key2") == data

    def test_set_list_value(self):
        cache.set("key3", [1, 2, 3])
        assert cache.get("key3") == [1, 2, 3]

    def test_set_integer_value(self):
        cache.set("key4", 42)
        assert cache.get("key4") == 42

    def test_overwrite_existing_key(self):
        cache.set("dup", "first")
        cache.set("dup", "second")
        assert cache.get("dup") == "second"

    def test_set_with_custom_ttl(self):
        cache.set("ttl_key", "value", ttl=999)
        assert cache.get("ttl_key") == "value"


class TestCacheGet:
    def test_get_existing_key(self):
        cache.set("exists", 99)
        assert cache.get("exists") == 99

    def test_get_missing_key_returns_none(self):
        assert cache.get("does_not_exist") is None

    def test_get_expired_key_returns_none(self):
        cache.set("soon_gone", "bye", ttl=0)
        time.sleep(0.05)
        assert cache.get("soon_gone") is None

    def test_get_unexpired_key_returns_value(self):
        cache.set("alive", "yes", ttl=60)
        time.sleep(0.05)
        assert cache.get("alive") == "yes"

    def test_get_removes_expired_entry_from_store(self):
        cache.set("ghost", "boo", ttl=0)
        time.sleep(0.05)
        cache.get("ghost")                    # triggers removal
        assert cache.stats()["total_keys"] == 0


class TestCacheClear:
    def test_clear_removes_all_keys(self):
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None
        assert cache.get("c") is None

    def test_clear_on_empty_cache_is_safe(self):
        cache.clear()   # should not raise
        assert cache.stats()["total_keys"] == 0


class TestCacheStats:
    def test_stats_empty_cache(self):
        s = cache.stats()
        assert s["total_keys"] == 0
        assert s["live_keys"] == 0

    def test_stats_counts_live_keys(self):
        cache.set("live1", 1, ttl=60)
        cache.set("live2", 2, ttl=60)
        s = cache.stats()
        assert s["total_keys"] == 2
        assert s["live_keys"] == 2

    def test_stats_counts_expired_keys(self):
        cache.set("dead", "rip", ttl=0)
        time.sleep(0.05)
        s = cache.stats()
        assert s["expired_keys"] >= 1

    def test_stats_returns_required_fields(self):
        s = cache.stats()
        assert "total_keys"   in s
        assert "live_keys"    in s
        assert "expired_keys" in s
