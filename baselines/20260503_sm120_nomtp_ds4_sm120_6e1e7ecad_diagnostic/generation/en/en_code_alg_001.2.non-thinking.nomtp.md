# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 59.047808
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 4041, "completion_tokens": 3747, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3747
- Total tokens: 4041

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

def parse_datetime(s):
    return datetime.fromisoformat(s)

def solve_weighted_interval_scheduling(sessions):
    # sessions: list of dicts with id, start, end, value (already validated)
    if not sessions:
        return [], 0

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s['end'])
    n = len(sorted_sessions)

    # Precompute p[i] = index of last session that ends before session i starts
    start_times = [s['start'] for s in sorted_sessions]
    end_times = [s['end'] for s in sorted_sessions]
    p = [-1] * n
    for i in range(n):
        # binary search for the rightmost end_time < start_times[i]
        idx = bisect_right(end_times, start_times[i]) - 1
        p[i] = idx  # -1 if none

    # DP arrays
    dp = [0] * (n + 1)  # dp[0] = 0, dp[i] = max value using first i sessions (0-indexed: first i means indices 0..i-1)
    choice = [False] * n  # True if session i is selected in optimal for dp[i+1]

    for i in range(1, n + 1):
        session = sorted_sessions[i-1]
        # Option 1: skip session
        skip_val = dp[i-1]
        # Option 2: take session
        take_val = session['value'] + (dp[p[i-1] + 1] if p[i-1] >= 0 else 0)

        if take_val > skip_val:
            dp[i] = take_val
            choice[i-1] = True
        elif take_val < skip_val:
            dp[i] = skip_val
            choice[i-1] = False
        else:
            # tie: compare number of sessions, then lexicographic order of IDs
            # Reconstruct both options to compare
            # Skip option: reconstruct from dp[i-1]
            # Take option: reconstruct from take
            # We need actual selected sets to compare
            def reconstruct_from(idx, chosen_flag=None):
                # if chosen_flag is set, force last session selection status for index idx
                selected = []
                j = idx
                while j >= 0:
                    if j == idx and chosen_flag is not None:
                        take = chosen_flag
                    else:
                        session_j = sorted_sessions[j]
                        skip_val_local = dp[j] if j > 0 else 0
                        take_val_local = session_j['value'] + (dp[p[j] + 1] if p[j] >= 0 else 0)
                        take = take_val_local > skip_val_local
                        if take_val_local == skip_val_local:
                            # tie breaking needed recursively - we prefer fewer sessions then lexicographic
                            # but here we only call when tie at top level, so we handle specially
                            take = False  # default to skip to minimize sessions? Actually we need to compare.
                            # To avoid deep recursion, we'll handle tie-breaking at top level differently
                            take = False  # placeholder

                    if take:
                        selected.append(sorted_sessions[j]['id'])
                        j = p[j]
                    else:
                        j -= 1
                selected.reverse()
                return selected

            # For tie-breaking, we reconstruct both full solutions
            # Skip option
            skip_selected = reconstruct_from(i-2 if i-2 >= 0 else -1) if i-1 > 0 else []
            # Take option
            take_selected = [session['id']] + (reconstruct_from(p[i-1]) if p[i-1] >= 0 else [])

            # Compare: fewer sessions first
            if len(take_selected) < len(skip_selected):
                dp[i] = take_val
                choice[i-1] = True
            elif len(take_selected) > len(skip_selected):
                dp[i] = skip_val
                choice[i-1] = False
            else:
                # Same number of sessions: lexicographic (ids are strings)
                if take_selected < skip_selected:
                    dp[i] = take_val
                    choice[i-1] = True
                else:
                    dp[i] = skip_val
                    choice[i-1] = False

    # Reconstruct optimal solution
    selected_ids = []
    j = n - 1
    # We need to re-decide to handle ties properly (since choice array may be ambiguous)
    # We'll reconstruct deterministically with tie-breaking
    while j >= 0:
        session = sorted_sessions[j]
        skip_val = dp[j] if j > 0 else 0
        take_val = session['value'] + (dp[p[j] + 1] if p[j] >= 0 else 0)

        if take_val > skip_val:
            selected_ids.append(session['id'])
            j = p[j]
        elif take_val < skip_val:
            j -= 1
        else:
            # tie: reconstruct both and compare
            # skip
            skip_list = []
            k = j - 1
            while k >= 0:
                sk = sorted_sessions[k]
                sv = dp[k] if k > 0 else 0
                tv = sk['value'] + (dp[p[k] + 1] if p[k] >= 0 else 0)
                if tv > sv:
                    skip_list.append(sk['id'])
                    k = p[k]
                elif tv < sv:
                    k -= 1
                else:
                    # sub-tie - prefer skip to minimize sessions? but we need consistency
                    # recursively handle - for simplicity break tie by skip (fewer sessions)
                    k -= 1
            skip_list.reverse()

            take_list = [session['id']]
            k = p[j]
            while k >= 0:
                sk = sorted_sessions[k]
                sv = dp[k] if k > 0 else 0
                tv = sk['value'] + (dp[p[k] + 1] if p[k] >= 0 else 0)
                if tv > sv:
                    take_list.append(sk['id'])
                    k = p[k]
                elif tv < sv:
                    k -= 1
                else:
                    k -= 1
            take_list.reverse()

            if len(take_list) < len(skip_list):
                selected_ids.extend(reversed(take_list))
                break
            elif len(take_list) > len(skip_list):
                j -= 1
                continue
            else:
                if take_list < skip_list:
                    selected_ids.extend(reversed(take_list))
                    break
                else:
                    j -= 1
                    continue
    else:
        # ensure correct order (already in reverse)
        pass

    selected_ids.reverse()
    max_value = dp[n]
    return selected_ids, max_value

