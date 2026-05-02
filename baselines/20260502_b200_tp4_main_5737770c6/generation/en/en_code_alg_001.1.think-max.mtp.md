# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 7.693648
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2524, "completion_tokens": 2230, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2230
- Total tokens: 2524

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

def parse_sessions(sessions_data):
    """Parse and validate sessions, return (valid_sessions, rejected_sessions)."""
    valid = []
    rejected = []

    for session in sessions_data:
        sid = session.get("id", "unknown")
        start_str = session.get("start", "")
        end_str = session.get("end", "")
        value = session.get("value", 0)

        # Validate start/end format
        try:
            start = datetime.fromisoformat(start_str)
            end = datetime.fromisoformat(end_str)
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reason": "Invalid date format"})
            continue

        # Validate value
        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({"id": sid, "reason": "Negative or invalid value"})
            continue

        # Validate end after start
        if end <= start:
            rejected.append({"id": sid, "reason": "End not after start"})
            continue

        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })

    return valid, rejected

def optimize_schedule(valid_sessions):
    """Dynamic programming solution for weighted interval scheduling."""
    if not valid_sessions:
        return {"max_value": 0, "selected_ids": []}

    # Sort by end time
    sorted_sessions = sorted(valid_sessions, key=lambda s: s["end"])

    n = len(sorted_sessions)

    # Precompute p[i] = latest non-overlapping session index before i
    p = [-1] * n
    for i in range(n):
        for j in range(i - 1, -1, -1):
            if sorted_sessions[j]["end"] <= sorted_sessions[i]["start"]:
                p[i] = j
                break

    # DP arrays: dp[i] = max value up to session i
    dp = [0] * n
    for i in range(n):
        include = sorted_sessions[i]["value"] + (dp[p[i]] if p[i] >= 0 else 0)
        exclude = dp[i - 1] if i > 0 else 0
        dp[i] = max(include, exclude)

    max_value = dp[-1] if n > 0 else 0

    # Reconstruct solution with tie-breaking
    best_combinations = {}

    def reconstruct(i):
        """Returns list of session ids for optimal solution up to i."""
        if i < 0:
            return []
        if i == 0:
            include = sorted_sessions[0]["value"] + (dp[p[0]] if p[0] >= 0 else 0)
            exclude = 0
            if include > exclude:
                return [sorted_sessions[0]["id"]]
            else:
                return [] if include < exclude else []

        include_val = sorted_sessions[i]["value"] + (dp[p[i]] if p[i] >= 0 else 0)
        exclude_val = dp[i - 1]

        include_path = reconstruct(p[i]) + [sorted_sessions[i]["id"]]
        exclude_path = reconstruct(i - 1)

        if include_val > exclude_val:
            return include_path
        elif exclude_val > include_val:
            return exclude_path
        else:
            # Tie: fewer sessions, then lexicographically smaller
            if len(include_path) < len(exclude_path):
                return include_path
            elif len(exclude_path) < len(include_path):
                return exclude_path
            else:
                return min(include_path, exclude_path)

    selected_ids = reconstruct(n - 1)

    return {"max_value": max_value, "selected_ids": selected_ids}

def run_tests():
    """Run built-in tests."""
    test_cases = [
        # Test 1: Basic case
        (
            {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                    {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
                    {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
                ]
            },
            {"max_value": 9, "selected_ids": ["a", "c"]}
        ),
        # Test 2: Single session
        (
            {
                "sessions": [
                    {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10}
                ]
            },
            {"max_value": 10, "selected_ids": ["x"]}
        ),
        # Test 3: Overlapping with higher value
        (
            {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 8},
                    {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                    {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T12:00:00", "value": 5}
                ]
            },
            {"max_value": 10, "selected_ids": ["b", "c"]}
        ),
        # Test 4: Invalid sessions
        (
            {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
                    {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
                    {"id": "c", "start": "invalid", "end": "2026-05-01T10:00:00", "value": 3}
                ]
            },
            {"max_value": 0, "selected_ids": [], "rejected_count": 3}
        ),
        # Test 5: Empty input
        (
            {"sessions": []},
            {"max_value": 0, "selected_ids": []}
        ),
        # Test 6: Tie-breaking (fewer sessions)
        (
            {
                "sessions": [
                    {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                    {"id": "b", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 5},
                    {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T13:00:00", "value": 10}
                ]
            },
            {"max_value": 10, "selected_ids": ["c"]}
        ),
        # Test 7: Lexicographic tie-breaking
        (
            {
                "sessions": [
                    {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                    {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
                ]
            },
            {"max_value": 10, "selected_ids": ["a", "b"]}
        ),
    ]

    for i, (input_data, expected) in enumerate(test_cases):
        valid, rejected = parse_sessions(input_data["sessions"])
        result = optimize_schedule(valid)

        if "rejected_count" in expected:
            assert len(rejected) == expected["rejected_count"], f"Test {i+1} failed: rejected count mismatch"
        else:
            assert result["max_value"] == expected["max_value"], f"Test {i+1} failed: max_value {result['max_value']} != {expected['max_value']}"
            assert result["selected_ids"] == expected["selected_ids"], f"Test {i+1} failed: selected_ids {result['selected_ids']} != {expected['selected_ids']}"
            assert len(rejected) == 0, f"Test {i+1} failed: unexpected rejected sessions"

    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)

    sessions_data = data.get("sessions", [])
    valid_sessions, rejected_sessions = parse_sessions(sessions_data)

    result = optimize_schedule(valid_sessions)

    output = {
        "max_value": result["max_value"],
        "selected_ids": result["selected_ids"],
        "rejected": rejected_sessions
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
```
````
