# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.373927
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3203, "completion_tokens": 2909, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2909
- Total tokens: 3203

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
import sys
import json
from datetime import datetime
from bisect import bisect_left

def parse_timestamp(ts_str):
    """Parse ISO timestamp without timezone info."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions, return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get("id", "unknown")
        if "start" not in sess or "end" not in sess or "value" not in sess:
            rejected.append({"id": sid, "reason": "Missing required field"})
            continue
        try:
            start = parse_timestamp(sess["start"])
            end = parse_timestamp(sess["end"])
        except Exception:
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue
        if end <= start:
            rejected.append({"id": sid, "reason": "End must be after start"})
            continue
        value = sess["value"]
        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({"id": sid, "reason": "Value must be non-negative"})
            continue
        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })
    return valid, rejected

def solve_weighted_interval_scheduling(sessions):
    """
    Weighted interval scheduling with tie-breaking:
    - Maximum total value
    - Fewest sessions
    - Lexicographically smallest IDs (list sorted chronologically)
    Returns (max_value, selected_ids)
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Precompute p: index of last session that ends before current starts
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]
    p = [-1] * n
    for i in range(n):
        # Binary search for rightmost end_time < start_times[i]
        lo, hi = 0, i
        while lo < hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_times[i]:
                lo = mid + 1
            else:
                hi = mid
        p[i] = lo - 1  # index of last non-overlapping

    # DP arrays
    dp = [0] * n          # max value up to i
    count = [0] * n       # number of sessions used for dp[i]
    choice = [False] * n  # whether session i is selected in optimal

    for i in range(n):
        # Option 1: exclude session i
        if i > 0:
            dp[i] = dp[i-1]
            count[i] = count[i-1]
            choice[i] = False
        else:
            dp[i] = 0
            count[i] = 0
            choice[i] = False

        # Option 2: include session i
        inc_val = sorted_sessions[i]["value"]
        inc_cnt = 1
        if p[i] != -1:
            inc_val += dp[p[i]]
            inc_cnt += count[p[i]]

        # Compare: higher value first, then fewer sessions, then lexicographic
        better = False
        if inc_val > dp[i]:
            better = True
        elif inc_val == dp[i]:
            if inc_cnt < count[i]:
                better = True
            elif inc_cnt == count[i]:
                # Lexicographic comparison: need to reconstruct ID lists
                # We compute both candidate ID lists and compare
                pass  # handled below

        if inc_val > dp[i] or (inc_val == dp[i] and inc_cnt < count[i]):
            better = True

        if inc_val == dp[i] and inc_cnt == count[i]:
            # Tie-breaking: choose lexicographically smaller list of IDs
            # Reconstruct both sequences to compare
            ids_exclude = reconstruct_ids(sorted_sessions, dp, choice, i-1 if i>0 else -1)
            ids_include = [sorted_sessions[i]["id"]]
            if p[i] != -1:
                ids_include = reconstruct_ids(sorted_sessions, dp, choice, p[i]) + ids_include
            # Compare lexicographically
            if ids_include < ids_exclude:
                better = True

        if better:
            dp[i] = inc_val
            count[i] = inc_cnt
            choice[i] = True

    # Reconstruct selected IDs in chronological order
    selected_ids = reconstruct_ids(sorted_sessions, dp, choice, n-1)

    return dp[-1] if n > 0 else 0, selected_ids

def reconstruct_ids(sorted_sessions, dp, choice, idx):
    """Reconstruct selected IDs up to index idx (inclusive)."""
    ids = []
    i = idx
    while i >= 0:
        if choice[i]:
            ids.append(sorted_sessions[i]["id"])
            # Find p[i]
            start = sorted_sessions[i]["start"]
            # Binary search
            lo, hi = 0, i
            while lo < hi:
                mid = (lo + hi) // 2
                if sorted_sessions[mid]["end"] <= start:
                    lo = mid + 1
                else:
                    hi = mid
            i = lo - 1
        else:
            i -= 1
    ids.reverse()  # chronological order
    return ids

def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic case
    total_tests += 1
    sessions = [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}
    ]
    valid, rejected = validate_sessions(sessions)
    max_val, ids = solve_weighted_interval_scheduling(valid)
    assert max_val == 15 and ids == ["a", "b"] and rejected == [], f"Test 1 failed: {max_val}, {ids}, {rejected}"
    tests_passed += 1

    # Test 2: Overlapping sessions
    total_tests += 1
    sessions = [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 10}
    ]
    valid, rejected = validate_sessions(sessions)
    max_val, ids = solve_weighted_interval_scheduling(valid)
    assert max_val == 10 and ids == ["b"], f"Test 2 failed: {max_val}, {ids}"
    tests_passed += 1

    # Test 3: Reject invalid
    total_tests += 1
    sessions = [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -1}
    ]
    valid, rejected = validate_sessions(sessions)
    assert len(valid) == 0 and len(rejected) == 2, f"Test 3 failed: {len(valid)}, {len(rejected)}"
    tests_passed += 1

    # Test 4: Tie-breaking - equal value, different count
    total_tests += 1
    sessions = [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
    ]
    valid, rejected = validate_sessions(sessions)
    max_val, ids = solve_weighted_interval_scheduling(valid)
    # Two sessions [a,b] = 10, one session [c] = 10 -> fewer sessions wins -> [c]
    assert max_val == 10 and ids == ["c"], f"Test 4 failed: {max_val}, {ids}"
    tests_passed += 1

    # Test 5: Tie-breaking - equal value, equal count, lexicographic
    total_tests += 1
    sessions = [
        {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
    ]
    valid, rejected = validate_sessions(sessions)
    max_val, ids = solve_weighted_interval_scheduling(valid)
    # Two non-overlapping sessions, both value 5, total 10
    # [a, b] vs [b, a] -> lexicographically smaller is [a, b] (since a < b)
    assert max_val == 10 and ids == ["a", "b"], f"Test 5 failed: {max_val}, {ids}"
    tests_passed += 1

    # Test 6: Empty input
    total_tests += 1
    valid, rejected = validate_sessions([])
    max_val, ids = solve_weighted_interval_scheduling(valid)
    assert max_val == 0 and ids == [] and rejected == [], f"Test 6 failed"
    tests_passed += 1

    # Test 7: Complex overlapping with many sessions
    total_tests += 1
    sessions = [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 8},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 7},
        {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 6},
        {"id": "d", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 9}
    ]
    valid, rejected = validate_sessions(sessions)
    max_val, ids = solve_weighted_interval_scheduling(valid)
    # Options: a(8)+c(6)=14, b(7)+d(9)=16, a+d(17), d alone(9) etc.
    assert max_val == 17 and ids == ["a", "d"], f"Test 7 failed: {max_val}, {ids}"
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"max_value": 0, "selected_ids": [], "rejected": [{"id": "unknown", "reason": "Invalid JSON"}]}))
        return

    sessions = data.get("sessions", [])
    valid, rejected = validate_sessions(sessions)
    max_val, selected_ids = solve_weighted_interval_scheduling(valid)

    output = {
        "max_value": max_val,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    print(json.dumps(output, indent=2, default=str))

if __name__ == "__main__":
    main()
```
````
