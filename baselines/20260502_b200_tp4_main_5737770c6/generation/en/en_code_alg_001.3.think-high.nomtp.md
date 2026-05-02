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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 17.082449
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2692, "completion_tokens": 2398, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2398
- Total tokens: 2692

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
    return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")

class Session:
    def __init__(self, session_dict):
        self.id = session_dict["id"]
        self.start = parse_timestamp(session_dict["start"])
        self.end = parse_timestamp(session_dict["end"])
        self.value = session_dict["value"]

def optimize_sessions(sessions):
    """Weighted interval scheduling with tie-breaking."""
    rejected = []
    valid = []

    for s in sessions:
        reasons = []
        if s.end <= s.start:
            reasons.append("end not after start")
        if s.value < 0:
            reasons.append("negative value")
        if reasons:
            rejected.append({"id": s.id, "reasons": reasons})
        else:
            valid.append(s)

    if not valid:
        return 0, [], rejected

    # Sort by end time
    valid.sort(key=lambda x: x.end)

    # Binary search for latest non-conflicting session
    def latest_non_conflict(i):
        lo, hi = 0, i - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if valid[mid].end <= valid[i].start:
                if mid == hi or valid[mid+1].end > valid[i].start:
                    return mid
                lo = mid + 1
            else:
                hi = mid - 1
        return -1

    n = len(valid)
    dp = [0] * (n + 1)
    choice = [None] * (n + 1)  # None means skip, True means take
    count = [0] * (n + 1)      # number of sessions in optimal solution

    # dp[i] = max value using first i sessions (sorted by end)
    for i in range(1, n + 1):
        # Option 1: skip session i-1
        skip_val = dp[i-1]
        skip_count = count[i-1]

        # Option 2: take session i-1
        p = latest_non_conflict(i-1) + 1  # convert to 1-based index
        take_val = valid[i-1].value + dp[p]
        take_count = count[p] + 1

        # Compare: higher value first, then fewer sessions, then lexicographic IDs
        if take_val > skip_val:
            dp[i] = take_val
            count[i] = take_count
            choice[i] = True
        elif take_val < skip_val:
            dp[i] = skip_val
            count[i] = skip_count
            choice[i] = None
        else:
            if take_count < skip_count:
                dp[i] = take_val
                count[i] = take_count
                choice[i] = True
            elif take_count > skip_count:
                dp[i] = skip_val
                count[i] = skip_count
                choice[i] = None
            else:
                # Build sequences to compare lexicographically
                take_ids = []
                j = i
                temp_j = i
                while temp_j > 0:
                    if choice[temp_j] is True:
                        take_ids.append(valid[temp_j-1].id)
                        p_inner = latest_non_conflict(temp_j-1) + 1
                        temp_j = p_inner
                    else:
                        temp_j -= 1
                take_ids.reverse()

                skip_ids = []
                j = i
                temp_j = i
                while temp_j > 0:
                    if choice[temp_j] is True:
                        skip_ids.append(valid[temp_j-1].id)
                        p_inner = latest_non_conflict(temp_j-1) + 1
                        temp_j = p_inner
                    else:
                        temp_j -= 1
                skip_ids.reverse()

                if take_ids < skip_ids:
                    dp[i] = take_val
                    count[i] = take_count
                    choice[i] = True
                else:
                    dp[i] = skip_val
                    count[i] = skip_count
                    choice[i] = None

    # Reconstruct
    selected_ids = []
    i = n
    while i > 0:
        if choice[i] is True:
            selected_ids.append(valid[i-1].id)
            p = latest_non_conflict(i-1) + 1
            i = p
        else:
            i -= 1
    selected_ids.reverse()

    return dp[n], selected_ids, rejected

def run_tests():
    """Built-in tests."""
    test_cases = []

    # Test 1: basic
    test_cases.append((
        [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
         {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
         {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}],
        9, ["a", "c"], []
    ))

    # Test 2: reject invalid
    test_cases.append((
        [{"id": "x", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5},
         {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}],
        0, [], [{"id": "x", "reasons": ["end not after start"]},
                {"id": "y", "reasons": ["negative value"]}]
    ))

    # Test 3: tie-breaking - fewer sessions
    test_cases.append((
        [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
         {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
         {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}],
        10, ["c"], []
    ))

    # Test 4: tie-breaking - lexicographic
    test_cases.append((
        [{"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
         {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
         {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}],
        10, ["a", "c"], []
    ))

    # Test 5: empty
    test_cases.append((
        [], 0, [], []
    ))

    # Test 6: single valid
    test_cases.append((
        [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 7}],
        7, ["a"], []
    ))

    all_passed = True
    for sessions_input, exp_val, exp_ids, exp_rej in test_cases:
        sessions = [Session(s) for s in sessions_input]
        max_val, sel_ids, rej = optimize_sessions(sessions)
        if max_val != exp_val or sel_ids != exp_ids:
            # Check rejected items more carefully
            rej_match = True
            if len(rej) != len(exp_rej):
                rej_match = False
            else:
                for r1, r2 in zip(rej, exp_rej):
                    if r1["id"] != r2["id"] or sorted(r1["reasons"]) != sorted(r2["reasons"]):
                        rej_match = False
                        break
            if not rej_match:
                all_passed = False
                print(f"FAIL: {sessions_input}")
                print(f"  Got: max_value={max_val}, ids={sel_ids}, rejected={rej}")
                print(f"  Exp: max_value={exp_val}, ids={exp_ids}, rejected={exp_rej}")

    if all_passed:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sys.exit(run_tests())

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    if "sessions" not in data or not isinstance(data["sessions"], list):
        print(json.dumps({"error": "Missing or invalid 'sessions' key"}))
        sys.exit(1)

    sessions = []
    for s_dict in data["sessions"]:
        if not isinstance(s_dict, dict) or "id" not in s_dict or "start" not in s_dict or "end" not in s_dict or "value" not in s_dict:
            print(json.dumps({"error": "Each session must have id, start, end, value"}))
            sys.exit(1)
        try:
            sessions.append(Session(s_dict))
        except ValueError as e:
            print(json.dumps({"error": f"Invalid timestamp: {e}"}))
            sys.exit(1)

    max_val, selected_ids, rejected = optimize_sessions(sessions)

    result = {
        "max_value": max_val,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
```
````
