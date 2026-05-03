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
- Elapsed seconds: 57.448732
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3942, "completion_tokens": 3648, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3648
- Total tokens: 3942

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
    """Parse ISO-like timestamp without timezone info."""
    # Remove trailing Z if present, as we don't handle timezones
    ts_str = ts_str.rstrip('Z')
    return datetime.fromisoformat(ts_str)

def is_valid_session(session):
    """Check if session has valid id, start < end, and non-negative value."""
    try:
        sid = session.get("id")
        start_str = session.get("start")
        end_str = session.get("end")
        value = session.get("value")

        if not isinstance(sid, str) or not sid:
            return False, "Invalid or missing id"
        if not isinstance(start_str, str) or not isinstance(end_str, str):
            return False, "Missing start or end"

        start = parse_timestamp(start_str)
        end = parse_timestamp(end_str)

        if not isinstance(value, (int, float)) or value < 0:
            return False, "Negative or invalid value"
        if end <= start:
            return False, "End must be after start"

        return True, None
    except (ValueError, TypeError):
        return False, "Invalid date format"

def find_last_non_conflicting(sessions, index):
    """Binary search for last session that ends before sessions[index] starts."""
    lo, hi = 0, index - 1
    target_start = sessions[index]['start']
    while lo <= hi:
        mid = (lo + hi) // 2
        if sessions[mid]['end'] <= target_start:
            if mid == index - 1 or sessions[mid + 1]['end'] > target_start:
                return mid
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def weighted_interval_scheduling(sessions):
    """DP for weighted interval scheduling. Returns (max_value, selected_indices)."""
    if not sessions:
        return 0, []

    n = len(sessions)
    # Precompute p[i] = last non-conflicting session index before i
    p = [-1] * n
    for i in range(n):
        p[i] = find_last_non_conflicting(sessions, i)

    # DP arrays: dp[i] = max value up to session i
    dp = [0] * n
    dp[0] = sessions[0]['value']

    for i in range(1, n):
        incl_val = sessions[i]['value']
        if p[i] != -1:
            incl_val += dp[p[i]]
        excl_val = dp[i - 1]

        if incl_val > excl_val:
            dp[i] = incl_val
        elif incl_val < excl_val:
            dp[i] = excl_val
        else:
            # tie: prefer fewer sessions, then lexicographically smaller IDs
            # Reconstruct both options to compare
            incl_indices = reconstruct(sessions, p, dp, i, take=i)
            excl_indices = reconstruct(sessions, p, dp, i, take=None)

            incl_count = len(incl_indices)
            excl_count = len(excl_indices)

            if incl_count < excl_count:
                dp[i] = incl_val
            elif incl_count > excl_count:
                dp[i] = excl_val
            else:
                # same count: compare lexicographically
                incl_ids = [sessions[idx]['id'] for idx in incl_indices]
                excl_ids = [sessions[idx]['id'] for idx in excl_indices]
                if incl_ids < excl_ids:
                    dp[i] = incl_val
                else:
                    dp[i] = excl_val

    max_val = dp[-1]
    selected = reconstruct(sessions, p, dp, n - 1, take=None)
    return max_val, selected

def reconstruct(sessions, p, dp, i, take=None):
    """Reconstruct solution up to index i. If take is given, force taking session i."""
    result = []
    while i >= 0:
        if take == i:
            result.append(i)
            i = p[i]
            take = None
        else:
            incl_val = sessions[i]['value']
            if p[i] != -1:
                incl_val += dp[p[i]]
            excl_val = dp[i - 1] if i > 0 else 0

            if incl_val > excl_val:
                result.append(i)
                i = p[i]
            elif incl_val < excl_val:
                i -= 1
            else:
                # tie: choose fewer sessions, then lexicographically smaller
                incl_indices = reconstruct(sessions, p, dp, i, take=i)
                excl_indices = reconstruct(sessions, p, dp, i - 1, take=None)

                incl_count = len(incl_indices)
                excl_count = len(excl_indices)

                if incl_count < excl_count:
                    result.extend(incl_indices)
                    break
                elif incl_count > excl_count:
                    i -= 1
                else:
                    incl_ids = [sessions[idx]['id'] for idx in incl_indices]
                    excl_ids = [sessions[idx]['id'] for idx in excl_indices]
                    if incl_ids < excl_ids:
                        result.extend(incl_indices)
                        break
                    else:
                        i -= 1
    result.reverse()
    return result

