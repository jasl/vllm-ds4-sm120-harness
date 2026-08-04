import urllib.error

import pytest

from ds4_harness import cold_prefill_probe
from ds4_harness.cold_prefill_probe import (
    ProbeResult,
    format_results,
    run_cold_prefill_probe,
)


def _patch_timer(monkeypatch, handler):
    """Replace the HTTP call with `handler(token_ids) -> seconds`."""
    calls = []

    def fake_time_completion(*, base_url, model, token_ids, max_tokens, timeout, api_key):
        calls.append(list(token_ids))
        return handler(token_ids)

    monkeypatch.setattr(cold_prefill_probe, "_time_completion", fake_time_completion)
    return calls


def test_probe_sends_exact_lengths_after_a_warmup(monkeypatch):
    calls = _patch_timer(monkeypatch, lambda ids: len(ids) / 1000.0)

    results = run_cold_prefill_probe(
        base_url="http://x", model="m", lengths=[8192, 32768]
    )

    # First call is the warmup and must not appear in the results.
    assert len(calls) == 3
    assert len(calls[0]) == cold_prefill_probe._WARMUP_TOKENS
    assert [len(c) for c in calls[1:]] == [8192, 32768]
    assert [r.prompt_tokens for r in results] == [8192, 32768]
    assert results[0].tokens_per_second == pytest.approx(1000.0)


def test_each_probe_uses_fresh_random_ids_so_a_cache_hit_is_impossible(monkeypatch):
    """The load-bearing property: two probes of the SAME length must not share a prefix.

    If they did, the second would be served from the prefix cache and report a warm
    number while claiming to be cold -- the exact failure this module exists to avoid.
    """
    calls = _patch_timer(monkeypatch, lambda ids: 1.0)

    run_cold_prefill_probe(base_url="http://x", model="m", lengths=[4096, 4096])

    first, second = calls[1], calls[2]
    assert len(first) == len(second) == 4096
    assert first != second
    assert first[:64] != second[:64]
    assert all(cold_prefill_probe._TOKEN_ID_MIN <= t < cold_prefill_probe._TOKEN_ID_MAX
               for t in first)


def test_one_failed_length_does_not_discard_the_others(monkeypatch):
    def handler(ids):
        if len(ids) == 260000:
            raise urllib.error.URLError("timed out")
        return 1.5

    _patch_timer(monkeypatch, handler)

    results = run_cold_prefill_probe(
        base_url="http://x", model="m", lengths=[8192, 260000, 32768]
    )

    assert [r.prompt_tokens for r in results] == [8192, 260000, 32768]
    assert results[0].seconds == 1.5
    assert results[1].seconds is None
    assert "URLError" in results[1].error
    assert results[2].seconds == 1.5


def test_warmup_failure_aborts_rather_than_reporting_compile_time_as_prefill(monkeypatch):
    def handler(ids):
        raise urllib.error.URLError("connection refused")

    _patch_timer(monkeypatch, handler)

    with pytest.raises(RuntimeError, match="warmup request failed"):
        run_cold_prefill_probe(base_url="http://x", model="m", lengths=[8192])


def test_empty_lengths_is_rejected():
    with pytest.raises(ValueError):
        run_cold_prefill_probe(base_url="http://x", model="m", lengths=[])


def test_failed_result_has_no_throughput_and_formats_as_failed():
    failed = ProbeResult(prompt_tokens=1024, seconds=None, error="URLError: nope")
    assert failed.tokens_per_second is None
    assert "FAILED" in format_results([failed])

    ok = ProbeResult(prompt_tokens=1024, seconds=2.0)
    assert ok.tokens_per_second == pytest.approx(512.0)
    assert "512.0 tok/s" in format_results([ok])
