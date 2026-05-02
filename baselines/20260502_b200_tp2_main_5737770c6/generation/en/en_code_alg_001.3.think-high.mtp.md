# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 13.296814
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 4057, "completion_tokens": 3763, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3763
- Total tokens: 4057

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

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    # Remove trailing Z if present for compatibility
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1]
    return datetime.fromisoformat(ts_str)

def optimize(sessions_data):
    """
    Weighted interval scheduling with tie-breaking:
    - Maximize total value
    - If multiple optimal, choose fewer sessions
    - If still tied, choose lexicographically smaller list of IDs
    """
    rejected = []
    valid_sessions = []

    for sess in sessions_data.get("sessions", []):
        sid = sess.get("id", "unknown")
        reasons = []

        # Check required fields
        if "start" not in sess or "end" not in sess or "value" not in sess:
            reasons.append("Missing required field")
        else:
            try:
                start = parse_timestamp(sess["start"])
                end = parse_timestamp(sess["end"])
                value = sess["value"]
                if not isinstance(value, (int, float)):
                    reasons.append("Value must be a number")
                elif value < 0:
                    reasons.append("Negative value")
                if end <= start:
                    reasons.append("End not after start")
                if not reasons:
                    valid_sessions.append((sid, start, end, value))
            except (ValueError, TypeError):
                reasons.append("Invalid timestamp format")

        if reasons:
            rejected.append({"id": sid, "reasons": reasons})

    if not valid_sessions:
        return {"max_value": 0, "selected_ids": [], "rejected": rejected}

    # Sort by end time
    valid_sessions.sort(key=lambda x: x[2])

    n = len(valid_sessions)
    end_times = [s[2] for s in valid_sessions]

    # Precompute p[i]: largest index j < i with end[j] <= start[i]
    p = [-1] * n
    for i in range(n):
        start_i = valid_sessions[i][1]
        # Binary search
        lo, hi = 0, i - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_i:
                lo = mid + 1
            else:
                hi = mid - 1
        p[i] = hi

    # DP arrays: (value, count, lex_key) for tie-breaking
    # lex_key is tuple of IDs for lexicographic comparison
    dp_value = [0] * (n + 1)
    dp_count = [0] * (n + 1)
    dp_lex = [()] * (n + 1)
    choice = [False] * n  # whether session i is selected in optimal solution up to i

    for i in range(1, n + 1):
        idx = i - 1
        # Option 1: skip session i-1
        skip_val = dp_value[i - 1]
        skip_cnt = dp_count[i - 1]
        skip_lex = dp_lex[i - 1]

        # Option 2: take session i-1
        take_idx = p[idx] + 1
        take_val = valid_sessions[idx][3] + dp_value[take_idx]
        take_cnt = dp_count[take_idx] + 1
        take_lex = dp_lex[take_idx] + (valid_sessions[idx][0],)

        # Compare: higher value wins
        if take_val > skip_val:
            dp_value[i] = take_val
            dp_count[i] = take_cnt
            dp_lex[i] = take_lex
            choice[idx] = True
        elif take_val < skip_val:
            dp_value[i] = skip_val
            dp_count[i] = skip_cnt
            dp_lex[i] = skip_lex
            choice[idx] = False
        else:
            # Same value: fewer sessions wins
            if take_cnt < skip_cnt:
                dp_value[i] = take_val
                dp_count[i] = take_cnt
                dp_lex[i] = take_lex
                choice[idx] = True
            elif take_cnt > skip_cnt:
                dp_value[i] = skip_val
                dp_count[i] = skip_cnt
                dp_lex[i] = skip_lex
                choice[idx] = False
            else:
                # Same count: lexicographically smaller list wins
                take_lex_list = list(take_lex)
                skip_lex_list = list(skip_lex)
                if take_lex_list < skip_lex_list:
                    dp_value[i] = take_val
                    dp_count[i] = take_cnt
                    dp_lex[i] = take_lex
                    choice[idx] = True
                else:
                    dp_value[i] = skip_val
                    dp_count[i] = skip_cnt
                    dp_lex[i] = skip_lex
                    choice[idx] = False

    # Reconstruct solution
    selected_ids = []
    i = n
    while i > 0:
        idx = i - 1
        if choice[idx]:
            selected_ids.append(valid_sessions[idx][0])
            i = p[idx] + 1
        else:
            i -= 1
    selected_ids.reverse()  # chronological order (sorted by end time already)

    return {
        "max_value": dp_value[n],
        "selected_ids": selected_ids,
        "rejected": rejected
    }

