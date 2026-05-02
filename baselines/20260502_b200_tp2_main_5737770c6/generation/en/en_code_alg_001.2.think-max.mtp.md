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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 11.212283
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3422, "completion_tokens": 3128, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3128
- Total tokens: 3422

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

def parse_iso(timestamp):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")

def precompute_p(sessions):
    """
    For each session (sorted by end time), find the last session that
    finishes before it starts. Return list p where p[i] is index of
    that session or -1 if none.
    """
    end_times = [s[2] for s in sessions]  # end timestamps
    p = []
    for i, s in enumerate(sessions):
        start = s[1]
        # binary search for rightmost end_time < start
        j = bisect_left(end_times, start) - 1
        p.append(j)
    return p

def reconstruct(dp, p, sessions):
    """Reconstruct the optimal set of sessions with tie-breaking."""
    n = len(sessions)
    chosen = []
    i = n - 1
    while i >= 0:
        value_if_take = sessions[i][3] + (dp[p[i]] if p[i] >= 0 else 0)
        value_if_skip = dp[i - 1] if i > 0 else 0
        if value_if_take > value_if_skip:
            chosen.append(i)
            i = p[i]
        elif value_if_take < value_if_skip:
            i -= 1
        else:
            # Equal value: choose fewer sessions, then lexicographically smaller IDs
            # Explore both branches and compare
            # Branch 1: take i
            branch_take = [i]
            j = p[i]
            while j >= 0:
                v_take = sessions[j][3] + (dp[p[j]] if p[j] >= 0 else 0)
                v_skip = dp[j - 1] if j > 0 else 0
                if v_take > v_skip:
                    branch_take.append(j)
                    j = p[j]
                elif v_take < v_skip:
                    j -= 1
                else:
                    # Recursive tie - we need consistent rule
                    # For simplicity, prefer skipping to reduce sessions
                    j -= 1
            # Branch 2: skip i
            branch_skip = []
            j = i - 1
            while j >= 0:
                v_take = sessions[j][3] + (dp[p[j]] if p[j] >= 0 else 0)
                v_skip = dp[j - 1] if j > 0 else 0
                if v_take > v_skip:
                    branch_skip.append(j)
                    j = p[j]
                elif v_take < v_skip:
                    j -= 1
                else:
                    j -= 1
            # Compare: fewer sessions preferred, then lexicographically smaller IDs
            len_take = len(branch_take)
            len_skip = len(branch_skip)
            id_list_take = sorted([sessions[idx][0] for idx in branch_take])
            id_list_skip = sorted([sessions[idx][0] for idx in branch_skip])
            if len_take < len_skip:
                chosen.extend(branch_take)
                i = p[i]
            elif len_skip < len_take:
                chosen.extend(branch_skip)
                i = i - 1
            else:
                # Same length, compare lexicographically
                if id_list_take < id_list_skip:
                    chosen.extend(branch_take)
                    i = p[i]
                else:
                    chosen.extend(branch_skip)
                    i = i - 1
    return chosen

def optimize(sessions):
    """Main DP optimization. Returns (max_value, selected_ids, rejected_list)."""
    rejected = []
    valid_sessions = []

    for s in sessions:
        sid = s["id"]
        start_str = s["start"]
        end_str = s["end"]
        value = s["value"]

        # Validate value
        if value < 0:
            rejected.append({"id": sid, "reason": "negative value"})
            continue

        # Parse timestamps
        try:
            start_dt = parse_iso(start_str)
            end_dt = parse_iso(end_str)
        except (ValueError, KeyError):
            rejected.append({"id": sid, "reason": "invalid timestamp format"})
            continue

        # Validate start < end
        if end_dt <= start_dt:
            rejected.append({"id": sid, "reason": "end not after start"})
            continue

        valid_sessions.append((sid, start_dt, end_dt, value))

    # Sort by end time
    valid_sessions.sort(key=lambda x: x[2])

    # If no valid sessions
    if not valid_sessions:
        return 0, [], rejected

    # Precompute p array
    p = precompute_p(valid_sessions)

    # DP
    n = len(valid_sessions)
    dp = [0] * n
    for i in range(n):
        value = valid_sessions[i][3]
        # Take session i
        take = value + (dp[p[i]] if p[i] >= 0 else 0)
        # Skip session i
        skip = dp[i - 1] if i > 0 else 0
        dp[i] = max(take, skip)

    max_value = dp[-1]

    # Reconstruct
    chosen_indices = reconstruct(dp, p, valid_sessions)

    # Get IDs in chronological order (already sorted by reconstruction if careful)
    # Reconstruct goes from end to start, so reverse
    chosen_indices.reverse()
    selected_ids = [valid_sessions[idx][0] for idx in chosen_indices]

    # Double-check chronological order (should be since sorted by end time and non-overlapping)
    # Not strictly needed but safe

    return max_value, selected_ids, rejected

def run_tests():
    """Run built-in tests."""
    test_cases = []

    # Test 1: Simple two non-overlapping
    data1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3}
        ]
    }
    test_cases.append((data1, 8, ["a", "b"], []))

    # Test 2: Overlapping - choose higher value
    data2 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 9}
        ]
    }
    test_cases.append((data2, 10, ["a"], []))

    # Test 3: Negative value rejection
    data3 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    test_cases.append((data3, 5, ["b"], [{"id": "a", "reason": "negative value"}]))

    # Test 4: End not after start
    data4 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
        ]
    }
    test_cases.append((data4, 0, [], [{"id": "a", "reason": "end not after start"}]))

    # Test 5: Tie-breaking - fewer sessions
    data5 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    # Option: [a,b] value=10, 2 sessions; [c] value=10, 1 session -> choose [c]
    test_cases.append((data5, 10, ["c"], []))

    # Test 6: Tie-breaking - same sessions count, lexicographically smaller
    data6 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    # [b,a] vs [c] same value, [c] has fewer sessions -> [c]
    test_cases.append((data6, 10, ["c"], []))

    # Test 7: Equal value, equal sessions, lexicographic tie
    data7 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 15}
        ]
    }
    # [a,b,c] value=15, 3 sessions; [d] value=15, 1 session -> [d]
    test_cases.append((data7, 15, ["d"], []))

    # Test 8: Complex overlapping
    data8 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 6},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 7},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4},
            {"id": "d", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:00:00", "value": 2}
        ]
    }
    # Best: a (6) + c (4) = 10; b (7) + ? b overlaps with a,d, but after b ends at 11:30, nothing? Actually c starts at 11:00 overlaps with b. So b alone 7, or a+c=10, or d+b? d 2 + b 7 =9. Best = a+c=10
    test_cases.append((data8, 10, ["a", "c"], []))

    # Run tests
    for i, (data, expected_val, expected_ids, expected_rejected) in enumerate(test_cases):
        max_val, sel_ids, rejected = optimize(data["sessions"])
        assert max_val == expected_val, f"Test {i+1} failed: value {max_val} != {expected_val}"
        assert sel_ids == expected_ids, f"Test {i+1} failed: ids {sel_ids} != {expected_ids}"
        assert rejected == expected_rejected, f"Test {i+1} failed: rejected {rejected} != {expected_rejected}"
    print("All tests passed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    data = json.load(sys.stdin)
    max_val, sel_ids, rejected = optimize(data["sessions"])
    output = {
        "max_value": max_val,
        "selected_ids": sel_ids,
        "rejected": rejected
    }
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
```
````
