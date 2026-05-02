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
- Elapsed seconds: 22.249502
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3021, "completion_tokens": 2727, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2727
- Total tokens: 3021

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

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate and separate valid and rejected sessions."""
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get("id", "unknown")
        errors = []
        if "start" not in session or "end" not in session:
            errors.append("Missing start or end")
        else:
            try:
                start = parse_timestamp(session["start"])
                end = parse_timestamp(session["end"])
                if end <= start:
                    errors.append("End not after start")
            except (ValueError, TypeError):
                errors.append("Invalid timestamp format")

        if "value" not in session:
            errors.append("Missing value")
        elif not isinstance(session["value"], (int, float)) or session["value"] < 0:
            errors.append("Negative or invalid value")

        if errors:
            rejected.append({"id": sid, "reason": "; ".join(errors)})
        else:
            valid.append({
                "id": sid,
                "start": start,
                "end": end,
                "value": session["value"]
            })
    return valid, rejected

def schedule_sessions(sessions):
    """Weighted interval scheduling with tie-breaking."""
    if not sessions:
        return 0, [], []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Precompute p[j] - last non-overlapping session index
    p = [-1] * n
    for j in range(n):
        for i in range(j-1, -1, -1):
            if sorted_sessions[i]["end"] <= sorted_sessions[j]["start"]:
                p[j] = i
                break

    # DP arrays: dp[j] = max value up to j, choice[j] = selected or not
    dp = [0] * (n + 1)  # dp[0] = 0 (no sessions)
    choice = [False] * (n + 1)  # choice[j] = True if session j-1 is selected

    # For tie-breaking: store detailed solutions for dp[j]
    # We'll reconstruct with tie-breaking rules afterward

    for j in range(1, n + 1):
        idx = j - 1
        include_val = sorted_sessions[idx]["value"] + dp[p[idx] + 1]
        exclude_val = dp[j - 1]

        if include_val > exclude_val:
            dp[j] = include_val
            choice[j] = True
        elif include_val < exclude_val:
            dp[j] = exclude_val
            choice[j] = False
        else:
            # Tie: compare number of sessions and lexicographic order
            include_sessions = reconstruct_solution(sorted_sessions, p, choice, j, True)
            exclude_sessions = reconstruct_solution(sorted_sessions, p, choice, j, False)

            if len(include_sessions) < len(exclude_sessions):
                dp[j] = include_val
                choice[j] = True
            elif len(include_sessions) > len(exclude_sessions):
                dp[j] = exclude_val
                choice[j] = False
            else:
                # Same length: lexicographic comparison of IDs
                include_ids = sorted([s["id"] for s in include_sessions])
                exclude_ids = sorted([s["id"] for s in exclude_sessions])
                if include_ids < exclude_ids:
                    dp[j] = include_val
                    choice[j] = True
                else:
                    dp[j] = exclude_val
                    choice[j] = False

    # Reconstruct optimal solution
    selected = reconstruct_solution(sorted_sessions, p, choice, n, choice[n])
    selected_sorted = sorted(selected, key=lambda x: x["start"])
    selected_ids = [s["id"] for s in selected_sorted]

    return dp[n], selected_ids, []

def reconstruct_solution(sorted_sessions, p, choice, j, choose_j):
    """Reconstruct sessions for subproblem j."""
    if j == 0:
        return []

    idx = j - 1
    if choose_j:
        return [sorted_sessions[idx]] + reconstruct_solution(sorted_sessions, p, choice, p[idx] + 1, choice[p[idx] + 1])
    else:
        return reconstruct_solution(sorted_sessions, p, choice, j - 1, choice[j - 1])

def optimize_schedule(input_data):
    """Main optimization function."""
    sessions = input_data.get("sessions", [])
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids, _ = schedule_sessions(valid)

    # Separate rejected with reasons
    rejected_output = []
    for r in rejected:
        rejected_output.append({"id": r["id"], "reason": r["reason"]})

    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected_output
    }
    return output

def run_tests():
    """Run built-in tests."""
    test_cases = [
        # Test 1: Basic case
        {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 3},
                {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T11:00:00", "value": 4}
            ],
            "expected_max": 8,
            "expected_ids": ["a", "b"]
        },
        # Test 2: Simple non-overlapping
        {
            "sessions": [
                {"id": "x", "start": "2026-05-01T08:00:00", "end": "2026-05-01T09:00:00", "value": 2},
                {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
                {"id": "z", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4}
            ],
            "expected_max": 9,
            "expected_ids": ["x", "y", "z"]
        },
        # Test 3: Overlapping with higher value
        {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
                {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 6},
                {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 5}
            ],
            "expected_max": 10,
            "expected_ids": ["a"]
        },
        # Test 4: Tie-breaking (same value, different counts)
        {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5}
            ],
            "expected_max": 5,
            "expected_ids": ["a", "b"]  # two sessions vs one, so choose two (same total value)
        },
        # Test 5: Tie-breaking lexicographic
        {
            "sessions": [
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 4},
                {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 4}
            ],
            "expected_max": 4,
            "expected_ids": ["a", "b"]  # ["a","b"] < ["b","c"] lexicographically? Actually ["a","b"] vs ["c"] -> fewer sessions, so ["a","b"] wins
        },
        # Test 6: Reject invalid sessions
        {
            "sessions": [
                {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "bad_end", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 3},
                {"id": "negative_val", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -1}
            ],
            "expected_max": 5,
            "expected_ids": ["good"],
            "expected_rejected_count": 2
        },
        # Test 7: Empty input
        {
            "sessions": [],
            "expected_max": 0,
            "expected_ids": []
        }
    ]

    all_passed = True
    for i, test in enumerate(test_cases):
        result = optimize_schedule(test)
        max_ok = result["max_value"] == test["expected_max"]
        ids_ok = result["selected_ids"] == test["expected_ids"]
        rejected_ok = True
        if "expected_rejected_count" in test:
            rejected_ok = len(result["rejected"]) == test["expected_rejected_count"]

        if not (max_ok and ids_ok and rejected_ok):
            print(f"Test {i+1} FAILED:")
            print(f"  Expected max: {test['expected_max']}, got: {result['max_value']}")
            print(f"  Expected ids: {test['expected_ids']}, got: {result['selected_ids']}")
            if "expected_rejected_count" in test:
                print(f"  Expected rejected count: {test['expected_rejected_count']}, got: {len(result['rejected'])}")
            all_passed = False

    if all_passed:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed.")
        return 1

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        sys.exit(run_tests())
    else:
        try:
            input_data = json.load(sys.stdin)
            output = optimize_schedule(input_data)
            print(json.dumps(output, indent=2))
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
            sys.exit(1)

if __name__ == "__main__":
    main()
```
````
