# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 11.686173
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 2510, "completion_tokens": 2216, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 2216
- Total tokens: 2510

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
from copy import deepcopy

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get("id", "unknown")
        reasons = []
        # Check required fields
        if "start" not in sess or "end" not in sess or "value" not in sess:
            reasons.append("missing required field(s)")
        else:
            try:
                start = parse_timestamp(sess["start"])
                end = parse_timestamp(sess["end"])
                if end <= start:
                    reasons.append("end not after start")
                value = sess["value"]
                if not isinstance(value, (int, float)):
                    reasons.append("value is not a number")
                elif value < 0:
                    reasons.append("negative value")
            except (ValueError, TypeError):
                reasons.append("invalid timestamp format")

        if reasons:
            rejected.append({"id": sid, "reasons": reasons})
        else:
            valid.append({
                "id": sid,
                "start": start,
                "end": end,
                "value": value
            })
    return valid, rejected

def weighted_interval_scheduling(sessions):
    """
    Solve weighted interval scheduling with tie-breaking.
    Returns (max_value, selected_ids).
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda x: x["end"])
    n = len(sorted_sessions)

    # Precompute p(j) - last non-overlapping session index
    p = [-1] * n
    for i in range(n):
        for j in range(i-1, -1, -1):
            if sorted_sessions[j]["end"] <= sorted_sessions[i]["start"]:
                p[i] = j
                break

    # DP arrays: dp_value, dp_sessions (list of IDs for best solution)
    dp_value = [0] * n
    dp_sessions = [[] for _ in range(n)]

    for i in range(n):
        # Option 1: exclude session i
        if i == 0:
            exclude_val = 0
            exclude_sess = []
        else:
            exclude_val = dp_value[i-1]
            exclude_sess = dp_sessions[i-1][:]

        # Option 2: include session i
        include_val = sorted_sessions[i]["value"]
        include_sess = [sorted_sessions[i]["id"]]
        if p[i] != -1:
            include_val += dp_value[p[i]]
            include_sess = dp_sessions[p[i]][:] + include_sess

        # Choose better option with tie-breaking
        if include_val > exclude_val:
            dp_value[i] = include_val
            dp_sessions[i] = include_sess
        elif include_val < exclude_val:
            dp_value[i] = exclude_val
            dp_sessions[i] = exclude_sess
        else:
            # Tie: prefer fewer sessions, then lexicographically smaller list
            if len(include_sess) < len(exclude_sess):
                dp_value[i] = include_val
                dp_sessions[i] = include_sess
            elif len(include_sess) > len(exclude_sess):
                dp_value[i] = exclude_val
                dp_sessions[i] = exclude_sess
            else:
                # Same number of sessions: lexicographic comparison
                if include_sess < exclude_sess:
                    dp_value[i] = include_val
                    dp_sessions[i] = include_sess
                else:
                    dp_value[i] = exclude_val
                    dp_sessions[i] = exclude_sess

    return dp_value[-1], dp_sessions[-1]

def solve(input_data):
    """Main solving function."""
    sessions = input_data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)

    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    # Sort selected IDs chronologically by their start time
    id_to_session = {s["id"]: s for s in valid_sessions}
    selected_ids.sort(key=lambda x: id_to_session[x]["start"])

    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

def run_tests():
    """Run built-in tests."""
    test_cases = []

    # Test 1: Basic case
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
                {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 4}
            ]
        },
        "expected": {
            "max_value": 8,
            "selected_ids": ["a", "b"],
            "rejected": []
        }
    })

    # Test 2: Empty sessions
    test_cases.append({
        "input": {"sessions": []},
        "expected": {
            "max_value": 0,
            "selected_ids": [],
            "rejected": []
        }
    })

    # Test 3: Rejected sessions
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
                {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
                {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3}
            ]
        },
        "expected": {
            "max_value": 3,
            "selected_ids": ["z"],
            "rejected": [
                {"id": "x", "reasons": ["end not after start"]},
                {"id": "y", "reasons": ["negative value"]}
            ]
        }
    })

    # Test 4: Tie-breaking (same value, different counts)
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5}
            ]
        },
        "expected": {
            "max_value": 5,
            "selected_ids": ["a"],
            "rejected": []
        }
    })

    # Test 5: Lexicographic tie-breaking
    test_cases.append({
        "input": {
            "sessions": [
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
                {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            ]
        },
        "expected": {
            "max_value": 3,
            "selected_ids": ["a"],
            "rejected": []
        }
    })

    # Run tests
    for i, tc in enumerate(test_cases, 1):
        result = solve(tc["input"])
        # Convert datetime back for comparison (if any start/end in expected)
        # Simplify: just compare the JSON-serializable parts
        assert result["max_value"] == tc["expected"]["max_value"], f"Test {i} failed: max_value mismatch"
        assert result["selected_ids"] == tc["expected"]["selected_ids"], f"Test {i} failed: selected_ids mismatch"
        assert result["rejected"] == tc["expected"]["rejected"], f"Test {i} failed: rejected mismatch"

    print("All tests passed! (5/5)")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        input_data = json.load(sys.stdin)
        result = solve(input_data)
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError:
        print(json.dumps({"error": "Invalid JSON input"}), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```
````
