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
- Elapsed seconds: 9.767311
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3089, "completion_tokens": 2795, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2795
- Total tokens: 3089

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
from datetime import datetime, date

def parse_time(s):
    """Parse ISO-like timestamp without timezone info."""
    # Handle both 'T' and space separators, with optional fractional seconds
    s = s.strip().replace(' ', 'T')
    if '.' in s:
        # Remove fractional seconds beyond 6 digits (microseconds)
        base, frac = s.split('.')
        frac = frac.rstrip('Zz')[:6].ljust(6, '0')
        s = f"{base}.{frac}"
    else:
        s = s.rstrip('Zz')
    return datetime.fromisoformat(s)

class Session:
    def __init__(self, id, start, end, value):
        self.id = id
        self.start = parse_time(start)
        self.end = parse_time(end)
        self.value = value

    def __repr__(self):
        return f"Session({self.id}, {self.start}, {self.end}, {self.value})"

def validate_sessions(sessions_data):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []

    for idx, s in enumerate(sessions_data):
        reasons = []

        # Check required fields
        if 'id' not in s or 'start' not in s or 'end' not in s or 'value' not in s:
            reasons.append("missing required fields")
        else:
            # Validate value
            try:
                value = float(s['value'])
                if value < 0:
                    reasons.append("negative value")
                elif value != int(value):
                    # Allow only integer values for simplicity (or could keep float)
                    reasons.append("non-integer value")
                else:
                    value = int(value)
            except (ValueError, TypeError):
                reasons.append("invalid value")
                value = None

            # Parse timestamps
            try:
                start = parse_time(s['start'])
            except (ValueError, TypeError):
                reasons.append("invalid start timestamp")
                start = None

            try:
                end = parse_time(s['end'])
            except (ValueError, TypeError):
                reasons.append("invalid end timestamp")
                end = None

            # Check chronological order
            if start and end:
                if end <= start:
                    reasons.append("end not after start")

        if not reasons:
            try:
                value = int(float(s['value']))
                parsed = Session(s['id'], s['start'], s['end'], value)
                valid.append(parsed)
            except Exception as e:
                reasons.append(f"parse error: {str(e)}")
                rejected.append({"id": s.get('id', f'entry_{idx}'), "reasons": reasons})
        else:
            rejected.append({"id": s.get('id', f'entry_{idx}'), "reasons": reasons})

    return valid, rejected

def weighted_interval_scheduling(sessions):
    """DP solution for weighted interval scheduling. Returns (max_value, selected_ids)."""
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s.end)
    n = len(sorted_sessions)

    # Precompute p[j] = index of last session that ends before session j starts
    p = [-1] * n
    for j in range(n):
        for i in range(j-1, -1, -1):
            if sorted_sessions[i].end <= sorted_sessions[j].start:
                p[j] = i
                break

    # DP: dp[j] = max value using first j+1 sessions (0-indexed)
    dp = [0] * n
    dp[0] = sorted_sessions[0].value

    for j in range(1, n):
        include = sorted_sessions[j].value
        if p[j] != -1:
            include += dp[p[j]]
        exclude = dp[j-1]
        dp[j] = max(include, exclude)

    max_value = dp[-1]

    # Reconstruct with tie-breaking: fewer sessions, then lexicographically smaller IDs
    # We'll do backward reconstruction collecting all optimal sets, then pick best
    def reconstruct_all(idx):
        """Recursively collect all optimal solutions ending at index idx."""
        if idx < 0:
            return [[]]  # list of lists of IDs

        solutions = []

        # Case 1: exclude this session
        if idx == 0:
            exclude_opt = 0
        else:
            exclude_opt = dp[idx-1]

        if dp[idx] == exclude_opt:
            sub_solutions = reconstruct_all(idx-1)
            solutions.extend(sub_solutions)

        # Case 2: include this session
        include_val = sorted_sessions[idx].value
        if p[idx] != -1:
            include_val += dp[p[idx]]

        if dp[idx] == include_val:
            sub_solutions = reconstruct_all(p[idx])
            for sub in sub_solutions:
                solutions.append(sub + [sorted_sessions[idx].id])

        return solutions

    all_solutions = reconstruct_all(n-1)

    # Deduplicate (convert to tuple for hashing)
    unique_solutions = set(tuple(sol) for sol in all_solutions)

    # Select best: fewer sessions, then lexicographically smaller
    def solution_key(sol):
        return (len(sol), list(sol))

    best_solution = min(unique_solutions, key=solution_key)

    return max_value, list(best_solution)

