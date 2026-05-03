# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 34.908486
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2521, "completion_tokens": 2227, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2227
- Total tokens: 2521

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

def parse_time(s):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

def weighted_interval_scheduling(sessions):
    """
    Weighted interval scheduling with tie-breaking:
    - maximize total value
    - if tie, fewer sessions
    - if still tie, lexicographically smaller list of IDs
    """
    n = len(sessions)
    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x['end_dt'])
    end_times = [s['end_dt'] for s in sorted_sessions]

    # Precompute p[i] = last non-overlapping session index before i
    p = [-1] * n
    for i in range(n):
        start = sorted_sessions[i]['start_dt']
        # Binary search for the rightmost session with end <= start
        lo, hi = 0, i-1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start:
                lo = mid + 1
            else:
                hi = mid - 1
        p[i] = hi  # hi is the last index with end <= start

    # DP arrays: (value, count, id_list) for optimal solution up to i
    dp_val = [0] * n
    dp_cnt = [0] * n
    dp_ids = [[] for _ in range(n)]

    for i in range(n):
        # Option 1: exclude session i
        if i > 0:
            best_val = dp_val[i-1]
            best_cnt = dp_cnt[i-1]
            best_ids = dp_ids[i-1][:]
        else:
            best_val = 0
            best_cnt = 0
            best_ids = []

        # Option 2: include session i
        include_val = sorted_sessions[i]['value']
        include_cnt = 1
        if p[i] >= 0:
            include_val += dp_val[p[i]]
            include_cnt += dp_cnt[p[i]]
            include_ids = dp_ids[p[i]][:]
        else:
            include_ids = []
        include_ids.append(sorted_sessions[i]['id'])

        # Compare options
        better = False
        if include_val > best_val:
            better = True
        elif include_val == best_val:
            if include_cnt < best_cnt:
                better = True
            elif include_cnt == best_cnt:
                if include_ids < best_ids:
                    better = True

        if better:
            dp_val[i] = include_val
            dp_cnt[i] = include_cnt
            dp_ids[i] = include_ids
        else:
            dp_val[i] = best_val
            dp_cnt[i] = best_cnt
            dp_ids[i] = best_ids

    if n == 0:
        return 0, []
    return dp_val[n-1], dp_ids[n-1]

def process_input(data):
    raw_sessions = data.get("sessions", [])
    valid_sessions = []
    rejected = []

    for idx, sess in enumerate(raw_sessions):
        reasons = []
        sid = sess.get("id", f"session_{idx}")

        # Check required fields
        if not isinstance(sess.get("id"), str) or not sess.get("id"):
            reasons.append("invalid or missing id")
        if "start" not in sess:
            reasons.append("missing start")
        if "end" not in sess:
            reasons.append("missing end")
        if "value" not in sess:
            reasons.append("missing value")

        if reasons:
            rejected.append({"id": sid, "reasons": reasons})
            continue

        # Parse timestamps
        try:
            start_dt = parse_time(sess["start"])
            end_dt = parse_time(sess["end"])
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reasons": ["invalid timestamp format"]})
            continue

        # Validate
        if end_dt <= start_dt:
            rejected.append({"id": sid, "reasons": ["end must be after start"]})
            continue
        if not isinstance(sess["value"], (int, float)) or sess["value"] < 0:
            rejected.append({"id": sid, "reasons": ["value must be non-negative"]})
            continue

        valid_sessions.append({
            "id": sid,
            "start_dt": start_dt,
            "end_dt": end_dt,
            "value": sess["value"],
            "end": sess["end"],
            "start": sess["start"]
        })

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)
    # Sort selected_ids by original order (chronological by start time)
    id_order = {s['id']: s['start_dt'] for s in valid_sessions}
    selected_ids_sorted = sorted(selected_ids, key=lambda x: id_order[x])

    return max_value, selected_ids_sorted, rejected

def run_tests():
    test_cases = []

    # Test 1: simple non-overlapping
    test_cases.append({
        "input": {"sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3}
        ]},
        "expected_max": 8,
        "expected_ids": ["a", "b"]
    })

    # Test 2: overlapping with better choice
    test_cases.append({
        "input": {"sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 6}
        ]},
        "expected_max": 6,
        "expected_ids": ["b"]
    })

    # Test 3: tie-breaking fewer sessions
    test_cases.append({
        "input": {"sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]},
        "expected_max": 10,
        "expected_ids": ["a", "b"]
    })

    # Test 4: tie-breaking lexicographic
    test_cases.append({
        "input": {"sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]},
        "expected_max": 10,
        "expected_ids": ["a", "b"]  # lexicographically smaller
    })

    # Test 5: rejection cases
    test_cases.append({
        "input": {"sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]},
        "expected_max": 0,
        "expected_ids": [],
        "check_rejected": True
    })

    # Test 6: empty input
    test_cases.append({
        "input": {"sessions": []},
        "expected_max": 0,
        "expected_ids": []
    })

    all_pass = True
    for i, tc in enumerate(test_cases):
        max_val, sel_ids, rejected = process_input(tc["input"])
        expected_max = tc["expected_max"]
        expected_ids = tc["expected_ids"]

        if max_val != expected_max or sel_ids != expected_ids:
            print(f"FAIL test {i+1}: got max={max_val}, ids={sel_ids}", file=sys.stderr)
            all_pass = False
        if tc.get("check_rejected") and len(rejected) == 0:
            print(f"FAIL test {i+1}: expected rejection but none occurred", file=sys.stderr)
            all_pass = False

    if all_pass:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!", file=sys.stderr)
        return 1

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sys.exit(run_tests())

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"error": "invalid JSON input"}))
        sys.exit(1)

    max_value, selected_ids, rejected = process_input(data)
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
```
````
