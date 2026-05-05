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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 19.229422
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 4593, "completion_tokens": 4299, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 4299
- Total tokens: 4593

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

def parse_timestamp(ts):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(ts)

def load_input(data):
    """Validate and parse input JSON."""
    if "sessions" not in data:
        raise ValueError("Input must contain 'sessions' key")
    return data["sessions"]

def validate_session(session):
    """Validate a single session and return list of errors."""
    errors = []
    if "id" not in session or not isinstance(session["id"], str):
        errors.append("missing or invalid id")
        return errors
    if "start" not in session:
        errors.append("missing start")
    if "end" not in session:
        errors.append("missing end")
    if "value" not in session:
        errors.append("missing value")
    if errors:
        return errors

    try:
        start = parse_timestamp(session["start"])
        end = parse_timestamp(session["end"])
        if end <= start:
            errors.append("end must be after start")
    except (ValueError, TypeError):
        errors.append("invalid datetime format")

    if not isinstance(session["value"], (int, float)) or session["value"] < 0:
        errors.append("value must be non-negative")
    elif isinstance(session["value"], float) and not session["value"].is_integer():
        pass  # allow integer values as float

    return errors

def solve_weighted_interval_scheduling(sessions):
    """
    Weighted interval scheduling with O(n log n) DP.
    Returns (max_value, selected_ids).
    In case of ties: fewer sessions, then lexicographically smaller IDs.
    """
    n = len(sessions)
    if n == 0:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["parsed_end"])
    ids_sorted = [s["id"] for s in sorted_sessions]

    # Precompute p(i): last non-overlapping job index
    p = [-1] * n
    for i in range(n):
        s_time = sorted_sessions[i]["parsed_start"]
        # Binary search for last job with end <= start
        lo, hi = 0, i - 1
        best = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if sorted_sessions[mid]["parsed_end"] <= s_time:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        p[i] = best

    # DP arrays
    dp = [0] * n  # max value up to i (inclusive)
    choice = [0] * n  # 1 = take job i, 0 = skip it

    for i in range(n):
        # Option 1: don't take job i
        skip_val = dp[i - 1] if i > 0 else 0

        # Option 2: take job i
        take_val = sorted_sessions[i]["value"]
        if p[i] != -1:
            take_val += dp[p[i]]

        # Compare: prefer higher value
        if take_val > skip_val:
            dp[i] = take_val
            choice[i] = 1
        elif take_val < skip_val:
            dp[i] = skip_val
            choice[i] = 0
        else:
            # Equal value: apply tie-breaking
            # Compute solutions for both options
            # We'll reconstruct both and compare after DP
            # For now, store temporarily and decide later
            # We'll do a second pass for tie-breaking
            dp[i] = take_val
            choice[i] = 1 if take_val >= skip_val else 0  # placeholder

    # Reconstruct both optimal solutions to break ties
    def reconstruct_with_choice(forced_choice_at, forced_value):
        """Reconstruct solution given a forced choice at index i."""
        selected = []
        i = n - 1
        while i >= 0:
            if i == forced_choice_at:
                take = forced_value
            else:
                # Determine best at this point
                skip_val = dp[i - 1] if i > 0 else 0
                take_val = sorted_sessions[i]["value"]
                if p[i] != -1:
                    take_val += dp[p[i]]
                take = 1 if take_val > skip_val else 0
                if take_val == skip_val:
                    # For reconstruction without forced choice, prefer skip (fewer sessions)
                    take = 0

            if take:
                selected.append(ids_sorted[i])
                i = p[i]
            else:
                i -= 1
        selected.reverse()
        return selected

    # Find where ties occurred and choose best
    best_value = dp[n - 1] if n > 0 else 0
    best_selected = None
    best_count = float('inf')
    best_lex = None

    # Reconstruct the solution(s) for optimal value
    # We'll do a systematic reconstruction that considers ties
    # Since there can be many ties, we use DP with tie-breaking embedded

    # Revised DP with tie-breaking integrated
    dp2 = [0] * n
    count2 = [0] * n  # number of sessions used
    lex2 = [None] * n  # list of IDs for tie-breaking

    for i in range(n):
        # Option skip
        skip_val = dp2[i - 1] if i > 0 else 0
        skip_count = count2[i - 1] if i > 0 else 0
        skip_lex = list(lex2[i - 1]) if i > 0 and lex2[i - 1] is not None else []

        # Option take
        take_val = sorted_sessions[i]["value"]
        take_count = 1
        if p[i] != -1:
            take_val += dp2[p[i]]
            take_count += count2[p[i]]
        take_lex = (list(lex2[p[i]]) if p[i] != -1 and lex2[p[i]] is not None else [])
        take_lex.append(ids_sorted[i])

        # Compare
        if take_val > skip_val:
            dp2[i] = take_val
            count2[i] = take_count
            lex2[i] = take_lex
        elif take_val < skip_val:
            dp2[i] = skip_val
            count2[i] = skip_count
            lex2[i] = skip_lex
        else:
            # Tie: prefer fewer sessions
            if take_count < skip_count:
                dp2[i] = take_val
                count2[i] = take_count
                lex2[i] = take_lex
            elif take_count > skip_count:
                dp2[i] = skip_val
                count2[i] = skip_count
                lex2[i] = skip_lex
            else:
                # Same count: lexicographically smaller
                if take_lex < skip_lex:
                    dp2[i] = take_val
                    count2[i] = take_count
                    lex2[i] = take_lex
                else:
                    dp2[i] = skip_val
                    count2[i] = skip_count
                    lex2[i] = skip_lex

    if n == 0:
        return 0, []
    return dp2[n - 1], lex2[n - 1] if lex2[n - 1] is not None else []

