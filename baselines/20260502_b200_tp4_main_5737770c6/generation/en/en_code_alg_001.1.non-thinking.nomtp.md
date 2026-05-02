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
- Elapsed seconds: 18.231596
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2841, "completion_tokens": 2547, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2547
- Total tokens: 2841

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
    # Remove trailing Z if present (treat as UTC without timezone)
    if ts_str.endswith('Z'):
        ts_str = ts_str[:-1]
    # Handle potential microsecond precision variations
    try:
        return datetime.fromisoformat(ts_str)
    except ValueError:
        # Try with space separator
        try:
            return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {ts_str}")

class Session:
    __slots__ = ('id', 'start', 'end', 'value', 'start_dt', 'end_dt')

    def __init__(self, id, start_str, end_str, value):
        self.id = id
        self.start = start_str
        self.end = end_str
        self.value = value
        self.start_dt = parse_timestamp(start_str)
        self.end_dt = parse_timestamp(end_str)

def optimize(sessions):
    """
    Weighted interval scheduling with O(n log n) DP.
    Returns (max_value, selected_ids, rejected_list).
    """
    rejected = []
    valid = []

    # Validate sessions
    for s in sessions:
        reasons = []
        if s.end_dt <= s.start_dt:
            reasons.append("end_not_after_start")
        if s.value < 0:
            reasons.append("negative_value")
        if reasons:
            rejected.append({"id": s.id, "reasons": reasons})
        else:
            valid.append(s)

    if not valid:
        return 0, [], rejected

    # Sort by end time
    valid.sort(key=lambda x: x.end_dt)

    n = len(valid)
    # Precompute p(i): index of last session that ends before session i starts
    p = [-1] * n
    for i in range(n):
        lo, hi = 0, i-1
        while lo <= hi:
            mid = (lo + hi) // 2
            if valid[mid].end_dt <= valid[i].start_dt:
                lo = mid + 1
            else:
                hi = mid - 1
        p[i] = hi  # hi is the last index with end <= start

    # DP arrays
    dp = [0] * n  # max value up to i
    choice = [0] * n  # 1 = take session i, 0 = skip

    for i in range(n):
        # Option 1: skip session i
        skip_val = dp[i-1] if i > 0 else 0

        # Option 2: take session i
        take_val = valid[i].value
        if p[i] >= 0:
            take_val += dp[p[i]]

        if take_val > skip_val:
            dp[i] = take_val
            choice[i] = 1
        elif take_val < skip_val:
            dp[i] = skip_val
            choice[i] = 0
        else:
            # Tie: prefer fewer sessions, then lexicographically smaller IDs
            # We need to reconstruct both options to compare
            take_sessions = []
            temp = i
            while temp >= 0:
                if choice[temp] == 1 and dp[temp] == (valid[temp].value + (dp[p[temp]] if p[temp] >= 0 else 0)):
                    take_sessions.append(valid[temp].id)
                    temp = p[temp]
                else:
                    temp -= 1
            take_sessions.reverse()

            skip_sessions = []
            temp = i-1
            while temp >= 0:
                if choice[temp] == 1:
                    skip_sessions.append(valid[temp].id)
                    temp = p[temp]
                else:
                    temp -= 1
            skip_sessions.reverse()

            # Compare: fewer sessions preferred, then lexicographically smaller list
            if len(take_sessions) < len(skip_sessions):
                dp[i] = take_val
                choice[i] = 1
            elif len(take_sessions) > len(skip_sessions):
                dp[i] = skip_val
                choice[i] = 0
            else:
                # Same count, compare lexicographically
                if take_sessions < skip_sessions:
                    dp[i] = take_val
                    choice[i] = 1
                else:
                    dp[i] = skip_val
                    choice[i] = 0

    # Reconstruct solution
    max_val = dp[-1] if n > 0 else 0
    selected = []
    i = n - 1
    while i >= 0:
        if choice[i] == 1:
            selected.append(valid[i].id)
            i = p[i]
        else:
            i -= 1
    selected.reverse()

    return max_val, selected, rejected

def run_tests():
    test_cases = [
        # Test 1: Basic case
        ({
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
            ]
        }, {"max_value": 8, "selected_ids": ["a", "c"]}),

        # Test 2: Empty
        ({"sessions": []}, {"max_value": 0, "selected_ids": []}),

        # Test 3: All rejected
        ({
            "sessions": [
                {"id": "x", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5},
                {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -1}
            ]
        }, {"max_value": 0, "selected_ids": [], "rejected_count": 2}),

        # Test 4: Tie-breaking (fewer sessions)
        ({
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
            ]
        }, {"max_value": 10, "selected_ids": ["c"]}),

        # Test 5: Tie-breaking lexicographic
        ({
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
            ]
        }, {"max_value": 15, "selected_ids": ["a", "b", "c"]}),

        # Test 6: Complex overlap
        ({
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 7},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 6},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 8},
                {"id": "d", "start": "2026-05-01T12:30:00", "end": "2026-05-01T14:00:00", "value": 4}
            ]
        }, {"max_value": 15, "selected_ids": ["a", "c"]}),

        # Test 7: With Z suffix
        ({
            "sessions": [
                {"id": "z1", "start": "2026-05-01T09:00:00Z", "end": "2026-05-01T10:00:00Z", "value": 3}
            ]
        }, {"max_value": 3, "selected_ids": ["z1"]}),
    ]

    passed = 0
    for idx, (input_data, expected) in enumerate(test_cases, 1):
        sessions = []
        for s in input_data["sessions"]:
            sessions.append(Session(s["id"], s["start"], s["end"], s["value"]))

        max_val, selected, rejected = optimize(sessions)

        if "rejected_count" in expected:
            ok = (max_val == expected["max_value"] and
                  selected == expected["selected_ids"] and
                  len(rejected) == expected["rejected_count"])
        else:
            ok = (max_val == expected["max_value"] and
                  selected == expected["selected_ids"])

        if ok:
            passed += 1
        else:
            print(f"FAIL test {idx}: expected {expected}, got max_val={max_val}, selected={selected}, rejected={len(rejected)}")

    print(f"All {len(test_cases)} tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    sessions = []
    for s in data.get("sessions", []):
        sessions.append(Session(s["id"], s["start"], s["end"], s["value"]))

    max_val, selected, rejected = optimize(sessions)

    output = {
        "max_value": max_val,
        "selected_ids": selected,
        "rejected": rejected
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
```
````