def solve(input_data):
    """Main solving function."""
    sessions_list = input_data.get("sessions", [])
    if not isinstance(sessions_list, list):
        sessions_list = []

    valid_sessions = []
    rejected = []

    for session in sessions_list:
        if not isinstance(session, dict):
            rejected.append({"id": None, "reason": "Invalid session format"})
            continue

        is_valid, reason = is_valid_session(session)
        if not is_valid:
            rejected.append({"id": session.get("id", None), "reason": reason})
            continue

        sid = session["id"]
        start = parse_timestamp(session["start"])
        end = parse_timestamp(session["end"])
        value = session["value"]

        valid_sessions.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value,
            "start_str": session["start"],
            "end_str": session["end"]
        })

    # Sort by end time
    valid_sessions.sort(key=lambda s: s["end"])

    max_value, selected_indices = weighted_interval_scheduling(valid_sessions)

    # Get selected IDs in chronological order (they already are due to DP reconstruction)
    selected_ids = [valid_sessions[i]["id"] for i in selected_indices]

    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

    return result

def run_tests():
    """Run built-in tests."""
    tests_passed = 0

    # Test 1: Basic case
    input1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 4}
        ]
    }
    result = solve(input1)
    assert result["max_value"] == 9, f"Expected 9, got {result['max_value']}"
    assert result["selected_ids"] == ["a", "c"], f"Expected ['a','c'], got {result['selected_ids']}"
    tests_passed += 1

    # Test 2: Reject invalid sessions
    input2 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10}
        ]
    }
    result = solve(input2)
    assert result["max_value"] == 10, f"Expected 10, got {result['max_value']}"
    assert result["selected_ids"] == ["z"], f"Expected ['z'], got {result['selected_ids']}"
    assert len(result["rejected"]) == 2, f"Expected 2 rejected, got {len(result['rejected'])}"
    tests_passed += 1

    # Test 3: Empty input
    input3 = {"sessions": []}
    result = solve(input3)
    assert result["max_value"] == 0, f"Expected 0, got {result['max_value']}"
    assert result["selected_ids"] == [], f"Expected [], got {result['selected_ids']}"
    tests_passed += 1

    # Test 4: Tie-breaking (fewer sessions)
    input4 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    result = solve(input4)
    # Options: [a,b] value=5+5=10 count=2, [c] value=5 count=1 -> value tie? No, [a,b] has higher value
    # Actually [a,b] = 10, [c] = 5, so max is 10 with [a,b]
    assert result["max_value"] == 10, f"Expected 10, got {result['max_value']}"
    assert result["selected_ids"] == ["a", "b"], f"Expected ['a','b'], got {result['selected_ids']}"
    tests_passed += 1

    # Test 5: Tie-breaking with equal values (both same value and count)
    input5 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    result = solve(input5)
    # [c] value=10, so no tie
    assert result["max_value"] == 10
    assert result["selected_ids"] == ["c"]
    tests_passed += 1

    # Test 6: Lexicographic tie-breaking
    input6 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ]
    }
    result = solve(input6)
    # Only possible: [b,a] value=10, [b,c] value=10? Wait b ends at 10, a starts at 10 -> non-overlap
    # Actually b:9-10, a:10-11, c:11-12 => they are all non-overlapping
    # Option1: [b,a] = 10, Option2: [b,c] = 10? b+c=10, a+c=10, b+a=10, b+a+c=15? No b+a+c=5+5+5=15
    # Actually all three are non-overlapping, so max is 15 with [b,a,c]
    # Let's make a case where two options have same value and count
    input6 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    result = solve(input6)
    # [c] value=10, [b,a] value=10 -> tie, same count (1 vs 2? no 1 vs 2) -> c wins with fewer sessions
    assert result["selected_ids"] == ["c"], f"Expected ['c'], got {result['selected_ids']}"
    tests_passed += 1

    # Test 7: Proper lexicographic tie with same count and value
    input7 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ]
    }
    result = solve(input7)
    # [x,y] value=10 count=2, [a,b] value=10 count=2 -> tie, lexicographically [a,b] < [x,y]
    assert result["selected_ids"] == ["a", "b"], f"Expected ['a','b'], got {result['selected_ids']}"
    tests_passed += 1

    print(f"All {tests_passed} tests passed!", file=sys.stderr)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        try:
            input_data = json.load(sys.stdin)
            result = solve(input_data)
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {str(e)}"}), file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
```
````
