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
- Elapsed seconds: 43.975776
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 4021, "completion_tokens": 3727, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3727
- Total tokens: 4021

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
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and return lists of valid sessions and rejected entries."""
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get("id", "unknown")
        reasons = []

        # Check required fields
        if "start" not in session or "end" not in session or "value" not in session:
            reasons.append("missing required fields")
        else:
            try:
                start = parse_timestamp(session["start"])
                end = parse_timestamp(session["end"])
                value = session["value"]

                if not isinstance(value, (int, float)):
                    reasons.append("value must be a number")
                elif value < 0:
                    reasons.append("value is negative")

                if end <= start:
                    reasons.append("end must be after start")

                if not reasons:
                    valid.append({
                        "id": sid,
                        "start": start,
                        "end": end,
                        "value": value
                    })
                else:
                    rejected.append({"id": sid, "reasons": reasons})

            except (ValueError, TypeError):
                reasons.append("invalid timestamp format")
                rejected.append({"id": sid, "reasons": reasons})

    return valid, rejected

def weighted_interval_scheduling(sessions):
    """Dynamic programming solution for weighted interval scheduling.
    Returns (max_value, selected_ids) with tie-breaking rules."""

    if not sessions:
        return 0, []

    # Sort sessions by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Precompute p(i) - the last session that doesn't overlap with session i
    p = [-1] * n
    for i in range(n):
        for j in range(i-1, -1, -1):
            if sorted_sessions[j]["end"] <= sorted_sessions[i]["start"]:
                p[i] = j
                break

    # DP arrays: store max value and the choice (pick or skip)
    dp = [0] * (n + 1)  # dp[i] is max value for first i sessions (0-indexed)
    choice = [False] * n  # choice[i] = True if we pick session i in optimal solution

    for i in range(1, n + 1):
        # Option 1: skip session i-1
        skip_val = dp[i-1]

        # Option 2: pick session i-1
        pick_val = sorted_sessions[i-1]["value"] + (dp[p[i-1] + 1] if p[i-1] >= 0 else 0)

        if pick_val > skip_val:
            dp[i] = pick_val
            choice[i-1] = True
        elif pick_val < skip_val:
            dp[i] = skip_val
            choice[i-1] = False
        else:
            # Equal value - tie-breaking: fewer sessions, then lexicographically smaller
            # Compute number of sessions for both options
            # We need to reconstruct to compare
            pick_sessions = reconstruct(sorted_sessions, p, choice[:i-1] + [True], n, i-1)
            skip_sessions = reconstruct(sorted_sessions, p, choice[:i-1] + [False], n, i-1)

            # For the skip option, we need to consider the optimal solution for first i-1
            skip_opt = reconstruct_optimal(sorted_sessions, p, dp, i-1)

            # Recompute both solutions properly
            # Pick option
            pick_sessions_list = []
            if pick_val == sorted_sessions[i-1]["value"] + (dp[p[i-1] + 1] if p[i-1] >= 0 else 0):
                pick_sessions_list = [sorted_sessions[i-1]["id"]]
                if p[i-1] >= 0:
                    prev_ids = reconstruct_optimal(sorted_sessions, p, dp, p[i-1] + 1)
                    pick_sessions_list = prev_ids + pick_sessions_list

            # Skip option (optimal from first i-1)
            skip_sessions_list = reconstruct_optimal(sorted_sessions, p, dp, i-1)

            # Apply tie-breaking
            if len(pick_sessions_list) < len(skip_sessions_list):
                dp[i] = pick_val
                choice[i-1] = True
            elif len(pick_sessions_list) > len(skip_sessions_list):
                dp[i] = skip_val
                choice[i-1] = False
            else:
                # Same number of sessions - lexicographic comparison
                if pick_sessions_list < skip_sessions_list:
                    dp[i] = pick_val
                    choice[i-1] = True
                else:
                    dp[i] = skip_val
                    choice[i-1] = False

    # Reconstruct the optimal solution
    max_value = dp[n]
    selected_ids = reconstruct_optimal(sorted_sessions, p, dp, n)

    return max_value, selected_ids

def reconstruct_optimal(sessions, p, dp, n):
    """Reconstruct optimal solution for first n sessions (0-indexed)."""
    if n == 0:
        return []

    i = n - 1
    pick_val = sessions[i]["value"] + (dp[p[i] + 1] if p[i] >= 0 else 0)
    skip_val = dp[i]

    if pick_val > skip_val:
        # Pick session i
        prev_ids = reconstruct_optimal(sessions, p, dp, p[i] + 1) if p[i] >= 0 else []
        return prev_ids + [sessions[i]["id"]]
    elif pick_val < skip_val:
        # Skip session i
        return reconstruct_optimal(sessions, p, dp, i)
    else:
        # Equal - apply tie-breaking
        pick_ids = reconstruct_optimal(sessions, p, dp, p[i] + 1) + [sessions[i]["id"]] if p[i] >= 0 else [sessions[i]["id"]]
        skip_ids = reconstruct_optimal(sessions, p, dp, i)

        if len(pick_ids) < len(skip_ids):
            return pick_ids
        elif len(pick_ids) > len(skip_ids):
            return skip_ids
        else:
            # Same length, lexicographic order
            return pick_ids if pick_ids < skip_ids else skip_ids

def reconstruct(sessions, p, choice, n, last_idx):
    """Reconstruct session IDs based on choices (for tie-breaking)."""
    ids = []
    i = last_idx
    while i >= 0:
        if choice[i]:
            ids.append(sessions[i]["id"])
            i = p[i]
        else:
            i -= 1
    ids.reverse()
    return ids

def solve(input_data):
    """Main solving function."""
    sessions = input_data.get("sessions", [])
    valid_sessions, rejected_entries = validate_sessions(sessions)

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected_entries
    }

    return result

def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Simple case
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 3}
        ]
    }
    result = solve(input_data)
    assert result["max_value"] == 5, f"Expected 5, got {result['max_value']}"
    assert result["selected_ids"] == ["a"], f"Expected ['a'], got {result['selected_ids']}"
    assert result["rejected"] == [], f"Expected no rejected, got {result['rejected']}"
    tests_passed += 1

    # Test 2: Non-overlapping
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    result = solve(input_data)
    assert result["max_value"] == 12, f"Expected 12, got {result['max_value']}"
    assert result["selected_ids"] == ["a", "b", "c"], f"Expected ['a','b','c'], got {result['selected_ids']}"
    tests_passed += 1

    # Test 3: Reject invalid sessions
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "bad1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10}
        ]
    }
    result = solve(input_data)
    assert result["max_value"] == 10, f"Expected 10, got {result['max_value']}"
    assert result["selected_ids"] == ["good"], f"Expected ['good'], got {result['selected_ids']}"
    assert len(result["rejected"]) == 2, f"Expected 2 rejected, got {len(result['rejected'])}"
    tests_passed += 1

    # Test 4: Tie-breaking (equal value, fewer sessions)
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    result = solve(input_data)
    # Options: [a,b] value=10, [c] value=10 - choose fewer sessions
    assert result["selected_ids"] == ["c"], f"Expected ['c'], got {result['selected_ids']}"
    tests_passed += 1

    # Test 5: Tie-breaking (equal value, same sessions count, lexicographic)
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            # Alternative: [a,b] value=10 (a,b non-overlapping if a starts at 11 and b ends at 10)
            # Actually let's make a proper tie
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    # Sessions: b(9-10,5), c(10-11,5), a(11-12,5) => [b,c,a] value=15
    # x(9-11,10) => [a,x]? No, a starts at 11, x ends 11, so [x,a] value=15
    # Both have 2 sessions: compare ['a','x'] vs ['b','c','a'] - different count, not tie.
    # Let's make a proper tie:
    # b(9-10,5), a(10-11,5) vs c(9-11,10) - 2 vs 1 session, choose 1.
    # For lexicographic tie:
    input_data = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 15}
        ]
    }
    result = solve(input_data)
    # [a,b,c] value=15, [d] value=15 -> choose [d] (fewer sessions)
    assert result["selected_ids"] == ["d"], f"Expected ['d'], got {result['selected_ids']}"
    tests_passed += 1

    # Test 6: Empty input
    total_tests += 1
    input_data = {"sessions": []}
    result = solve(input_data)
    assert result["max_value"] == 0, f"Expected 0, got {result['max_value']}"
    assert result["selected_ids"] == [], f"Expected [], got {result['selected_ids']}"
    assert result["rejected"] == [], f"Expected [], got {result['rejected']}"
    tests_passed += 1

    # Test 7: Missing fields
    total_tests += 1
    input_data = {
        "sessions": [
            {"id": "missing", "start": "2026-05-01T09:00:00", "value": 5}
        ]
    }
    result = solve(input_data)
    assert len(result["rejected"]) == 1, f"Expected 1 rejected, got {len(result['rejected'])}"
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        input_data = json.load(sys.stdin)
        result = solve(input_data)
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {str(e)}"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```
````
