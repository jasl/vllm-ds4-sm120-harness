# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 46.463145
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3250, "completion_tokens": 2956, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2956
- Total tokens: 3250

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

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.strptime(ts_str, ISO_FORMAT)


def parse_sessions(data):
    """Parse sessions from input dict, return (valid_sessions, rejected_list)."""
    sessions_raw = data.get("sessions", [])
    valid = []
    rejected = []

    for idx, sess in enumerate(sessions_raw):
        sid = sess.get("id", f"index_{idx}")
        start_str = sess.get("start")
        end_str = sess.get("end")
        value = sess.get("value")
        reasons = []

        # Check presence
        if start_str is None:
            reasons.append("missing start")
        if end_str is None:
            reasons.append("missing end")
        if value is None:
            reasons.append("missing value")

        if reasons:
            rejected.append({"id": sid, "reason": "; ".join(reasons)})
            continue

        # Parse timestamps
        try:
            start = parse_timestamp(start_str)
        except (ValueError, TypeError):
            reasons.append("invalid start timestamp")

        try:
            end = parse_timestamp(end_str)
        except (ValueError, TypeError):
            reasons.append("invalid end timestamp")

        if reasons:
            rejected.append({"id": sid, "reason": "; ".join(reasons)})
            continue

        # Value check
        if not isinstance(value, (int, float)):
            rejected.append({"id": sid, "reason": "value must be a number"})
            continue

        if value < 0:
            rejected.append({"id": sid, "reason": "negative value"})
            continue

        # End must be after start
        if end <= start:
            rejected.append({"id": sid, "reason": "end not after start"})
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
    O(n log n) DP for weighted interval scheduling.
    Returns (max_value, selected_ids) with tie-breaking.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Precompute p(j): largest index i < j such that session i ends before session j starts
    end_times = [s["end"] for s in sorted_sessions]
    p = [-1] * n
    for j in range(n):
        start_j = sorted_sessions[j]["start"]
        # Find rightmost end_time < start_j
        idx = bisect_right(end_times, start_j) - 1
        # We need strict <, bisect_right gives <=, but datetime comparison works
        # Since end_times are sorted, we need end_time < start_j
        # bisect_right returns insertion point after any equals, so it's correct for <
        # Actually bisect_right finds position where end_time <= start_j, so index-1 gives last with end_time <= start_j
        # But we need < not <=. If there's equality, we want to exclude. So we need to adjust.
        # Let's use binary search manually for strict <
        lo, hi = 0, j
        while lo < hi:
            mid = (lo + hi) // 2
            if end_times[mid] < start_j:
                lo = mid + 1
            else:
                hi = mid
        p[j] = lo - 1

    # DP arrays
    dp = [0.0] * n
    choice = [None] * n  # 'take' or 'skip'

    for j in range(n):
        # Value if we take session j
        take_val = sorted_sessions[j]["value"]
        if p[j] >= 0:
            take_val += dp[p[j]]

        skip_val = dp[j-1] if j > 0 else 0.0

        # Compare with tie-breaking
        if take_val > skip_val:
            dp[j] = take_val
            choice[j] = 'take'
        elif skip_val > take_val:
            dp[j] = skip_val
            choice[j] = 'skip'
        else:
            # Equal values: choose fewer sessions, then lexicographically smaller IDs
            # Reconstruct both options to compare
            take_sessions = reconstruct(j, sorted_sessions, p, choice, 'take')
            skip_sessions = reconstruct(j, sorted_sessions, p, choice, 'skip')
            take_ids = [s["id"] for s in take_sessions]
            skip_ids = [s["id"] for s in skip_sessions]

            # Compare: fewer sessions first
            if len(take_ids) < len(skip_ids):
                dp[j] = take_val
                choice[j] = 'take'
            elif len(skip_ids) < len(take_ids):
                dp[j] = skip_val
                choice[j] = 'skip'
            else:
                # Same length: lexicographically smaller list of IDs
                if sorted(take_ids) < sorted(skip_ids):
                    dp[j] = take_val
                    choice[j] = 'take'
                else:
                    dp[j] = skip_val
                    choice[j] = 'skip'

    # Reconstruct optimal from full array
    selected = reconstruct(n-1, sorted_sessions, p, choice, None)
    selected_ids = [s["id"] for s in selected]

    return dp[-1], selected_ids


def reconstruct(j, sessions, p, choice, override):
    """Helper to reconstruct solution up to index j."""
    result = []
    while j >= 0:
        if override is not None:
            dec = override
            override = None
        else:
            dec = choice[j]

        if dec == 'take':
            result.append(sessions[j])
            j = p[j]
        else:
            j -= 1
    result.reverse()
    return result


def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic example
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 8},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 6}
        ]
    }
    total_tests += 1
    valid, rejected = parse_sessions(data)
    max_val, ids = weighted_interval_scheduling(valid)
    assert max_val == 11, f"Expected 11, got {max_val}"
    assert ids == ["a", "c"] or ids == ["b"], f"Unexpected ids {ids}"
    assert len(rejected) == 0
    tests_passed += 1

    # Test 2: Empty
    data = {"sessions": []}
    valid, rejected = parse_sessions(data)
    max_val, ids = weighted_interval_scheduling(valid)
    assert max_val == 0 and ids == []
    assert len(rejected) == 0
    tests_passed += 1

    # Test 3: Reject invalid
    data = {
        "sessions": [
            {"id": "x", "start": "invalid", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]
    }
    valid, rejected = parse_sessions(data)
    assert len(valid) == 0
    assert len(rejected) == 3
    total_tests += 1
    tests_passed += 1

    # Test 4: Tie-breaking - equal values
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    valid, rejected = parse_sessions(data)
    max_val, ids = weighted_interval_scheduling(valid)
    # Two possibilities: [a] or [b] (same value, same count, lexicographic: a < b)
    assert max_val == 10 and ids == ["a"], f"Got {ids}"
    total_tests += 1
    tests_passed += 1

    # Test 5: Tie-breaking - fewer sessions
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:30:00", "value": 10}
        ]
    }
    valid, rejected = parse_sessions(data)
    max_val, ids = weighted_interval_scheduling(valid)
    # [c] value 10 vs [a,b] value 10, [c] has fewer sessions
    assert max_val == 10 and ids == ["c"], f"Got {ids}"
    total_tests += 1
    tests_passed += 1

    # Test 6: Complex overlapping
    data = {
        "sessions": [
            {"id": "1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 2},
            {"id": "2", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 3},
            {"id": "3", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4},
            {"id": "4", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 3}
        ]
    }
    valid, rejected = parse_sessions(data)
    max_val, ids = weighted_interval_scheduling(valid)
    # Best: [1,3] = 6 or [2,4] = 6, but [1,3] has fewer? same count, lexicographic: [1,3] vs [2,4] -> [1,3]
    assert max_val == 6 and ids == ["1", "3"], f"Got {ids}"
    total_tests += 1
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed.", file=sys.stderr)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    valid_sessions, rejected = parse_sessions(data)

    if not valid_sessions:
        result = {
            "max_value": 0,
            "selected_ids": [],
            "rejected": rejected
        }
        print(json.dumps(result, default=str))
        return

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    # Ensure integer output if values are integers
    if isinstance(max_value, float) and max_value.is_integer():
        max_value = int(max_value)

    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

    print(json.dumps(result, default=str))


if __name__ == "__main__":
    main()
```
````