def process_input(data):
    """Process input data and return output dict."""
    sessions_data = data.get('sessions', [])
    valid_sessions, rejected = validate_sessions(sessions_data)

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    # Sort selected IDs chronologically by their session start times
    session_map = {s.id: s for s in valid_sessions}
    selected_ids.sort(key=lambda x: session_map[x].start)

    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    return output

def run_tests():
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Simple case
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 3}
        ]
    }
    result = process_input(data)
    assert result["max_value"] == 5, f"Test 1 max_value failed: {result['max_value']}"
    assert result["selected_ids"] == ["a"], f"Test 1 selected_ids failed: {result['selected_ids']}"
    assert result["rejected"] == [], f"Test 1 rejected failed: {result['rejected']}"
    tests_passed += 1

    # Test 2: Overlapping sessions
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a1", "start": "2026-05-01 09:00:00", "end": "2026-05-01 11:00:00", "value": 10},
            {"id": "b1", "start": "2026-05-01 10:00:00", "end": "2026-05-01 12:00:00", "value": 8},
            {"id": "c1", "start": "2026-05-01 11:00:00", "end": "2026-05-01 13:00:00", "value": 7}
        ]
    }
    result = process_input(data)
    assert result["max_value"] == 17, f"Test 2 max_value failed: {result['max_value']}"
    assert set(result["selected_ids"]) == {"a1", "c1"}, f"Test 2 selected_ids failed: {result['selected_ids']}"
    tests_passed += 1

    # Test 3: Rejected sessions
    total_tests += 1
    data = {
        "sessions": [
            {"id": "good", "start": "2026-05-01T09:00", "end": "2026-05-01T10:00", "value": 5},
            {"id": "bad_end", "start": "2026-05-01T10:00", "end": "2026-05-01T09:00", "value": 3},
            {"id": "neg_val", "start": "2026-05-01T11:00", "end": "2026-05-01T12:00", "value": -2}
        ]
    }
    result = process_input(data)
    assert result["max_value"] == 5, f"Test 3 max_value failed: {result['max_value']}"
    assert len(result["rejected"]) == 2, f"Test 3 rejected count failed: {len(result['rejected'])}"
    tests_passed += 1

    # Test 4: Tie-breaking - fewer sessions
    total_tests += 1
    data = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00", "end": "2026-05-01T12:00", "value": 10},
            {"id": "y", "start": "2026-05-01T09:00", "end": "2026-05-01T10:00", "value": 5},
            {"id": "z", "start": "2026-05-01T10:00", "end": "2026-05-01T12:00", "value": 5}
        ]
    }
    result = process_input(data)
    # Both {y, z} (2 sessions, value 10) and {x} (1 session, value 10) are optimal
    # Fewer sessions wins, so should pick {x}
    assert result["max_value"] == 10, f"Test 4 max_value failed: {result['max_value']}"
    assert result["selected_ids"] == ["x"], f"Test 4 selected_ids failed: {result['selected_ids']}"
    tests_passed += 1

    # Test 5: Tie-breaking - lexicographically smaller
    total_tests += 1
    data = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00", "end": "2026-05-01T10:00", "value": 10},
            {"id": "a", "start": "2026-05-01T10:00", "end": "2026-05-01T11:00", "value": 10}
        ]
    }
    result = process_input(data)
    # Both sessions have same value, but they don't overlap, so both are selected
    assert result["max_value"] == 20, f"Test 5 max_value failed: {result['max_value']}"
    assert result["selected_ids"] == ["b", "a"], f"Test 5 selected_ids failed: {result['selected_ids']}"
    tests_passed += 1

    # Test 6: Empty input
    total_tests += 1
    data = {"sessions": []}
    result = process_input(data)
    assert result["max_value"] == 0, f"Test 6 max_value failed: {result['max_value']}"
    assert result["selected_ids"] == [], f"Test 6 selected_ids failed: {result['selected_ids']}"
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    result = process_input(data)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
```
````