def process_input(input_data):
    """Process input data and return output dictionary."""
    try:
        sessions_raw = load_input(input_data)
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        return {"error": str(e)}

    valid_sessions = []
    rejected = []

    for session in sessions_raw:
        errors = validate_session(session)
        if errors:
            rejected.append({
                "id": session.get("id", "unknown"),
                "reason": "; ".join(errors)
            })
        else:
            parsed_start = parse_timestamp(session["start"])
            parsed_end = parse_timestamp(session["end"])
            valid_sessions.append({
                "id": session["id"],
                "start": session["start"],
                "end": session["end"],
                "value": session["value"],
                "parsed_start": parsed_start,
                "parsed_end": parsed_end
            })

    # Solve
    max_value, selected_ids = solve_weighted_interval_scheduling(valid_sessions)

    # Build output
    result = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    return result

def run_tests():
    """Built-in tests."""
    test_cases = []

    # Test 1: Empty
    test_cases.append((
        {"sessions": []},
        {"max_value": 0, "selected_ids": [], "rejected": []}
    ))

    # Test 2: Single valid
    test_cases.append((
        {"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5}]},
        {"max_value": 5, "selected_ids": ["a"], "rejected": []}
    ))

    # Test 3: Two overlapping, choose higher value
    test_cases.append((
        {"sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 8}
        ]},
        {"max_value": 8, "selected_ids": ["b"], "rejected": []}
    ))

    # Test 4: Two non-overlapping
    test_cases.append((
        {"sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3}
        ]},
        {"max_value": 8, "selected_ids": ["a", "b"], "rejected": []}
    ))

    # Test 5: Reject invalid
    test_cases.append((
        {"sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5}
        ]},
        {"max_value": 0, "selected_ids": [], "rejected": [{"id": "x", "reason": "end must be after start"}]}
    ))

    # Test 6: Tie-breaking: same value, fewer sessions
    test_cases.append((
        {"sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]},
        # a+b = 10 with 2 sessions vs c=10 with 1 session -> choose c
        {"max_value": 10, "selected_ids": ["c"], "rejected": []}
    ))

    # Test 7: Tie-breaking: same value, same count, lexicographic
    test_cases.append((
        {"sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]},
        # a+b = 10 vs c=10, both 1 session? No: a+b is 2 sessions, c is 1 -> c wins
        {"max_value": 10, "selected_ids": ["c"], "rejected": []}
    ))

    # Test 8: Complex tie: same value same count
    test_cases.append((
        {"sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 2},
            {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10}
        ]},
        # a+b+c = 10 with 3 sessions vs d=10 with 1 -> d wins
        {"max_value": 10, "selected_ids": ["d"], "rejected": []}
    ))

    # Test 9: Lexicographic tie-break
    test_cases.append((
        {"sessions": [
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "m", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 20}
        ]},
        # z+a = 20 with 2 sessions vs m=20 with 1 -> m wins
        {"max_value": 20, "selected_ids": ["m"], "rejected": []}
    ))

    # Test 10: Negative value rejection
    test_cases.append((
        {"sessions": [
            {"id": "n", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]},
        {"max_value": 0, "selected_ids": [], "rejected": [{"id": "n", "reason": "value must be non-negative"}]}
    ))

    # Test 11: Multiple valid, some rejected
    test_cases.append((
        {"sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]},
        {"max_value": 10, "selected_ids": ["a", "b"],
         "rejected": [{"id": "bad", "reason": "end must be after start"}]}
    ))

    # Test 12: All rejected
    test_cases.append((
        {"sessions": [
            {"id": "x", "start": "invalid", "end": "2026-05-01T10:00:00", "value": 5}
        ]},
        {"max_value": 0, "selected_ids": [],
         "rejected": [{"id": "x", "reason": "invalid datetime format; value must be non-negative"}]}
    ))

    all_passed = True
    for idx, (input_data, expected) in enumerate(test_cases):
        try:
            result = process_input(input_data)
            # Sort rejected by id for comparison
            result["rejected"].sort(key=lambda x: x["id"])
            expected_rejected = sorted(expected.get("rejected", []), key=lambda x: x["id"])
            if result["max_value"] != expected["max_value"]:
                print(f"Test {idx+1} FAIL: max_value {result['max_value']} != {expected['max_value']}")
                all_passed = False
            elif result["selected_ids"] != expected["selected_ids"]:
                print(f"Test {idx+1} FAIL: selected_ids {result['selected_ids']} != {expected['selected_ids']}")
                all_passed = False
            elif result["rejected"] != expected_rejected:
                print(f"Test {idx+1} FAIL: rejected {result['rejected']} != {expected_rejected}")
                all_passed = False
        except Exception as e:
            print(f"Test {idx+1} ERROR: {e}")
            all_passed = False

    if all_passed:
        print("All tests passed!")
        return True
    else:
        print("Some tests failed!")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = run_tests()
        sys.exit(0 if success else 1)
    else:
        try:
            input_data = json.load(sys.stdin)
            result = process_input(input_data)
            # For invalid input structure, return error
            if "error" in result:
                print(json.dumps(result))
            else:
                print(json.dumps(result, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}))
        except Exception as e:
            print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
```
````
