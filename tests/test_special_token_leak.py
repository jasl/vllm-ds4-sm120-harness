"""A leaked control token is a defect no matter how fluent its surroundings.

brianmiller (vllm-project/vllm#41834) hit a spurious `<｜begin▁of▁sentence｜>`
mid-generation under concurrent mixed prefill+decode with MTP. The text either
side of it stayed fluent English, so every other signal the coherence gate
scores -- replacement characters, script mixing, degenerate repetition -- rated
those responses coherent. The gate could not have caught the failure it was
pointed at.
"""

from ds4_harness.coherence_gate import (
    assess_english_coherence,
    find_leaked_special_tokens,
)

_LEAK = "<｜begin▁of▁sentence｜>"


def test_fluent_text_around_a_leaked_token_still_fails():
    text = (
        "# Summary\nThe deployment completed without errors."
        f"{_LEAK}"
        "# Summary\nThe subsequent run also completed cleanly."
    )
    result = assess_english_coherence(text)

    assert not result.ok
    assert "begin" in result.detail
    # The pre-existing heuristics see nothing wrong, which is the whole point.
    assert "�" not in text
    assert result.non_latin_fraction == 0.0


def test_clean_english_is_unaffected():
    text = "The deployment completed and the logs show nothing unusual."
    assert assess_english_coherence(text).ok


def test_ordinary_angle_brackets_are_not_control_tokens():
    for text in ("if a<b and c>d", "use <html> tags", "a <| b |> c"):
        assert find_leaked_special_tokens(text) == []


def test_reports_every_distinct_leaked_token():
    text = f"start{_LEAK}middle<｜end▁of▁sentence｜>tail{_LEAK}"
    assert sorted(set(find_leaked_special_tokens(text))) == [
        "<｜begin▁of▁sentence｜>",
        "<｜end▁of▁sentence｜>",
    ]
