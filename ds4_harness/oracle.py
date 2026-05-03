from __future__ import annotations

import copy
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


Json = dict[str, Any]


@dataclass(frozen=True)
class OracleCase:
    name: str
    path: str
    request: Json
    response: Json


def token_ids_from_tokenize_response(response: Json | None) -> list[int] | None:
    if not isinstance(response, dict):
        return None
    raw_tokens = response.get("tokens")
    if raw_tokens is None:
        raw_tokens = response.get("token_ids")
    if not isinstance(raw_tokens, list):
        return None
    try:
        return [int(token) for token in raw_tokens]
    except (TypeError, ValueError):
        return None


def attach_prompt_token_ids(response: Json, token_ids: list[int] | None) -> Json:
    if not token_ids:
        return response
    output = copy.deepcopy(response)
    choices = output.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        return output
    choices[0]["prompt_token_ids"] = token_ids
    return output


def _choice(response: Json) -> Json:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("response has no choices[0]")
    choice = choices[0]
    if not isinstance(choice, dict):
        raise ValueError("response choices[0] is not an object")
    return choice


def _token_key(token: Any) -> str:
    if isinstance(token, str):
        return token
    if isinstance(token, int):
        return f"token_id:{token}"
    return str(token)


def _generated_tokens(response: Json) -> list[str]:
    choice = _choice(response)
    logprobs = choice.get("logprobs") or {}
    tokens = logprobs.get("tokens")
    if isinstance(tokens, list) and tokens:
        return [_token_key(token) for token in tokens]
    token_ids = choice.get("token_ids")
    if isinstance(token_ids, list):
        return [_token_key(token) for token in token_ids]
    return []


def _prompt_token_ids(response: Json) -> list[int] | None:
    token_ids = _choice(response).get("prompt_token_ids")
    if not isinstance(token_ids, list):
        return None
    return [int(token) for token in token_ids]


def _token_logprobs(response: Json) -> list[float | None]:
    logprobs = _choice(response).get("logprobs") or {}
    values = logprobs.get("token_logprobs")
    if not isinstance(values, list):
        return []
    return [float(value) if value is not None else None for value in values]


def _top_logprobs(response: Json) -> list[dict[str, float]]:
    logprobs = _choice(response).get("logprobs") or {}
    values = logprobs.get("top_logprobs")
    if not isinstance(values, list):
        return []
    out: list[dict[str, float]] = []
    for step in values:
        if not isinstance(step, dict):
            out.append({})
            continue
        out.append({_token_key(token): float(logprob) for token, logprob in step.items()})
    return out


def generated_tokens(response: Json) -> list[str]:
    return _generated_tokens(response)


def _first_mismatch(oracle_tokens: list[str], actual_tokens: list[str]) -> Json | None:
    for step, (oracle_token, actual_token) in enumerate(
        zip(oracle_tokens, actual_tokens)
    ):
        if oracle_token != actual_token:
            return {"step": step, "oracle": oracle_token, "actual": actual_token}
    if len(oracle_tokens) != len(actual_tokens):
        step = min(len(oracle_tokens), len(actual_tokens))
        return {
            "step": step,
            "oracle": oracle_tokens[step] if step < len(oracle_tokens) else None,
            "actual": actual_tokens[step] if step < len(actual_tokens) else None,
        }
    return None


def _matching_prefix(oracle_tokens: list[str], actual_tokens: list[str]) -> int:
    count = 0
    for oracle_token, actual_token in zip(oracle_tokens, actual_tokens):
        if oracle_token != actual_token:
            break
        count += 1
    return count


def _top_keys(top_logprobs: dict[str, float], top_n: int) -> list[str]:
    return list(top_logprobs.keys())[:top_n]


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _rank(token: str | None, keys: list[str]) -> int | None:
    if token is None:
        return None
    try:
        return keys.index(token) + 1
    except ValueError:
        return None


def _top1_margins(top_logprobs: list[dict[str, float]]) -> list[float | None]:
    margins: list[float | None] = []
    for step in top_logprobs:
        values = list(step.values())
        if len(values) < 2:
            margins.append(None)
            continue
        margins.append(values[0] - values[1])
    return margins


