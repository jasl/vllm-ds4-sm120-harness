import pytest

from ds4_harness.multi_needle_probe import (
    build_multi_needle_prompt,
    run_multi_needle_probe,
    score_multi_needle_response,
)


def _answer_all(prompt):
    return "\n".join(f"{key}={code}" for key, code in prompt.needles)


def test_prompt_places_every_fact_and_asks_only_about_needles():
    prompt = build_multi_needle_prompt(line_count=512, needle_count=4, distractor_count=4)

    assert len(prompt.needles) == 4
    assert len(prompt.distractors) == 4
    # Distractors must be present in the haystack but absent from the question.
    question = prompt.text.rsplit("Question:", 1)[1]
    for key, code in prompt.needles:
        assert f"vault {key} is {code}" in prompt.text
        assert key in question
    for key, code in prompt.distractors:
        assert f"vault {key} is {code}" in prompt.text
        assert key not in question


def test_keys_and_codes_are_all_distinct():
    """A repeated key or code would make a hit ambiguous and silently inflate the score."""
    prompt = build_multi_needle_prompt(line_count=2048, needle_count=8, distractor_count=8)
    keys = [k for k, _ in prompt.needles] + [k for k, _ in prompt.distractors]
    codes = [c for _, c in prompt.needles] + [c for _, c in prompt.distractors]
    assert len(set(keys)) == len(keys)
    assert len(set(codes)) == len(codes)


def test_needles_are_spread_not_clustered():
    """Clustered needles would fit one attention window and measure the wrong thing."""
    prompt = build_multi_needle_prompt(line_count=4000, needle_count=8, distractor_count=0)
    lines = sorted(prompt.needle_lines)
    span = lines[-1] - lines[0]
    assert span > 4000 * 0.5, f"needles occupy only {span} of 4000 lines"


def test_scoring_requires_key_and_code_to_be_paired():
    prompt = build_multi_needle_prompt(line_count=512, needle_count=3, distractor_count=0)

    assert score_multi_needle_response(_answer_all(prompt), prompt)["needles_hit"] == 3

    # Codes alone must not score: a model that dumped every number it saw would
    # otherwise look perfect.
    codes_only = " ".join(code for _, code in prompt.needles)
    assert score_multi_needle_response(codes_only, prompt)["needles_hit"] == 0

    # Keys alone must not score either -- that is just echoing the question back.
    keys_only = " ".join(key for key, _ in prompt.needles)
    assert score_multi_needle_response(keys_only, prompt)["needles_hit"] == 0


def test_scoring_accepts_the_common_separators():
    prompt = build_multi_needle_prompt(line_count=512, needle_count=1, distractor_count=0)
    key, code = prompt.needles[0]
    for text in (f"{key}={code}", f"{key}: {code}", f"The code for {key} is {code}."):
        assert score_multi_needle_response(text, prompt)["needles_hit"] == 1, text


def test_scoring_counts_distractor_leaks_separately():
    """Reporting an unasked vault is a different failure from missing an asked one."""
    prompt = build_multi_needle_prompt(line_count=512, needle_count=2, distractor_count=2)
    dkey, dcode = prompt.distractors[0]
    result = score_multi_needle_response(f"{_answer_all(prompt)}\n{dkey}={dcode}", prompt)

    assert result["needles_hit"] == 2
    assert result["distractors_leaked"] == 1
    assert result["leaked_keys"] == [dkey]


def test_partial_recall_is_scored_continuously():
    """The point of per-needle scoring: a knee needs intermediate values, not pass/fail."""
    prompt = build_multi_needle_prompt(line_count=1024, needle_count=8, distractor_count=0)
    partial = "\n".join(f"{k}={c}" for k, c in prompt.needles[:5])
    result = score_multi_needle_response(partial, prompt)

    assert result["needles_hit"] == 5
    assert result["needles_total"] == 8
    assert sorted(result["missed_keys"]) == sorted(k for k, _ in prompt.needles[5:])


