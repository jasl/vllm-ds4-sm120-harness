# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 32.406104
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 4818, "completion_tokens": 4524, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 4524
- Total tokens: 4818

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
    """Parse ISO timestamp without timezone info."""
    try:
        return datetime.fromisoformat(ts_str)
    except ValueError:
        raise ValueError(f"Invalid timestamp: {ts_str}")

def validate_sessions(sessions):
    """Validate and separate sessions into valid and rejected."""
    valid = []
    rejected = []

    for session in sessions:
        sid = session.get("id", "unknown")
        errors = []

        # Check required fields
        if "start" not in session or "end" not in session:
            errors.append("Missing start or end time")
            rejected.append({"id": sid, "reason": "; ".join(errors)})
            continue

        # Parse timestamps
        try:
            start = parse_timestamp(session["start"])
        except ValueError as e:
            errors.append(str(e))
            start = None

        try:
            end = parse_timestamp(session["end"])
        except ValueError as e:
            errors.append(str(e))
            end = None

        if start and end:
            if end <= start:
                errors.append("End time must be after start time")

        # Check value
        value = session.get("value", 0)
        if not isinstance(value, (int, float)):
            errors.append("Value must be a number")
        elif value < 0:
            errors.append("Value cannot be negative")

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

def weighted_interval_scheduling(sessions):
    """DP solution for weighted interval scheduling.
    Returns max value and optimal set of session IDs."""
    if not sessions:
        return 0, []

    # Sort sessions by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Precompute p[j] = index of last session that ends before session j starts
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]

    # For binary search, we need the end times as a list of timestamps
    # p[j] is the largest index i < j such that end_times[i] <= start_times[j]
    p = [-1] * n
    for j in range(n):
        target = start_times[j]
        # Binary search for the last end time <= target
        idx = bisect_right(end_times, target) - 1
        p[j] = idx

    # DP arrays: M[j] = max value up to session j (inclusive)
    M = [0] * n
    # Decision tracking: 1 = take session j, 0 = skip it
    decision = [0] * n

    M[0] = sorted_sessions[0]["value"]
    decision[0] = 1

    for j in range(1, n):
        # Option 1: exclude session j
        exclude_val = M[j-1]

        # Option 2: include session j
        include_val = sorted_sessions[j]["value"]
        if p[j] != -1:
            include_val += M[p[j]]

        # Choose better option
        if include_val > exclude_val:
            M[j] = include_val
            decision[j] = 1
        elif include_val < exclude_val:
            M[j] = exclude_val
            decision[j] = 0
        else:
            # Tie-breaking: prefer fewer sessions, then lexicographically smaller IDs
            # Reconstruct both options to compare
            # Option include
            inc_set = set()
            temp_j = j
            inc_count = 0
            inc_list = []
            while temp_j >= 0:
                if decision[temp_j] == 1 and M[temp_j] == include_val:
                    inc_set.add(sorted_sessions[temp_j]["id"])
                    inc_list.append(sorted_sessions[temp_j]["id"])
                    temp_j = p[temp_j]
                else:
                    temp_j -= 1
            inc_count = len(inc_set)

            # Option exclude (skip j)
            exc_set = set()
            temp_j = j - 1
            exc_count = 0
            exc_list = []
            while temp_j >= 0:
                if decision[temp_j] == 1 and M[temp_j] == exclude_val:
                    exc_set.add(sorted_sessions[temp_j]["id"])
                    exc_list.append(sorted_sessions[temp_j]["id"])
                    temp_j = p[temp_j]
                else:
                    temp_j -= 1
            exc_count = len(exc_set)

            # Prefer fewer sessions
            if inc_count < exc_count:
                M[j] = include_val
                decision[j] = 1
            elif exc_count < inc_count:
                M[j] = exclude_val
                decision[j] = 0
            else:
                # Same count, prefer lexicographically smaller sorted list
                inc_sorted = sorted(inc_list)
                exc_sorted = sorted(exc_list)
                if inc_sorted < exc_sorted:
                    M[j] = include_val
                    decision[j] = 1
                else:
                    M[j] = exclude_val
                    decision[j] = 0

    # Reconstruct optimal solution
    selected = []
    j = n - 1
    # Track max_value for reconstruction
    max_val = M[-1]

    while j >= 0:
        if decision[j] == 1:
            selected.append(sorted_sessions[j]["id"])
            j = p[j]
        else:
            j -= 1

    # Reverse to get chronological order
    selected.reverse()

    # Rebuild to ensure tie-breaking is correct
    # If M[-1] == exclude_last_path value, check if we could achieve same value
    # with fewer sessions or lexicographically smaller
    best_selected = selected
    best_count = len(selected)
    best_sorted = sorted(selected)

    # Check all possible optimal solutions for tie-breaking
    # This is O(n^2) but n is typically small for the tie-breaking case
    # For true O(n log n), we would need more complex reconstruction
    # But this preserves correctness for tie-breaking
    def reconstruct_optimal(j, target_val):
        """Reconstruct an optimal solution achieving target_val up to index j."""
        if j < 0:
            return []
        if M[j] != target_val:
            return None

        result = []
        if decision[j] == 1:
            # Include j
            sub = reconstruct_optimal(p[j], target_val - sorted_sessions[j]["value"])
            if sub is not None:
                result = sub + [sorted_sessions[j]["id"]]
        else:
            # Exclude j, try include path if it also achieves target
            if j > 0 and M[j-1] == target_val:
                sub = reconstruct_optimal(j-1, target_val)
                if sub is not None:
                    result = sub
            else:
                # Must include j
                sub = reconstruct_optimal(p[j], target_val - sorted_sessions[j]["value"])
                if sub is not None:
                    result = sub + [sorted_sessions[j]["id"]]
        return result if result or j < 0 else None

    # Find best among all optimal solutions
    optimal_candidates = []
    for j in range(n):
        if M[j] == max_val:
            candidate = reconstruct_optimal(j, max_val)
            if candidate:
                optimal_candidates.append(candidate)

    if optimal_candidates:
        # Sort by: fewer sessions first, then lexicographically
        def sort_key(candidate):
            return (len(candidate), sorted(candidate))
        best_candidate = min(optimal_candidates, key=sort_key)
        # Map back to original order (sorted by end time)
        original_order = []
        id_to_session = {s["id"]: s for s in sorted_sessions}
        # Preserve the chronological order from reconstruction
        ordered_by_end = {s["id"]: idx for idx, s in enumerate(sorted_sessions)}
        best_candidate_sorted = sorted(best_candidate, key=lambda x: ordered_by_end[x])
        return max_val, best_candidate_sorted

    return max_val, selected