def _known_values(values: list[float | None]) -> list[float]:
    return [value for value in values if value is not None]


def _margin_at(margins: list[float | None], step: int | None) -> float | None:
    if step is None or step >= len(margins):
        return None
    return margins[step]


def _is_low_margin(
    oracle_margin: float | None,
    actual_margin: float | None,
    threshold: float | None,
) -> bool | None:
    if threshold is None:
        return None
    known = [margin for margin in (oracle_margin, actual_margin) if margin is not None]
    if not known:
        return False
    return min(known) <= threshold


def _topk_overlap_at(
    oracle_top: list[dict[str, float]],
    actual_top: list[dict[str, float]],
    *,
    step: int | None,
    top_n: int,
) -> float | None:
    if step is None or step >= len(oracle_top) or step >= len(actual_top):
        return None
    oracle_set = set(_top_keys(oracle_top[step], top_n))
    actual_set = set(_top_keys(actual_top[step], top_n))
    if not oracle_set:
        return None
    return len(oracle_set & actual_set) / len(oracle_set)


def _count_items_in_first_seen_order(values: list[Any]) -> list[Json]:
    counts = Counter(values)
    seen = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return [{"value": value, "count": counts[value]} for value in seen]


def summarize_stability_records(case_name: str, records: list[Json]) -> Json:
    token_sequences = [tuple(record.get("actual_tokens", [])) for record in records]
    sequence_counts = _count_items_in_first_seen_order(token_sequences)
    first_tokens = [
        sequence[0] if sequence else None
        for sequence in token_sequences
    ]
    first_token_counts = _count_items_in_first_seen_order(first_tokens)
    mismatch_records = [
        record
        for record in records
        if record.get("tokens_match") is False and "error" not in record
    ]
    low_margin_mismatches = [
        record
        for record in mismatch_records
        if record.get("first_token_mismatch_low_margin") is True
    ]
    high_margin_mismatches = [
        record
        for record in mismatch_records
        if record.get("first_token_mismatch_low_margin") is not True
    ]
    return {
        "case": case_name,
        "rounds": len(records),
        "stable_token_sequence": len(sequence_counts) <= 1,
        "unique_token_sequences": len(sequence_counts),
        "token_sequence_counts": [
            {"tokens": list(item["value"]), "count": item["count"]}
            for item in sequence_counts
        ],
        "first_token_counts": [
            {"token": item["value"], "count": item["count"]}
            for item in first_token_counts
        ],
        "exact_token_match_rounds": sum(
            1 for record in records if record.get("tokens_match") is True
        ),
        "low_margin_mismatch_rounds": len(low_margin_mismatches),
        "high_margin_mismatch_rounds": len(high_margin_mismatches),
        "error_rounds": sum(1 for record in records if "error" in record),
    }


