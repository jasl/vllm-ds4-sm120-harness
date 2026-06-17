from ds4_harness.coherence_gate import (
    assess_english_coherence,
    run_long_context_coherence_gate,
)
from ds4_harness.long_context_probe import DEFAULT_REQUIRED_TERMS


_CLEAN_ANSWER = (
    "The first indexer validation code is alpha-cobalt-17, the middle indexer "
    "validation code is beta-quartz-29, and the final indexer validation code "
    "is gamma-onyx-43."
)


def _chat(content):
    return {"choices": [{"message": {"content": content}, "finish_reason": "stop"}]}


def test_assess_english_coherence_accepts_clean_answer():
    result = assess_english_coherence(_CLEAN_ANSWER)

    assert result.ok
    assert result.non_latin_fraction == 0.0


def test_assess_english_coherence_tolerates_occasional_non_latin_token():
    result = assess_english_coherence(
        "The configuration file 设定 was loaded and the service started cleanly "
        "with all English diagnostics reporting nominal status across the run."
    )

    assert result.ok


def test_assess_english_coherence_rejects_mixed_script_gibberish():
    result = assess_english_coherence(
        "代码是的の안녕시스템验证な코드エラー混乱한字符串の乱码検証システム"
    )

    assert not result.ok
    assert "non-Latin" in result.detail


def test_assess_english_coherence_rejects_arthur_reported_fragment():
    # The verbatim mixed-script fragment from PR#41834 comment 4734576100
    # (Greek + Cyrillic + CJK injected into English) must be flagged.
    result = assess_english_coherence(
        "Lambdaλθελόγ—— just查看 logs, let me check --result instead of "
        "polling我的猜测 aλθελόγaπInfobox, let me test proxying внутрьπροσπ + wait"
    )

    assert not result.ok
    assert "non-Latin" in result.detail


def test_assess_english_coherence_rejects_replacement_char_and_degenerate():
    assert not assess_english_coherence("answer is ����������").ok
    assert not assess_english_coherence("a" * 60).ok
    assert not assess_english_coherence("").ok


def test_run_gate_passes_when_all_responses_are_coherent_and_recall_codes():
    seen_payloads = []

    def fake_post(base_url, path, payload, timeout, **kwargs):
        seen_payloads.append(payload)
        return _chat(_CLEAN_ANSWER)

    row = run_long_context_coherence_gate(
        base_url="http://localhost:8000",
        model="deepseek-ai/DeepSeek-V4-Flash",
        line_count=128,
        concurrency=2,
        repeat_count=1,
        post_func=fake_post,
    )

    assert row["ok"]
    assert row["failures"] == 0
    assert row["total_requests"] == 2
    assert all(item["recall_ok"] and item["coherence_ok"] for item in row["rows"])
    # thinking-off direct path is the default regression probe
    assert seen_payloads[0]["chat_template_kwargs"] == {"enable_thinking": False}


def test_run_gate_extra_body_overrides_thinking_default():
    seen_payloads = []

    def fake_post(base_url, path, payload, timeout, **kwargs):
        seen_payloads.append(payload)
        return _chat(_CLEAN_ANSWER)

    run_long_context_coherence_gate(
        base_url="http://localhost:8000",
        model="deepseek-ai/DeepSeek-V4-Flash",
        line_count=128,
        concurrency=1,
        repeat_count=1,
        extra_body={"chat_template_kwargs": {"enable_thinking": True}},
        post_func=fake_post,
    )

    assert seen_payloads[0]["chat_template_kwargs"] == {"enable_thinking": True}


def test_run_gate_fails_on_mixed_script_gibberish_response():
    def fake_post(base_url, path, payload, timeout, **kwargs):
        return _chat("代码是的の안녕시스템验证な코드エラー混乱한字符串の乱码検証")

    row = run_long_context_coherence_gate(
        base_url="http://localhost:8000",
        model="deepseek-ai/DeepSeek-V4-Flash",
        line_count=128,
        concurrency=2,
        repeat_count=1,
        post_func=fake_post,
    )

    assert not row["ok"]
    assert row["failures"] == row["total_requests"]
    assert all(term in _CLEAN_ANSWER for term in DEFAULT_REQUIRED_TERMS)