def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic example
    data1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    res1 = optimize(data1)
    assert res1["max_value"] == 9, f"Test 1 failed: max_value {res1['max_value']}"
    assert res1["selected_ids"] == ["a", "c"], f"Test 1 failed: selected_ids {res1['selected_ids']}"
    tests_passed += 1
    total_tests += 1

    # Test 2: Empty input
    res2 = optimize({"sessions": []})
    assert res2["max_value"] == 0
    assert res2["selected_ids"] == []
    tests_passed += 1
    total_tests += 1

    # Test 3: Reject invalid sessions
    data3 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3}
        ]
    }
    res3 = optimize(data3)
    assert res3["max_value"] == 3
    assert res3["selected_ids"] == ["z"]
    assert len(res3["rejected"]) == 2
    tests_passed += 1
    total_tests += 1

    # Test 4: Tie-breaking - fewer sessions
    data4 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    # Option 1: {a} value=10, sessions=1
    # Option 2: {b,c} value=10, sessions=2
    # Should choose {a}
    res4 = optimize(data4)
    assert res4["max_value"] == 10
    assert res4["selected_ids"] == ["a"], f"Test 4 failed: {res4['selected_ids']}"
    tests_passed += 1
    total_tests += 1

    # Test 5: Tie-breaking - lexicographic
    data5 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    # Two options with value 10: {a} and {b,c}
    # {a} has fewer sessions, so choose {a}
    res5 = optimize(data5)
    assert res5["max_value"] == 10
    assert res5["selected_ids"] == ["a"], f"Test 5 failed: {res5['selected_ids']}"
    tests_passed += 1
    total_tests += 1

    # Test 6: Tie-breaking same count lexicographic
    data6 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ]
    }
    # All sessions non-overlapping, same value
    # Possible: {a,b,c} value=15, count=3
    # Also possible: any subset? No, all disjoint, so only {a,b,c}
    res6 = optimize(data6)
    assert res6["max_value"] == 15
    assert res6["selected_ids"] == ["a", "b", "c"], f"Test 6 failed: {res6['selected_ids']}"
    tests_passed += 1
    total_tests += 1

    # Test 7: All rejected
    data7 = {
        "sessions": [
            {"id": "bad1", "start": "invalid", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5}
        ]
    }
    res7 = optimize(data7)
    assert res7["max_value"] == 0
    assert res7["selected_ids"] == []
    assert len(res7["rejected"]) == 2
    tests_passed += 1
    total_tests += 1

    # Test 8: Missing fields
    data8 = {
        "sessions": [
            {"id": "no_start", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "no_end", "start": "2026-05-01T09:00:00", "value": 5},
            {"id": "no_value", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00"}
        ]
    }
    res8 = optimize(data8)
    assert res8["max_value"] == 0
    assert len(res8["rejected"]) == 3
    tests_passed += 1
    total_tests += 1

    # Test 9: Large value and overlapping
    data9 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 100},
            {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 1},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 1}
        ]
    }
    # {a,c} value=101, {b} value=1, or {a} value=100, {c} value=1
    res9 = optimize(data9)
    assert res9["max_value"] == 101
    assert res9["selected_ids"] == ["a", "c"]
    tests_passed += 1
    total_tests += 1

    # Test 10: Complex tie-breaking
    data10 = {
        "sessions": [
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    # {a} value=10 count=1, {b,c} value=10 count=2 -> choose {a}
    res10 = optimize(data10)
    assert res10["max_value"] == 10
    assert res10["selected_ids"] == ["a"]
    tests_passed += 1
    total_tests += 1

    # Test 11: Many sessions, ensure O(n log n) works
    sessions = []
    for i in range(100):
        sessions.append({
            "id": str(i),
            "start": f"2026-05-01T{9 + i//4:02d}:{(i*15)%60:02d}:00",
            "end": f"2026-05-01T{9 + i//4 + 1:02d}:{(i*15)%60:02d}:00",
            "value": 1
        })
    data11 = {"sessions": sessions}
    res11 = optimize(data11)
    # Should pick 25 non-overlapping sessions (since each hour block has 4 sessions)
    assert res11["max_value"] == 25
    assert len(res11["selected_ids"]) == 25
    tests_passed += 1
    total_tests += 1

    print(f"All {tests_passed}/{total_tests} tests passed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
        result = optimize(data)
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```
````