def compare_response(
    case_name: str,
    oracle_response: Json,
    actual_response: Json,
    *,
    top_n: int = 50,
    low_margin_threshold: float | None = None,
) -> Json:
    oracle_tokens = _generated_tokens(oracle_response)
    actual_tokens = _generated_tokens(actual_response)
    oracle_top = _top_logprobs(oracle_response)
    actual_top = _top_logprobs(actual_response)
    oracle_token_logprobs = _token_logprobs(oracle_response)
    actual_token_logprobs = _token_logprobs(actual_response)
    oracle_margins = _top1_margins(oracle_top)
    actual_margins = _top1_margins(actual_top)

    steps = min(
        len(oracle_tokens), len(actual_tokens), len(oracle_top), len(actual_top)
    )
    top1_matches = 0
    topk_overlaps: list[float] = []
    common_logprob_errors: list[float] = []
    chosen_token_logprob_errors: list[float] = []

    for step in range(steps):
        oracle_keys = _top_keys(oracle_top[step], top_n)
        actual_keys = _top_keys(actual_top[step], top_n)
        if oracle_keys and actual_keys and oracle_keys[0] == actual_keys[0]:
            top1_matches += 1

        oracle_set = set(oracle_keys)
        actual_set = set(actual_keys)
        if oracle_set:
            topk_overlaps.append(len(oracle_set & actual_set) / len(oracle_set))
        for token in oracle_set & actual_set:
            common_logprob_errors.append(
                abs(oracle_top[step][token] - actual_top[step][token])
            )

        if (
            oracle_tokens[step] == actual_tokens[step]
            and step < len(oracle_token_logprobs)
            and step < len(actual_token_logprobs)
            and oracle_token_logprobs[step] is not None
            and actual_token_logprobs[step] is not None
        ):
            chosen_token_logprob_errors.append(
                abs(oracle_token_logprobs[step] - actual_token_logprobs[step])
            )

    oracle_prompt_ids = _prompt_token_ids(oracle_response)
    actual_prompt_ids = _prompt_token_ids(actual_response)
    prompt_ids_match = (
        None
        if oracle_prompt_ids is None or actual_prompt_ids is None
        else oracle_prompt_ids == actual_prompt_ids
    )

    first_mismatch = _first_mismatch(oracle_tokens, actual_tokens)
    mismatch_step = (
        int(first_mismatch["step"])
        if first_mismatch is not None and isinstance(first_mismatch.get("step"), int)
        else None
    )
    mismatch_oracle_keys = (
        _top_keys(oracle_top[mismatch_step], top_n)
        if mismatch_step is not None and mismatch_step < len(oracle_top)
        else []
    )
    mismatch_actual_keys = (
        _top_keys(actual_top[mismatch_step], top_n)
        if mismatch_step is not None and mismatch_step < len(actual_top)
        else []
    )
    mismatch_oracle_margin = _margin_at(oracle_margins, mismatch_step)
    mismatch_actual_margin = _margin_at(actual_margins, mismatch_step)
    first_mismatch_low_margin = _is_low_margin(
        mismatch_oracle_margin,
        mismatch_actual_margin,
        low_margin_threshold,
    )
    trajectory_stopped_at_low_margin_fork = (
        first_mismatch is not None and first_mismatch_low_margin is True
    )
    trajectory_steps = (
        min(steps, mismatch_step)
        if trajectory_stopped_at_low_margin_fork and mismatch_step is not None
        else steps
    )
    trajectory_top1_matches = 0
    trajectory_topk_overlaps: list[float] = []

    for step in range(trajectory_steps):
        oracle_keys = _top_keys(oracle_top[step], top_n)
        actual_keys = _top_keys(actual_top[step], top_n)
        if oracle_keys and actual_keys and oracle_keys[0] == actual_keys[0]:
            trajectory_top1_matches += 1

        oracle_set = set(oracle_keys)
        actual_set = set(actual_keys)
        if oracle_set:
            trajectory_topk_overlaps.append(
                len(oracle_set & actual_set) / len(oracle_set)
            )

    known_oracle_margins = _known_values(oracle_margins)
    known_actual_margins = _known_values(actual_margins)
    return {
        "case": case_name,
        "tokens_match": first_mismatch is None,
        "prompt_token_ids_match": prompt_ids_match,
        "first_token_mismatch": first_mismatch,
        "first_token_mismatch_oracle_top1_margin": mismatch_oracle_margin,
        "first_token_mismatch_actual_top1_margin": mismatch_actual_margin,
        "first_token_mismatch_oracle_actual_rank": _rank(
            first_mismatch.get("actual") if first_mismatch else None,
            mismatch_oracle_keys,
        ),
        "first_token_mismatch_actual_oracle_rank": _rank(
            first_mismatch.get("oracle") if first_mismatch else None,
            mismatch_actual_keys,
        ),
        "first_token_mismatch_topk_overlap": _topk_overlap_at(
            oracle_top,
            actual_top,
            step=mismatch_step,
            top_n=top_n,
        ),
        "first_token_mismatch_low_margin": first_mismatch_low_margin,
        "matching_prefix_tokens": _matching_prefix(oracle_tokens, actual_tokens),
        "oracle_token_count": len(oracle_tokens),
        "actual_token_count": len(actual_tokens),
        "compared_steps": steps,
        "top1_matches": top1_matches,
        "top1_match_rate": top1_matches / steps if steps else None,
        "topk_overlap_mean": _mean(topk_overlaps),
        "topk_overlap_min": min(topk_overlaps) if topk_overlaps else None,
        "trajectory_stopped_at_low_margin_fork": (
            trajectory_stopped_at_low_margin_fork
        ),
        "trajectory_stop_step": (
            mismatch_step if trajectory_stopped_at_low_margin_fork else None
        ),
        "trajectory_compared_steps": trajectory_steps,
        "trajectory_top1_matches": trajectory_top1_matches,
        "trajectory_top1_match_rate": (
            trajectory_top1_matches / trajectory_steps
            if trajectory_steps
            else None
        ),
        "trajectory_topk_overlap_mean": _mean(trajectory_topk_overlaps),
        "trajectory_topk_overlap_min": (
            min(trajectory_topk_overlaps) if trajectory_topk_overlaps else None
        ),
        "oracle_top1_margin_mean": _mean(known_oracle_margins),
        "oracle_top1_margin_min": (
            min(known_oracle_margins) if known_oracle_margins else None
        ),
        "actual_top1_margin_mean": _mean(known_actual_margins),
        "actual_top1_margin_min": (
            min(known_actual_margins) if known_actual_margins else None
        ),
        "max_common_logprob_abs_error": (
            max(common_logprob_errors) if common_logprob_errors else None
        ),
        "mean_common_logprob_abs_error": _mean(common_logprob_errors),
        "max_chosen_token_logprob_abs_error": (
            max(chosen_token_logprob_errors) if chosen_token_logprob_errors else None
        ),
        "mean_chosen_token_logprob_abs_error": _mean(chosen_token_logprob_errors),
    }


