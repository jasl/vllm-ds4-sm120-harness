#!/usr/bin/env python3
"""schedule_optimizer.py - Weighted interval scheduling with reconstruction."""

import sys
import json
from datetime import datetime
from bisect import bisect_right

def parse_timestamp(s: str):
    """Parse ISO 8601 timestamp without timezone info using stdlib."""
    return datetime.fromisoformat(s)

def solve(sessions_data: dict):
    """Given input dict with 'sessions' list, return result dict."""
    rejected = []
    valid = []
    for sess in sessions_data.get("sessions", []):
        sid = sess.get("id")
        # Validate fields existence
        if not all(k in sess for k in ("id", "start", "end", "value")):
            rejected.append({"id": sid, "reason": "Missing required fields"})
            continue
        try:
            start = parse_timestamp(sess["start"])
            end = parse_timestamp(sess["end"])
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue
        value = sess["value"]
        if not isinstance(value, (int, float)):
            rejected.append({"id": sid, "reason": "Value must be a number"})
            continue
        if value < 0:
            rejected.append({"id": sid, "reason": "Value cannot be negative"})
            continue
        if end <= start:
            rejected.append({"id": sid, "reason": "End time must be after start time"})
            continue
        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })
    if not valid:
        return {
            "max_value": 0,
            "selected_ids": [],
            "rejected": rejected
        }

    # Sort by end time, then start, then id for deterministic ordering
    valid.sort(key=lambda x: (x["end"], x["start"], x["id"]))
    n = len(valid)
    end_times = [s["end"] for s in valid]
    start_times = [s["start"] for s in valid]
    values = [s["value"] for s in valid]
    ids = [s["id"] for s in valid]

    # Compute p[i]: last index j such that end[j] <= start[i]
    p = []
    for start in start_times:
        # bisect_right returns insertion point after equal elements
        idx = bisect_right(end_times, start) - 1
        p.append(idx)

    # DP arrays storing best (value, count, ids_tuple)
    best_value = [0.0] * n
    best_count = [0] * n
    best_ids = [()] * n  # tuples of IDs in chronological order

    for i in range(n):
        # Option 1: skip session i
        if i > 0:
            skip_value = best_value[i-1]
            skip_count = best_count[i-1]
            skip_ids = best_ids[i-1]
        else:
            skip_value = 0.0
            skip_count = 0
            skip_ids = ()

        # Option 2: include session i
        prev = p[i]
        if prev >= 0:
            inc_value = values[i] + best_value[prev]
            inc_count = best_count[prev] + 1
            inc_ids = best_ids[prev] + (ids[i],)
        else:
            inc_value = values[i]
            inc_count = 1
            inc_ids = (ids[i],)

        # Compare: maximize value, then minimize count, then lexicographically smaller ids
        # Use tuple (-value, count, ids) -> lower is better
        inc_tuple = (-inc_value, inc_count, inc_ids)
        skip_tuple = (-skip_value, skip_count, skip_ids)
        if inc_tuple < skip_tuple:
            best_value[i] = inc_value
            best_count[i] = inc_count
            best_ids[i] = inc_ids
        else:
            best_value[i] = skip_value
            best_count[i] = skip_count
            best_ids[i] = skip_ids

    # Result
    return {
        "max_value": best_value[n-1],
        "selected_ids": list(best_ids[n-1]),
        "rejected": rejected
    }

def run_tests():
    """Run built-in tests and print success message."""
    tests = []

    # Test 1: basic case
    tests.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 10},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
            ]
        },
        "expected": {
            "max_value": 10,
            "selected_ids": ["b"],
            "rejected": []
        }
    })

    # Test 2: overlapping intervals - choose the better combination
    tests.append({
        "input": {
            "sessions": [
                {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 8},
                {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 6},
                {"id": "z", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 5}
            ]
        },
        "expected": {
            "max_value": 13,
            "selected_ids": ["x", "z"],
            "rejected": []
        }
    })

    # Test 3: tie-breaking - fewer sessions preferred
    tests.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 5}
            ]
        },
        "expected": {
            "max_value": 10,
            "selected_ids": ["a"],
            "rejected": []
        }
    })

    # Test 4: tie-breaking - same value and count, lexicographically smaller list
    tests.append({
        "input": {
            "sessions": [
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
            ]
        },
        "expected": {
            "max_value": 10,
            "selected_ids": ["a"],
            "rejected": []
        }
    })

    # Test 5: lexicographic tie when multiple solutions with same value and count
    tests.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 4},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 8}
            ]
        },
        "expected": {
            "max_value": 8,
            "selected_ids": ["c"],
            "rejected": []
        }
    })

    # Test 6: rejections
    tests.append({
        "input": {
            "sessions": [
                {"id": "ok", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1},
                {"id": "bad_time", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 1},
                {"id": "neg_val", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
            ]
        },
        "expected": {
            "max_value": 1,
            "selected_ids": ["ok"],
            "rejected": [
                {"id": "bad_time", "reason": "End time must be after start time"},
                {"id": "neg_val", "reason": "Value cannot be negative"}
            ]
        }
    })

    # Test 7: empty input
    tests.append({
        "input": {"sessions": []},
        "expected": {
            "max_value": 0,
            "selected_ids": [],
            "rejected": []
        }
    })

    # Test 8: all rejected
    tests.append({
        "input": {
            "sessions": [
                {"id": "x", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
            ]
        },
        "expected": {
            "max_value": 0,
            "selected_ids": [],
            "rejected": [{"id": "x", "reason": "End time must be after start time"}]
        }
    })

    for i, test in enumerate(tests, 1):
        result = solve(test["input"])
        # Compare carefully
        assert result["max_value"] == test["expected"]["max_value"], f"Test {i} failed: max_value mismatch"
        assert result["selected_ids"] == test["expected"]["selected_ids"], f"Test {i} failed: selected_ids mismatch"
        # We need to compare rejected lists irrespective of order? Assume same order as input processing, should match.
        assert result["rejected"] == test["expected"]["rejected"], f"Test {i} failed: rejected mismatch\nGot: {result['rejected']}\nExpected: {test['expected']['rejected']}"
    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return
    data = json.load(sys.stdin)
    result = solve(data)
    # Output compact JSON with no extra whitespace
    print(json.dumps(result, ensure_ascii=False, separators=(',', ':')))

if __name__ == "__main__":
    main()
