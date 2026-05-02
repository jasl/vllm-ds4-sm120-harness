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
- Elapsed seconds: 9.407813
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2998, "completion_tokens": 2704, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2704
- Total tokens: 2998

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
    try:
        return datetime.fromisoformat(ts_str)
    except ValueError:
        return None

def validate_sessions(sessions):
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get("id", "unknown")
        start_str = session.get("start", "")
        end_str = session.get("end", "")
        value = session.get("value", None)

        errors = []
        if not isinstance(sid, str) or not sid:
            errors.append("invalid or missing id")
        start = parse_timestamp(start_str)
        if start is None:
            errors.append("invalid start timestamp")
        end = parse_timestamp(end_str)
        if end is None:
            errors.append("invalid end timestamp")
        if start and end and end <= start:
            errors.append("end not after start")
        if value is None or not isinstance(value, (int, float)) or value < 0:
            errors.append("negative or missing value")

        if errors:
            rejected.append({"id": sid, "reason": "; ".join(errors)})
        else:
            valid.append({
                "id": sid,
                "start": start,
                "end": end,
                "value": value
            })
    return valid, rejected

def optimize(valid_sessions):
    if not valid_sessions:
        return 0, [], []

    # Sort by end time
    sorted_sessions = sorted(valid_sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)
    end_times = [s["end"] for s in sorted_sessions]

    # Compute p[i] = last non-overlapping session index before i
    p = [-1] * n
    for i in range(n):
        start_i = sorted_sessions[i]["start"]
        # Binary search for latest end <= start_i
        j = bisect_right(end_times, start_i) - 1
        p[i] = j

    # DP tables: dp[i] = max value up to i, choice[i] = True if selected
    dp = [0] * (n + 1)  # dp[0] = 0 before any session
    choice = [False] * n

    for i in range(1, n + 1):
        idx = i - 1
        # Option 1: don't include session i
        dont_take = dp[i - 1]
        # Option 2: include session i
        prev_idx = p[idx] + 1  # index in dp array
        take = sorted_sessions[idx]["value"] + dp[prev_idx]

        if take > dont_take:
            dp[i] = take
            choice[idx] = True
        elif take < dont_take:
            dp[i] = dont_take
            choice[idx] = False
        else:
            # Tie: prefer fewer sessions, then lexicographically smaller IDs
            # We need to compare solutions: reconstruct both and pick
            # Dummy reconstruction for comparison (lazy)
            # For efficiency, we can store both possibilities or compare later
            # Here we do a simple reconstruction on tie
            sol_take = reconstruct(sorted_sessions, p, choice[:idx] + [True] + choice[idx+1:], idx)
            sol_dont = reconstruct(sorted_sessions, p, choice[:idx] + [False] + choice[idx+1:], idx)
            # Compare: fewer sessions
            if len(sol_take) < len(sol_dont):
                dp[i] = take
                choice[idx] = True
            elif len(sol_take) > len(sol_dont):
                dp[i] = dont_take
                choice[idx] = False
            else:
                # Lexicographically smaller list of IDs
                ids_take = sorted([s["id"] for s in sol_take])
                ids_dont = sorted([s["id"] for s in sol_dont])
                if ids_take < ids_dont:
                    dp[i] = take
                    choice[idx] = True
                else:
                    dp[i] = dont_take
                    choice[idx] = False

    max_value = dp[n]
    selected = reconstruct(sorted_sessions, p, choice, n - 1)
    selected_ids = [s["id"] for s in selected]
    return max_value, selected_ids, []

def reconstruct(sessions, p, choice, last_idx):
    result = []
    i = last_idx
    while i >= 0:
        if choice[i]:
            result.append(sessions[i])
            i = p[i]
        else:
            i -= 1
    result.reverse()
    return result

def solve(input_data):
    sessions = input_data.get("sessions", [])
    if not isinstance(sessions, list):
        sessions = []
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids, _ = optimize(valid)
    # Ensure chronological order (already by end time, but just in case)
    selected_ids_sorted = selected_ids  # already in order from reconstruction
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids_sorted,
        "rejected": rejected
    }
    return output

# Built-in tests
def run_tests():
    # Test 1: simple case
    data1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
        ]
    }
    res1 = solve(data1)
    assert res1["max_value"] == 5, f"Test 1 failed: {res1}"
    assert res1["selected_ids"] == ["a"], f"Test 1 ids: {res1}"

    # Test 2: two non-overlapping
    data2 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 2},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
        ]
    }
    res2 = solve(data2)
    assert res2["max_value"] == 5, f"Test 2 failed: {res2}"
    assert res2["selected_ids"] == ["a", "b"], f"Test 2 ids: {res2}"

    # Test 3: overlapping with higher value
    data3 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 8},
        ]
    }
    res3 = solve(data3)
    assert res3["max_value"] == 10, f"Test 3 failed: {res3}"
    assert res3["selected_ids"] == ["a"], f"Test 3 ids: {res3}"

    # Test 4: rejected sessions
    data4 = {
        "sessions": [
            {"id": "bad1", "start": "invalid", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 3},
            {"id": "bad3", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
        ]
    }
    res4 = solve(data4)
    assert res4["max_value"] == 0, f"Test 4 max_value: {res4}"
    assert len(res4["rejected"]) == 3, f"Test 4 rejected count: {res4}"

    # Test 5: tie-breaking (fewer sessions)
    data5 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
        ]
    }
    res5 = solve(data5)
    assert res5["max_value"] == 10, f"Test 5 max_value: {res5}"
    assert res5["selected_ids"] == ["c"], f"Test 5 ids: {res5}"

    # Test 6: lexicographic tie-break
    data6 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        ]
    }
    res6 = solve(data6)
    assert res6["max_value"] == 15, f"Test 6 max_value: {res6}"
    assert res6["selected_ids"] == ["a", "b", "c"], f"Test 6 ids: {res6}"

    # Test 7: complex tie (same total value, different session counts)
    data7 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 6},
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 6},
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 12},
        ]
    }
    res7 = solve(data7)
    assert res7["max_value"] == 12, f"Test 7 max_value: {res7}"
    assert res7["selected_ids"] == ["z"], f"Test 7 ids: {res7}"

    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)
    result = solve(input_data)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```
````