def load_json(path: Path) -> Json:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def _load_request_response_pairs(oracle_dir: Path) -> list[OracleCase]:
    cases: list[OracleCase] = []
    request_paths = sorted(oracle_dir.glob("request_*.json"))
    for request_path in request_paths:
        suffix = request_path.stem.removeprefix("request_")
        response_path = oracle_dir / f"response_{suffix}.json"
        if not response_path.exists():
            raise ValueError(f"missing {response_path.name} for {request_path.name}")
        response = load_json(response_path)
        tokenize_path = oracle_dir / f"tokenize_{suffix}.json"
        if tokenize_path.exists():
            response = attach_prompt_token_ids(
                response,
                token_ids_from_tokenize_response(load_json(tokenize_path)),
            )
        cases.append(
            OracleCase(
                name=suffix,
                path="/v1/completions",
                request=load_json(request_path),
                response=response,
            )
        )
    return cases


def _load_wrapped_completion_cases(oracle_dir: Path) -> list[OracleCase]:
    cases: list[OracleCase] = []
    for path in sorted(oracle_dir.glob("*.json")):
        if path.name.startswith(("request_", "response_", "tokenize_")):
            continue
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            continue
        request = data.get("request")
        response = data.get("response")
        endpoint = data.get("path")
        if not isinstance(request, dict) or not isinstance(response, dict):
            continue
        if endpoint != "/v1/completions":
            continue
        response = attach_prompt_token_ids(
            response,
            token_ids_from_tokenize_response(data.get("tokenize_response")),
        )
        cases.append(
            OracleCase(
                name=str(data.get("name") or path.stem),
                path=endpoint,
                request=request,
                response=response,
            )
        )
    return cases


def load_oracle_cases(oracle_dir: Path) -> list[OracleCase]:
    cases = _load_request_response_pairs(oracle_dir)
    cases.extend(_load_wrapped_completion_cases(oracle_dir))
    if not cases:
        raise ValueError(
            f"{oracle_dir} has no completion oracle cases; expected "
            "request_*.json/response_*.json pairs or wrapped completion_*.json files"
        )
    return cases