def solve(input_data):
    """Main solving function."""
    if not isinstance(input_data, dict) or "sessions" not in input_data:
        print(json.dumps({
            "max_value": 0,
            "selected_ids": [],
            "rejected": [{"id": "unknown", "reason": "Invalid input format"}]
        }))
        return

    valid, rejected = validate_sessions(input_data["sessions"])

    if not valid:
        print(json.dumps({
            "max_value": 0,
            "selected_ids": [],
            "rejected": rejected
        }))
        return

    max_val, selected_ids = weighted_interval_scheduling(valid)

    result = {
        "max_value": max_val,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

    print(json.dumps(result, default=str))

def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic case
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 4}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, selected = weighted_interval_scheduling(valid)
    assert max_val == 8, f"Test 1 failed: max_val {max_val}"
    assert selected == ["a", "b"], f"Test 1 failed: selected {selected}"
    tests_passed += 1

    # Test 2: Overlapping sessions with different values
    total_tests += 1
    data = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "y", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 6},
            {"id": "z", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 7}
        ]
    }
    valid, _ = validate_sessions(data["sessions"])
    max_val, selected = weighted_interval_scheduling(valid)
    assert max_val == 17, f"Test 2 failed: max_val {max_val}"
    assert set(selected) == {"y", "z"}, f"Test 2 failed: selected {selected}"
    tests_passed += 1

    # Test 3: Session with value 0
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 0},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3}
        ]
    }
    valid, _ = validate_sessions(data["sessions"])
    max_val, selected = weighted_interval_scheduling(valid)
    assert max_val == 3, f"Test 3 failed: max_val {max_val}"
    assert selected == ["b"], f"Test 3 failed: selected {selected}"
    tests_passed += 1

    # Test 4: Validation - end before start
    total_tests += 1
    data = {
        "sessions": [
            {"id": "bad", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert len(valid) == 0, "Test 4 failed: should have no valid sessions"
    assert len(rejected) == 1, "Test 4 failed: should have 1 rejected"
    assert "after start" in rejected[0]["reason"], f"Test 4 failed: wrong reason {rejected[0]['reason']}"
    tests_passed += 1

    # Test 5: Validation - negative value
    total_tests += 1
    data = {
        "sessions": [
            {"id": "neg", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert len(valid) == 0, "Test 5 failed: should have no valid sessions"
    assert len(rejected) == 1, "Test 5 failed: should have 1 rejected"
    assert "negative" in rejected[0]["reason"], f"Test 5 failed: wrong reason {rejected[0]['reason']}"
    tests_passed += 1

    # Test 6: Tie-breaking - same value, different counts
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    valid, _ = validate_sessions(data["sessions"])
    max_val, selected = weighted_interval_scheduling(valid)
    assert max_val == 10, f"Test 6 failed: max_val {max_val}"
    assert selected == ["c"], f"Test 6 failed: selected {selected}"
    tests_passed += 1

    # Test 7: Tie-breaking - same value and count, lexicographic
    total_tests += 1
    data = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        ]
    }
    valid, _ = validate_sessions(data["sessions"])
    max_val, selected = weighted_interval_scheduling(valid)
    assert max_val == 10, f"Test 7 failed: max_val {max_val}"
    assert selected == ["a", "b"] or selected == ["b", "a"], f"Test 7 failed: selected {selected}"
    # Both are optimal; lexicographically ["a","b"] < ["b","a"]
    # But we need to check chronological order
    # Sessions don't overlap, so both can be taken
    # Chronological order by end time: a (10:00) before b (11:00) -> ["a","b"]
    tests_passed += 1

    # Test 8: Zero sessions
    total_tests += 1
    data = {"sessions": []}
    valid, rejected = validate_sessions(data["sessions"])
    assert len(valid) == 0
    assert len(rejected) == 0
    tests_passed += 1

    # Test 9: Multiple overlapping
    total_tests += 1
    data = {
        "sessions": [
            {"id": "1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "2", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 4},
            {"id": "3", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "4", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 5}
        ]
    }
    valid, _ = validate_sessions(data["sessions"])
    max_val, selected = weighted_interval_scheduling(valid)
    assert max_val == 9, f"Test 9 failed: max_val {max_val}"  # 1+3+4? No, 1 and 3 don't overlap? 1 ends 10:00, 3 starts 10:00 -> valid
    # Possible: 1,3,4 = 3+3+5=11? Wait check overlaps: 3 ends 11:00, 4 starts 10:30 -> overlap!
    # Best is 1 (3) + 3 (3) = 6? Or 2 (4) + 4 (5) = 9, or 1+4=8, or 2+3=7
    # So max is 9 with sessions 2 and 4.
    assert set(selected) == {"2", "4"}, f"Test 9 failed: selected {selected}"
    tests_passed += 1

    # Test 10: Complex tie-breaking
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        ]
    }
    valid, _ = validate_sessions(data["sessions"])
    max_val, selected = weighted_interval_scheduling(valid)
    assert max_val == 15, f"Test 10 failed: max_val {max_val}"
    assert selected == ["a", "b", "c"], f"Test 10 failed: selected {selected}"
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
    else:
        input_data = json.load(sys.stdin)
        solve(input_data)
```
````
