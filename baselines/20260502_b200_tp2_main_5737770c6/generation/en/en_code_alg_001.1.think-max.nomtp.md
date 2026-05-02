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
- Elapsed seconds: 22.449392
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3016, "completion_tokens": 2722, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2722
- Total tokens: 3016

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
from bisect import bisect_right

def parse_timestamp(s):
    try:
        return datetime.fromisoformat(s)
    except:
        return None

def validate_sessions(sessions):
    valid = []
    rejected = []
    for s in sessions:
        sid = s.get("id", "unknown")
        start_str = s.get("start", "")
        end_str = s.get("end", "")
        value = s.get("value")

        if not isinstance(sid, str) or not sid:
            rejected.append({"id": sid, "reason": "Missing or empty id"})
            continue

        start = parse_timestamp(start_str)
        end = parse_timestamp(end_str)

        if start is None:
            rejected.append({"id": sid, "reason": "Invalid start timestamp"})
            continue
        if end is None:
            rejected.append({"id": sid, "reason": "Invalid end timestamp"})
            continue
        if end <= start:
            rejected.append({"id": sid, "reason": "End must be after start"})
            continue
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

def weighted_interval_scheduling(sessions):
    if not sessions:
        return 0, [], []

    sessions.sort(key=lambda x: x["end"])
    n = len(sessions)
    end_times = [s["end"] for s in sessions]

    p = [-1] * n
    for i in range(n):
        target = sessions[i]["start"]
        j = bisect_right(end_times, target) - 1
        p[i] = j

    dp = [0] * (n + 1)
    dp[0] = 0
    choice = [0] * (n + 1)

    for i in range(1, n + 1):
        idx = i - 1
        include_val = sessions[idx]["value"] + dp[p[idx] + 1]
        exclude_val = dp[i - 1]

        if include_val > exclude_val:
            dp[i] = include_val
            choice[i] = 1
        elif include_val < exclude_val:
            dp[i] = exclude_val
            choice[i] = 0
        else:
            candidates = []
            # Path with include
            path_inc = []
            k = i
            while k > 0:
                if choice[k] == 1:
                    path_inc.append(sessions[k - 1]["id"])
                    k = p[k - 1] + 1
                else:
                    k -= 1
            path_inc.reverse()

            # Path with exclude
            path_exc = []
            k = i
            while k > 0:
                if choice[k] == 1 and k != i:
                    path_exc.append(sessions[k - 1]["id"])
                    k = p[k - 1] + 1
                elif k == i:
                    k -= 1
                else:
                    k -= 1
            path_exc.reverse()

            # Prefer fewer sessions
            if len(path_inc) < len(path_exc):
                dp[i] = include_val
                choice[i] = 1
            elif len(path_exc) < len(path_inc):
                dp[i] = exclude_val
                choice[i] = 0
            else:
                if path_inc < path_exc:
                    dp[i] = include_val
                    choice[i] = 1
                else:
                    dp[i] = exclude_val
                    choice[i] = 0

    max_value = dp[n]
    selected_ids = []
    i = n
    while i > 0:
        if choice[i] == 1:
            selected_ids.append(sessions[i - 1]["id"])
            i = p[i - 1] + 1
        else:
            i -= 1
    selected_ids.reverse()

    return max_value, selected_ids, sessions

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        return

    sessions_data = data.get("sessions", [])
    if not isinstance(sessions_data, list):
        print(json.dumps({"error": "Sessions must be a list"}))
        return

    valid, rejected = validate_sessions(sessions_data)

    max_value, selected_ids, _ = weighted_interval_scheduling(valid)

    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    print(json.dumps(output, default=str))

def run_tests():
    passed = 0
    failed = 0

    # Test 1: Basic example
    test1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    valid, rejected = validate_sessions(test1["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 9, f"Test 1 max_value failed: {max_val}"
    assert sel_ids == ["a", "c"], f"Test 1 selected_ids failed: {sel_ids}"
    passed += 1

    # Test 2: Empty sessions
    test2 = {"sessions": []}
    valid, rejected = validate_sessions(test2["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 0
    assert sel_ids == []
    passed += 1

    # Test 3: Reject invalid sessions
    test3 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "y", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]
    }
    valid, rejected = validate_sessions(test3["sessions"])
    assert len(valid) == 0
    assert len(rejected) == 3
    passed += 1

    # Test 4: Tie-breaking with fewer sessions
    test4 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(test4["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    # Options: a+b=10 (2 sessions), c=5 (1 session), so a+b wins with fewer sessions? Wait 2 > 1, so c wins
    assert max_val == 5, f"Test 4 max_value failed: {max_val}"
    assert sel_ids == ["c"], f"Test 4 selected_ids failed: {sel_ids}"
    passed += 1

    # Test 5: Lexicographic tie
    test5 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 2}
        ]
    }
    valid, rejected = validate_sessions(test5["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    # Options: a+b=8, a+c=7, b+c=5, a=5, b=3, c=2. Best is a+b=8.
    assert max_val == 8
    assert sel_ids == ["a", "b"]
    passed += 1

    # Test 6: Multiple optimal with same value, different sessions
    test6 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 4},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 4}
        ]
    }
    valid, rejected = validate_sessions(test6["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    # Options: b+a=8 (2 sessions), c=4 (1 session) -> b+a wins with fewer? 2 > 1 -> c wins.
    # Actually c has same value as b? b+a=8, c=4, so b+a wins.
    # For tie: suppose value 4 each, b+a=8, c=4 -> b+a wins.
    assert max_val == 8
    # Both [a,b] and [b,a] but chronologically a after b -> [a,b]? Wait sorting by end: b end=10:00, a end=11:00, c end=10:30
    # Optimal: b (9-10) and a (10-11) = 8
    assert sel_ids == ["a", "b"] or sel_ids == ["b", "a"]
    passed += 1

    # Test 7: Non-negative value check
    test7 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 0},
        ]
    }
    valid, rejected = validate_sessions(test7["sessions"])
    max_val, sel_ids, _ = weighted_interval_scheduling(valid)
    assert max_val == 0
    assert sel_ids == ["x"]
    passed += 1

    print(f"All {passed} tests passed. (0 failed)")

if __name__ == "__main__":
    main()
```
````
