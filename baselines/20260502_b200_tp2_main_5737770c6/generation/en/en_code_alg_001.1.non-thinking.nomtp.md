# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 21.856417
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2780, "completion_tokens": 2486, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2486
- Total tokens: 2780

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

def parse_timestamp(ts_str):
    return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")

def validate_sessions(sessions):
    valid = []
    rejected = []
    for s in sessions:
        sid = s.get("id")
        if not sid:
            rejected.append({"id": sid, "reason": "Missing id"})
            continue
        try:
            start = parse_timestamp(s["start"])
            end = parse_timestamp(s["end"])
        except (KeyError, ValueError):
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue
        if end <= start:
            rejected.append({"id": sid, "reason": "End not after start"})
            continue
        value = s.get("value")
        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({"id": sid, "reason": "Negative or invalid value"})
            continue
        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })
    return valid, rejected

def schedule(valid_sessions):
    if not valid_sessions:
        return {"max_value": 0, "selected_ids": [], "rejected": []}

    # Sort by end time
    sorted_sessions = sorted(valid_sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Precompute end times for binary search
    end_times = [s["end"] for s in sorted_sessions]

    # Find last compatible session index for each session
    p = [-1] * n
    for i in range(n):
        # Binary search for rightmost end <= sorted_sessions[i].start
        j = bisect_right(end_times, sorted_sessions[i]["start"]) - 1
        p[i] = j

    # DP arrays: (max_value, session_count, lexicographic_key)
    # lexicographic_key is tuple of ids in order for tie-breaking
    dp_value = [0] * (n + 1)
    dp_count = [0] * (n + 1)
    dp_ids = [[] for _ in range(n + 1)]  # list of ids in order

    for i in range(1, n + 1):
        idx = i - 1
        # Option 1: exclude this session
        exclude_val = dp_value[i-1]
        exclude_cnt = dp_count[i-1]
        exclude_ids = dp_ids[i-1]

        # Option 2: include this session
        include_val = sorted_sessions[idx]["value"] + (dp_value[p[idx] + 1] if p[idx] >= 0 else 0)
        include_cnt = (dp_count[p[idx] + 1] if p[idx] >= 0 else 0) + 1
        # Build include_ids: ids from compatible prefix + current id
        if p[idx] >= 0:
            include_ids = dp_ids[p[idx] + 1] + [sorted_sessions[idx]["id"]]
        else:
            include_ids = [sorted_sessions[idx]["id"]]

        # Choose better option
        if include_val > exclude_val:
            dp_value[i] = include_val
            dp_count[i] = include_cnt
            dp_ids[i] = include_ids
        elif include_val < exclude_val:
            dp_value[i] = exclude_val
            dp_count[i] = exclude_cnt
            dp_ids[i] = exclude_ids
        else:
            # Values equal: choose fewer sessions
            if include_cnt < exclude_cnt:
                dp_value[i] = include_val
                dp_count[i] = include_cnt
                dp_ids[i] = include_ids
            elif include_cnt > exclude_cnt:
                dp_value[i] = exclude_val
                dp_count[i] = exclude_cnt
                dp_ids[i] = exclude_ids
            else:
                # Same count: lexicographically smaller list of ids
                # Compare as tuples of strings
                if tuple(include_ids) < tuple(exclude_ids):
                    dp_value[i] = include_val
                    dp_count[i] = include_cnt
                    dp_ids[i] = include_ids
                else:
                    dp_value[i] = exclude_val
                    dp_count[i] = exclude_cnt
                    dp_ids[i] = exclude_ids

    max_val = dp_value[n]
    selected = dp_ids[n]
    return {"max_value": max_val, "selected_ids": selected}

def run_tests():
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic case
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    result = schedule(valid)
    total_tests += 1
    assert result["max_value"] == 8, f"Test 1 failed: {result}"
    assert result["selected_ids"] == ["a", "c"], f"Test 1 failed: {result}"
    tests_passed += 1

    # Test 2: Empty
    data = {"sessions": []}
    valid, rejected = validate_sessions(data["sessions"])
    result = schedule(valid)
    total_tests += 1
    assert result["max_value"] == 0 and result["selected_ids"] == [], f"Test 2 failed"
    tests_passed += 1

    # Test 3: Rejection cases
    data = {
        "sessions": [
            {"id": "x", "start": "2026-01-01T00:00:00", "end": "2026-01-01T01:00:00", "value": -1},
            {"id": "y", "start": "2026-01-01T00:00:00", "end": "2025-01-01T00:00:00", "value": 5},
            {"id": "z", "start": "notatimestamp", "end": "2026-01-01T01:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    total_tests += 1
    assert len(rejected) == 3, f"Test 3 failed: {len(rejected)} rejected"
    tests_passed += 1

    # Test 4: Tie-breaking - fewer sessions
    data = {
        "sessions": [
            {"id": "a", "start": "2026-01-01T09:00:00", "end": "2026-01-01T12:00:00", "value": 10},
            {"id": "b", "start": "2026-01-01T09:00:00", "end": "2026-01-01T10:00:00", "value": 5},
            {"id": "c", "start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00", "value": 5},
            {"id": "d", "start": "2026-01-01T11:00:00", "end": "2026-01-01T12:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    result = schedule(valid)
    total_tests += 1
    # Both [a] and [b,c,d] give 10, but [a] has fewer sessions
    assert result["max_value"] == 10 and result["selected_ids"] == ["a"], f"Test 4 failed: {result}"
    tests_passed += 1

    # Test 5: Tie-breaking - lexicographic
    data = {
        "sessions": [
            {"id": "b", "start": "2026-01-01T09:00:00", "end": "2026-01-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-01-01T11:00:00", "end": "2026-01-01T12:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    # All non-overlapping, total 15. Two solutions with same count? Actually only one ordering.
    # Force tie by making two different sets with same value and count
    data2 = {
        "sessions": [
            {"id": "c", "start": "2026-01-01T09:00:00", "end": "2026-01-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-01-01T09:00:00", "end": "2026-01-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-01-01T10:00:00", "end": "2026-01-01T11:00:00", "value": 5}
        ]
    }
    valid2, _ = validate_sessions(data2["sessions"])
    result2 = schedule(valid2)
    total_tests += 1
    # Both [a,b] and [c,b] give 10, 2 sessions. Lexicographically ["a","b"] < ["c","b"]
    assert result2["selected_ids"] == ["a", "b"], f"Test 5 failed: {result2}"
    tests_passed += 1

    print(f"All {total_tests} tests passed.", file=sys.stderr)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)

    sessions = data.get("sessions", [])
    valid, rejected = validate_sessions(sessions)
    result = schedule(valid)
    result["rejected"] = rejected
    print(json.dumps(result, default=str))

if __name__ == "__main__":
    main()
```
````
