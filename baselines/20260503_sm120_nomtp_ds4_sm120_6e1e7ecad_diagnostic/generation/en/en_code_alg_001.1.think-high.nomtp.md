# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 42.41377
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2995, "completion_tokens": 2701, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2701
- Total tokens: 2995

## Prompt

```markdown
Write a single-file Python 3 command-line program named `schedule_optimizer.py`. Use no third-party packages. Keep the code under 1,000 lines.

Problem: Given a list of candidate work sessions, choose a non-overlapping subset that maximizes total value. Each session has an ID, start time, end time, and value. This is weighted interval scheduling with reconstruction.

Input: read JSON from standard input. Format:
{
  "sessions": [
    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}
  ]
}

Requirements:
1. Parse ISO-like timestamps without time zones using Python standard library.
2. Reject sessions whose end is not after start or whose value is negative.
3. Output JSON with `max_value`, `selected_ids` in chronological order, and `rejected` entries with reasons.
4. If multiple optimal solutions exist, choose the one with fewer sessions; if still tied, choose lexicographically smaller list of IDs.
5. Include an efficient O(n log n) dynamic programming solution.
6. Include built-in tests. When run with `--test`, execute tests and print a short success message. Normal mode should print only JSON.

Output only the complete Python code. Do not include explanations.
```

## Assistant

````markdown
```python
#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from bisect import bisect_right

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get("id", "unknown")
        reasons = []

        # Check required fields
        if "start" not in sess or "end" not in sess:
            reasons.append("missing start or end")
        if "value" not in sess:
            reasons.append("missing value")

        if reasons:
            rejected.append({"id": sid, "reasons": reasons})
            continue

        try:
            start = parse_timestamp(sess["start"])
            end = parse_timestamp(sess["end"])
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reasons": ["invalid timestamp format"]})
            continue

        # Check value
        value = sess["value"]
        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({"id": sid, "reasons": ["value is negative or not a number"]})
            continue

        # Check end > start
        if end <= start:
            rejected.append({"id": sid, "reasons": ["end not after start"]})
            continue

        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })

    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    Weighted interval scheduling with O(n log n) DP.
    Returns (max_value, selected_ids_chronological).
    If multiple optimal solutions, pick fewest sessions, then lexicographically smallest IDs.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Precompute p(j) = last non-overlapping session index
    end_times = [s["end"] for s in sorted_sessions]
    p = [-1] * n
    for i in range(n):
        start_i = sorted_sessions[i]["start"]
        # Binary search for last end_time <= start_i
        idx = bisect_right(end_times, start_i) - 1
        p[i] = idx

    # DP arrays: dp[j] = max value considering first j+1 sessions
    # We'll store (value, session_count, list_of_ids) for tie-breaking
    dp = [(0, 0, [])] * (n + 1)  # dp[0] = (0, 0, [])

    for j in range(1, n + 1):
        # Option 1: exclude session j-1
        exclude = dp[j-1]

        # Option 2: include session j-1
        include_val = sorted_sessions[j-1]["value"]
        include_count = 1
        include_ids = [sorted_sessions[j-1]["id"]]

        if p[j-1] != -1:
            prev = dp[p[j-1] + 1]
            include_val += prev[0]
            include_count += prev[1]
            include_ids = prev[2] + include_ids  # chronological order since p is earlier

        # Compare: maximize value, then minimize session count, then lexicographic IDs
        best = None
        for candidate in [exclude, (include_val, include_count, include_ids)]:
            if best is None:
                best = candidate
            else:
                # Compare value
                if candidate[0] > best[0]:
                    best = candidate
                elif candidate[0] == best[0]:
                    # Fewer sessions
                    if candidate[1] < best[1]:
                        best = candidate
                    elif candidate[1] == best[1]:
                        # Lexicographically smaller IDs
                        if candidate[2] < best[2]:
                            best = candidate
        dp[j] = best

    max_val, _, ids = dp[n]
    return max_val, ids

def solve(input_data):
    """Main solver function."""
    sessions = input_data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)
    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    return output

# ---------- Tests ----------
def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    def check(name, input_data, expected_output):
        nonlocal tests_passed, total_tests
        total_tests += 1
        result = solve(input_data)
        # Compare ignoring order of rejected if present
        ok = True
        for key in expected_output:
            if key == "rejected":
                # Compare as sets of dicts (order independent)
                exp_set = frozenset((d["id"], tuple(d.get("reasons", []))) for d in expected_output[key])
                res_set = frozenset((d["id"], tuple(d.get("reasons", []))) for d in result[key])
                if exp_set != res_set:
                    ok = False
                    break
            else:
                if result[key] != expected_output[key]:
                    ok = False
                    break
        if ok:
            tests_passed += 1
        else:
            print(f"FAIL: {name}")
            print(f"  Expected: {expected_output}")
            print(f"  Got: {result}")

    # Test 1: empty sessions
    check("empty sessions", {"sessions": []}, {"max_value": 0, "selected_ids": [], "rejected": []})

    # Test 2: single valid session
    check("single valid", {
        "sessions": [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}]
    }, {"max_value": 5, "selected_ids": ["a"], "rejected": []})

    # Test 3: two non-overlapping sessions
    check("two non-overlapping", {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4}
        ]
    }, {"max_value": 7, "selected_ids": ["a", "b"], "rejected": []})

    # Test 4: overlapping - must choose one
    check("overlapping", {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 6}
        ]
    }, {"max_value": 6, "selected_ids": ["b"], "rejected": []})

    # Test 5: tie-breaking - same value, fewer sessions
    check("tie fewer sessions", {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }, {"max_value": 5, "selected_ids": ["a"], "rejected": []})  # single session vs two sessions

    # Test 6: tie-breaking - same value, same count, lexicographic
    check("tie lexicographic", {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }, {"max_value": 5, "selected_ids": ["a"], "rejected": []})

    # Test 7: rejected sessions
    check("rejected", {
        "sessions": [
            {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1},
            {"id": "bad1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 1},
            {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "bad3", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 1}
        ]
    }, {
        "max_value": 1,
        "selected_ids": ["good"],
        "rejected": [
            {"id": "bad1", "reasons": ["end not after start"]},
            {"id": "bad2", "reasons": ["value is negative or not a number"]},
            {"id": "bad3", "reasons": ["invalid timestamp format"]}
        ]
    })

    # Test 8: complex scenario - weighted interval scheduling classic
    check("complex", {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 2},
            {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 4},
            {"id": "d", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:30:00", "value": 3}
        ]
    }, {"max_value": 7, "selected_ids": ["a", "c"], "rejected": []})  # a+c=6, b=5, a+d=5, c=4, d=3

    print(f"All {tests_passed}/{total_tests} tests passed.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        input_data = json.load(sys.stdin)
        output = solve(input_data)
        print(json.dumps(output, indent=2))
```
````