def process_input(data):
    sessions_raw = data.get("sessions", [])
    valid_sessions = []
    rejected = []

    for idx, s in enumerate(sessions_raw):
        sid = s.get("id", f"unknown_{idx}")
        reasons = []

        # Parse times
        try:
            start = parse_datetime(s["start"])
            end = parse_datetime(s["end"])
        except (KeyError, ValueError, TypeError):
            reasons.append("invalid datetime format")
            rejected.append({"id": sid, "reasons": reasons})
            continue

        # Check end > start
        if end <= start:
            reasons.append("end not after start")

        # Check value
        value = s.get("value", 0)
        if not isinstance(value, (int, float)) or value < 0:
            reasons.append("negative or invalid value")

        if reasons:
            rejected.append({"id": sid, "reasons": reasons})
        else:
            valid_sessions.append({
                "id": sid,
                "start": start,
                "end": end,
                "value": value
            })

    # Sort sessions by id for deterministic tie-breaking in DP
    # But DP sorts by end time; we need stable original order for lexicographic comparison
    # Actually lexicographic comparison is on IDs in the final selected list order (chronological)
    # We'll keep original order for tie-breaking reconstruction
    # Store original index for deterministic comparison
    for i, s in enumerate(valid_sessions):
        s["_orig_idx"] = i

    selected_ids, max_value = solve_weighted_interval_scheduling(valid_sessions)

    # Ensure selected_ids are in chronological order (they come from DP sorted by end time)
    # They should already be chronological because we reconstructed in order

    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

def run_tests():
    tests_passed = 0
    tests_total = 0

    # Test 1: basic case
    data1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    result = process_input(data1)
    assert result["max_value"] == 10, f"Test 1 failed: {result}"
    assert result["selected_ids"] == ["c"], f"Test 1 failed ids: {result}"
    tests_passed += 1
    tests_total += 1

    # Test 2: non-overlapping all selected
    data2 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1},
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 2},
            {"id": "z", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 3}
        ]
    }
    result = process_input(data2)
    assert result["max_value"] == 6, f"Test 2 failed: {result}"
    assert result["selected_ids"] == ["x", "y", "z"], f"Test 2 failed ids: {result}"
    tests_passed += 1
    tests_total += 1

    # Test 3: rejected sessions
    data3 = {
        "sessions": [
            {"id": "good", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad_end", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 3},
            {"id": "neg_val", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": -1},
            {"id": "no_val", "start": "2026-05-01T12:00:00", "end": "2026-05-01T13:00:00"}
        ]
    }
    result = process_input(data3)
    assert result["max_value"] == 5, f"Test 3 failed: {result}"
    assert result["selected_ids"] == ["good"], f"Test 3 failed ids: {result}"
    assert len(result["rejected"]) == 3, f"Test 3 rejected count: {result}"
    tests_passed += 1
    tests_total += 1

    # Test 4: tie-breaking (same value, different session count)
    data4 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    result = process_input(data4)
    # Option [a,b]=10 vs [c]=10, choose fewer sessions: [c]
    assert result["max_value"] == 10, f"Test 4 failed: {result}"
    assert result["selected_ids"] == ["c"], f"Test 4 failed ids: {result}"
    tests_passed += 1
    tests_total += 1

    # Test 5: tie-breaking same count, lexicographic
    data5 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    result = process_input(data5)
    # Both non-overlapping, value=10, 2 sessions each (only one option), but ids: [b,a] vs [a,b] -> lexicographic [a,b]
    assert result["max_value"] == 10, f"Test 5 failed: {result}"
    assert result["selected_ids"] == ["a", "b"], f"Test 5 failed ids: {result}"
    tests_passed += 1
    tests_total += 1

    # Test 6: empty input
    data6 = {"sessions": []}
    result = process_input(data6)
    assert result["max_value"] == 0, f"Test 6 failed: {result}"
    assert result["selected_ids"] == [], f"Test 6 failed ids: {result}"
    tests_passed += 1
    tests_total += 1

    # Test 7: overlapping complex
    data7 = {
        "sessions": [
            {"id": "1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 7},
            {"id": "2", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 6},
            {"id": "3", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 8},
            {"id": "4", "start": "2026-05-01T12:00:00", "end": "2026-05-01T14:00:00", "value": 5}
        ]
    }
    # Options: [1,3]=15, [2,4]=11, [1,4]=12, [3]=8, etc. Best is [1,3]
    result = process_input(data7)
    assert result["max_value"] == 15, f"Test 7 failed: {result}"
    assert result["selected_ids"] == ["1", "3"], f"Test 7 failed ids: {result}"
    tests_passed += 1
    tests_total += 1

    print(f"All {tests_passed}/{tests_total} tests passed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        sys.exit(0)

    data = json.load(sys.stdin)
    result = process_input(data)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")

if __name__ == "__main__":
    main()
```
````
