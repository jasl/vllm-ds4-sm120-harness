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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.779558
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3293, "completion_tokens": 2999, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2999
- Total tokens: 3293

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

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for s in sessions:
        sid = s.get("id", "unknown")
        reasons = []
        # Check required fields
        if "start" not in s or "end" not in s or "value" not in s:
            reasons.append("missing required field(s)")
        else:
            try:
                start = parse_timestamp(s["start"])
                end = parse_timestamp(s["end"])
                if end <= start:
                    reasons.append("end not after start")
            except (ValueError, TypeError):
                reasons.append("invalid timestamp format")
            try:
                value = float(s["value"])
                if value < 0:
                    reasons.append("negative value")
            except (ValueError, TypeError):
                reasons.append("invalid value")
        if reasons:
            rejected.append({"id": sid, "reasons": reasons})
        else:
            # Keep original data plus parsed times
            valid.append({
                "id": sid,
                "start": start,
                "end": end,
                "value": value
            })
    return valid, rejected

def weighted_interval_scheduling(sessions):
    """O(n log n) DP: returns (max_value, selected_ids) or (0, [])."""
    if not sessions:
        return 0.0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Precompute p[j] = index of last non-overlapping session before j
    # Use binary search
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]

    p = [0] * n  # p[j] is index (0-based) of last non-overlapping, -1 if none
    for j in range(n):
        # Find rightmost i < j with end[i] <= start[j]
        lo, hi = 0, j - 1
        best = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_times[j]:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = best

    # DP arrays
    dp = [0.0] * n
    choice = [False] * n  # whether we take session j in optimal solution

    for j in range(n):
        # Option 1: skip session j
        skip_val = dp[j-1] if j > 0 else 0.0
        # Option 2: take session j
        take_val = sorted_sessions[j]["value"]
        if p[j] != -1:
            take_val += dp[p[j]]

        # Ties: prefer fewer sessions, then lexicographically smaller IDs
        if take_val > skip_val:
            dp[j] = take_val
            choice[j] = True
        elif take_val < skip_val:
            dp[j] = skip_val
            choice[j] = False
        else:
            # Equal value: need tie-breaking
            # Compute number of sessions and ID list for both options
            # Option take
            take_ids = []
            if p[j] != -1:
                take_ids.extend(get_optimal_ids(sorted_sessions, p, choice, p[j]))
            take_ids.append(sorted_sessions[j]["id"])
            take_count = len(take_ids)

            # Option skip
            skip_ids = get_optimal_ids(sorted_sessions, p, choice, j-1) if j > 0 else []
            skip_count = len(skip_ids)

            # Prefer fewer sessions
            if take_count < skip_count:
                dp[j] = take_val
                choice[j] = True
            elif take_count > skip_count:
                dp[j] = skip_val
                choice[j] = False
            else:
                # Same count: lexicographically smaller list
                if take_ids < skip_ids:
                    dp[j] = take_val
                    choice[j] = True
                else:
                    dp[j] = skip_val
                    choice[j] = False

    # Reconstruct optimal solution
    optimal_ids = get_optimal_ids(sorted_sessions, p, choice, n-1)
    # Convert to original order (chronological by start time, then end time)
    id_order = {s["id"]: (s["start"], s["end"]) for s in sessions}
    optimal_ids.sort(key=lambda x: (id_order[x][0], id_order[x][1]))

    return dp[n-1], optimal_ids

def get_optimal_ids(sessions, p, choice, j):
    """Recursively collect selected IDs up to index j."""
    if j < 0:
        return []
    if choice[j]:
        res = get_optimal_ids(sessions, p, choice, p[j])
        res.append(sessions[j]["id"])
        return res
    else:
        return get_optimal_ids(sessions, p, choice, j-1)

def run_tests():
    """Built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic case
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 9, f"Test 1 failed: expected 9, got {max_val}"
    assert ids == ["a", "c"], f"Test 1 failed: ids mismatch {ids}"
    assert len(rejected) == 0
    tests_passed += 1

    # Test 2: Overlapping case
    data = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 8},
            {"id": "z", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 7}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 17, f"Test 2 failed: expected 17, got {max_val}"
    assert ids == ["x", "z"], f"Test 2 failed: ids mismatch {ids}"
    tests_passed += 1

    # Test 3: Reject invalid
    data = {
        "sessions": [
            {"id": "ok", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad_end", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 3},
            {"id": "neg_val", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "no_end", "start": "2026-05-01T09:00:00", "value": 2}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    total_tests += 1
    assert len(valid) == 1 and valid[0]["id"] == "ok"
    assert len(rejected) == 3
    assert rejected[0]["id"] == "bad_end"
    assert "end not after start" in rejected[0]["reasons"]
    assert rejected[1]["id"] == "neg_val"
    assert "negative value" in rejected[1]["reasons"]
    assert rejected[2]["id"] == "no_end"
    tests_passed += 1

    # Test 4: Tie-breaking (same value, different counts)
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids = weighted_interval_scheduling(valid)
    total_tests += 1
    # Max value = 10 (a+b or a+c?) Actually a overlaps with c, b overlaps with c.
    # a+b = 10, a+c = 10 (a and c overlap? a:9-10, c:9:30-10:30 -> overlap) so only a+b possible.
    assert max_val == 10
    assert ids == ["a", "b"], f"Test 4 failed: ids mismatch {ids}"
    tests_passed += 1

    # Test 5: Another tie: same value and same count, lexicographically smaller
    data = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 10
    # Options: [a,b], [a,d], [c,b], [c,d] (but b and d same start/end? Actually overlapping not allowed)
    # a:10-11, b:9-10 can combine, c:9-10, d:10-11 can combine
    # All have count 2, value 10. Lexicographically smallest list is ["a","b"]
    assert ids == ["a", "b"], f"Test 5 failed: ids mismatch {ids}"
    tests_passed += 1

    # Test 6: Empty input
    data = {"sessions": []}
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 0 and ids == [] and len(rejected) == 0
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"error": "invalid JSON input"}))
        sys.exit(1)

    sessions = data.get("sessions", [])
    valid_sessions, rejected_sessions = validate_sessions(sessions)

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected_sessions
    }
    print(json.dumps(output, default=str))

if __name__ == "__main__":
    main()
```
````
