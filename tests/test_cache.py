import time

from app.cache import QueryCache


def test_cache_hit_and_miss():
    cache = QueryCache(default_ttl_seconds=60)
    key = cache.compute_key("How much subsidy for 3 kW solar?", top_k=3)

    # Initially missing
    assert cache.get(key) is None
    assert cache.misses == 1
    assert cache.hits == 0

    # Store entry
    dummy_response = {"answer": "₹78,000 subsidy available.", "confidence": "high"}
    cache.set(key, dummy_response)

    # Cache hit
    cached = cache.get(key)
    assert cached == dummy_response
    assert cache.hits == 1


def test_cache_query_normalization():
    cache = QueryCache()
    # Varying casing, whitespace, and punctuation should yield the exact same cache key
    key1 = cache.compute_key("  How much subsidy for 3 kW solar?  ")
    key2 = cache.compute_key("how much subsidy for 3 kw solar")
    key3 = cache.compute_key("HOW MUCH SUBSIDY FOR 3 KW SOLAR!!")

    assert key1 == key2 == key3


def test_cache_ttl_expiration():
    # Cache with very short 0.1s TTL
    cache = QueryCache(default_ttl_seconds=1)
    key = cache.compute_key("Quick query")
    cache.set(key, {"data": "solar"}, ttl=0.1)

    # Immediately available
    assert cache.get(key) == {"data": "solar"}

    # Wait past TTL
    time.sleep(0.15)
    assert cache.get(key) is None
    assert cache.evictions >= 1


def test_cache_stats_and_clear():
    cache = QueryCache()
    key1 = cache.compute_key("Q1")
    key2 = cache.compute_key("Q2")

    cache.set(key1, "Val1")
    cache.get(key1)  # hit
    cache.get(key2)  # miss

    stats = cache.get_stats()
    assert stats["active_entries"] == 1
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["total_requests"] == 2
    assert stats["hit_ratio"] == 0.5

    cache.clear()
    assert cache.get_stats()["active_entries"] == 0
    assert cache.get_stats()["hits"] == 0