def test_repeats_reroll_the_prompt(monkeypatch):
    """Identical repeats would measure sampling noise, not retrieval."""
    seen = []

    def fake_post(*, base_url, model, prompt, max_tokens, timeout):
        seen.append(prompt)
        return {"choices": [{"message": {"content": ""}}], "usage": {"prompt_tokens": 1}}, 0.1

    run_multi_needle_probe(
        base_url="http://x", model="m", line_counts=[512],
        needle_count=2, distractor_count=2, repeat_count=3, post_func=fake_post,
    )
    assert len(seen) == 3
    assert len(set(seen)) == 3


def test_one_failed_cell_does_not_discard_the_rest():
    def fake_post(*, base_url, model, prompt, max_tokens, timeout):
        if "Line 2000:" in prompt:
            raise OSError("timed out")
        return {"choices": [{"message": {"content": ""}}], "usage": {"prompt_tokens": 7}}, 0.2

    rows = run_multi_needle_probe(
        base_url="http://x", model="m", line_counts=[512, 4096],
        needle_count=2, distractor_count=0, repeat_count=1, post_func=fake_post,
    )
    assert len(rows) == 2
    assert rows[0].get("error") is None
    assert "OSError" in rows[1]["error"]


def test_key_pool_spans_the_token_budget_crossing():
    """The pool must reach past where the 512-token budget actually saturates.

    The quantity under test is a 512-TOKEN attention budget, and a fact line runs about
    15 tokens, so retrieval cannot start failing until roughly 34 needles. A ladder that
    stops at 24 -- as the first version of this file did, capped by a 24-entry key list
    -- can only ever produce ceilings, whatever the model does.
    """
    from ds4_harness.multi_needle_probe import _VAULT_KEYS

    assert len(_VAULT_KEYS) >= 144, "cannot run 72 needles + 72 distractors"
    assert len(set(_VAULT_KEYS)) == len(_VAULT_KEYS)
    # No key may be a prefix of another, or a regex hit on the short one would also fire
    # inside the long one and credit a retrieval that never happened.
    ordered = sorted(_VAULT_KEYS)
    assert not any(b.startswith(a) for a, b in zip(ordered, ordered[1:]))

    prompt = build_multi_needle_prompt(line_count=4096, needle_count=72, distractor_count=72)
    assert len(prompt.needles) == 72


def test_impossible_configurations_are_rejected():
    with pytest.raises(ValueError):
        build_multi_needle_prompt(line_count=64, needle_count=1)          # too few lines
    with pytest.raises(ValueError):
        build_multi_needle_prompt(line_count=4096, needle_count=500)      # beyond the key pool
    with pytest.raises(ValueError):
        build_multi_needle_prompt(line_count=200, needle_count=80, distractor_count=80)


def test_output_budget_scales_with_needle_count():
    """A fixed budget silently caps recall; 512 capped 72 needles at ~55."""
    from ds4_harness.multi_needle_probe import default_max_tokens

    assert default_max_tokens(8) >= 512
    # 72 answer lines at ~11 tokens each need well over 512.
    assert default_max_tokens(72) > 72 * 11
    assert default_max_tokens(144) > default_max_tokens(72)


def test_truncation_is_recorded_and_never_scores_as_ok():
    """Truncation and failed retrieval produce the same hit count; they must not
    produce the same verdict."""
    def fake_post(*, base_url, model, prompt, max_tokens, timeout):
        return {
            "choices": [{"message": {"content": ""}, "finish_reason": "length"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": max_tokens},
        }, 0.1

    rows = run_multi_needle_probe(
        base_url="http://x", model="m", line_counts=[512],
        needle_count=2, distractor_count=0, repeat_count=1, post_func=fake_post,
    )
    assert rows[0]["truncated"] is True
    assert rows[0]["finish_reason"] == "length"
    assert rows[0]["ok"] is False


def test_a_complete_answer_is_not_flagged_truncated():
    prompts = []

    def fake_post(*, base_url, model, prompt, max_tokens, timeout):
        prompts.append(prompt)
        return {
            "choices": [{"message": {"content": ""}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20},
        }, 0.1

    rows = run_multi_needle_probe(
        base_url="http://x", model="m", line_counts=[512],
        needle_count=2, distractor_count=0, repeat_count=1, post_func=fake_post,
    )
    assert rows[0]["truncated"] is False
    assert rows[0]["max_tokens"] == 2 * 16 + 256 or rows[0]["max_tokens"] == 512
