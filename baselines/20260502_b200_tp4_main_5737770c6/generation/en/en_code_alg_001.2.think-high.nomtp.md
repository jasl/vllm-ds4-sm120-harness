# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 21.754517
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 3331, "completion_tokens": 3037, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3037
- Total tokens: 3331

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

# ------------------------------------------------------------
# Core scheduling logic (weighted interval scheduling)
# ------------------------------------------------------------

def parse_iso_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(ts_str)


def validate_sessions(sessions):
    """Validate sessions and return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get("id", "unknown")
        # Check required fields
        if "start" not in sess or "end" not in sess or "value" not in sess:
            rejected.append({"id": sid, "reason": "Missing required fields (start, end, value)"})
            continue
        try:
            start = parse_iso_timestamp(sess["start"])
            end = parse_iso_timestamp(sess["end"])
        except Exception:
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue
        value = sess["value"]
        if not isinstance(value, (int, float)):
            rejected.append({"id": sid, "reason": "Value must be a number"})
            continue
        if value < 0:
            rejected.append({"id": sid, "reason": "Negative value"})
            continue
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


def weighted_interval_scheduling(sessions):
    """
    Weighted interval scheduling with tie-breaking.
    Returns (max_value, selected_ids).
    Tie-breaking: fewer sessions, then lexicographically smaller list.
    """
    if not sessions:
        return 0, []

    # Sort by end time
    sorted_sessions = sorted(sessions, key=lambda s: s["end"])
    n = len(sorted_sessions)

    # Precompute p(i): last non-overlapping session index
    end_times = [s["end"] for s in sorted_sessions]
    p = [-1] * n
    for i in range(n):
        start_i = sorted_sessions[i]["start"]
        # Binary search: find rightmost session with end <= start_i
        j = bisect_right(end_times, start_i) - 1
        p[i] = j

    # DP arrays: (value, count, list of ids) for tie-breaking
    # We store: dp[i] = (total_value, -count_sessions, ids_tuple)
    # Using -count so we maximize value, then maximize -count (minimize count),
    # then lexicographic on ids.
    dp = [(0, 0, ())] * (n + 1)  # dp[0] = before any sessions

    for i in range(1, n + 1):
        idx = i - 1
        val = sorted_sessions[idx]["value"]
        # Option 1: include session i
        if p[idx] == -1:
            include_val = val
            include_count = 1
            include_ids = (sorted_sessions[idx]["id"],)
        else:
            prev = dp[p[idx] + 1]
            include_val = prev[0] + val
            include_count = -prev[1] + 1  # prev[1] is negative count
            include_ids = prev[2] + (sorted_sessions[idx]["id"],)

        # Option 2: exclude session i
        exclude = dp[i - 1]

        # Compare: higher value first, then fewer sessions (higher -count),
        # then lexicographically smaller ids
        include_key = (include_val, -include_count, include_ids)
        exclude_key = (exclude[0], exclude[1], exclude[2])

        if include_key > exclude_key:  # tuple comparison works
            dp[i] = (include_val, -include_count, include_ids)
        else:
            dp[i] = exclude

    max_val, neg_count, ids_tuple = dp[n]
    selected_ids = list(ids_tuple)
    # Ensure chronological order (already sorted by end time, which respects start times)
    return max_val, selected_ids


# ------------------------------------------------------------
# Main processing
# ------------------------------------------------------------

def process_input(json_data):
    """Process parsed JSON data and return result dict."""
    sessions_raw = json_data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions_raw)
    max_val, selected_ids = weighted_interval_scheduling(valid_sessions)
    return {
        "max_value": max_val,
        "selected_ids": selected_ids,
        "rejected": rejected
    }


def run_tests():
    """Run built-in tests."""
    # Test 1: Simple case
    data1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 10},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 6}
        ]
    }
    result1 = process_input(data1)
    assert result1["max_value"] == 11, f"Test 1 max_value failed: {result1['max_value']}"
    assert result1["selected_ids"] == ["b"], f"Test 1 selected failed: {result1['selected_ids']}"
    assert result1["rejected"] == [], f"Test 1 rejected failed: {result1['rejected']}"

    # Test 2: Tie-breaking - same value, fewer sessions
    data2 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "y", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 10},
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T13:00:00", "value": 10}
        ]
    }
    result2 = process_input(data2)
    assert result2["max_value"] == 10, f"Test 2 max_value failed: {result2['max_value']}"
    # Both x+y=20, z=10 -> best is x+y with value 20? Wait, 10+10=20, z=10 -> optimal is 20
    # Actually tie-breaking: value 20 is unique, so selected = ["x","y"]
    assert result2["max_value"] == 20, f"Test 2 corrected max_value failed: {result2['max_value']}"
    assert result2["selected_ids"] == ["x", "y"], f"Test 2 selected failed: {result2['selected_ids']}"

    # Test 3: Tie-breaking 2 - same value and count, lexicographic
    data3 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "a", "start": "2026-05-01T11:00:00", "end": "2026-05-01T13:00:00", "value": 10},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 15}
        ]
    }
    result3 = process_input(data3)
    # Options: a alone =10, b alone=10, c alone=15, a+b=20 (overlap? a starts at 11, b ends at 11 -> no overlap)
    # a+b value 20, c value 15 -> optimal is a+b value 20. Lexicographically ["a","b"] vs ["b","a"] -> ["a","b"] is smaller
    assert result3["max_value"] == 20, f"Test 3 max_value failed: {result3['max_value']}"
    assert result3["selected_ids"] == ["a", "b"], f"Test 3 selected failed: {result3['selected_ids']}"

    # Test 4: Rejection cases
    data4 = {
        "sessions": [
            {"id": "ok", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "bad1", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},
            {"id": "bad2", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
            {"id": "bad3", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }
    result4 = process_input(data4)
    assert result4["max_value"] == 5, f"Test 4 max_value failed: {result4['max_value']}"
    assert result4["selected_ids"] == ["ok"], f"Test 4 selected failed: {result4['selected_ids']}"
    assert len(result4["rejected"]) == 3, f"Test 4 rejected count failed: {len(result4['rejected'])}"
    reasons = [r["reason"] for r in result4["rejected"]]
    assert any("End not after start" in r for r in reasons), "Test 4 missing end before start rejection"
    assert any("Negative" in r for r in reasons), "Test 4 missing negative value rejection"
    assert any("Invalid timestamp" in r for r in reasons), "Test 4 missing invalid timestamp rejection"

    # Test 5: Empty sessions
    data5 = {"sessions": []}
    result5 = process_input(data5)
    assert result5["max_value"] == 0, f"Test 5 max_value failed: {result5['max_value']}"
    assert result5["selected_ids"] == [], f"Test 5 selected failed: {result5['selected_ids']}"
    assert result5["rejected"] == [], f"Test 5 rejected failed: {result5['rejected']}"

    # Test 6: Complex tie - value 10 each, two vs two
    data6 = {
        "sessions": [
            {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    }
    # Possible: d+b=20, c=10 -> d+b wins. d+b = 20, ids ["b","d"] sorted? Actually d end=10:00, b start=10:00 non-overlap
    result6 = process_input(data6)
    assert result6["max_value"] == 20, f"Test 6 max_value failed: {result6['max_value']}"
    # d before b chronologically -> ["d","b"]? Actually sorted by end: d(10:00), b(11:00), c(11:00)
    # End sorted: d end 10:00, b end 11:00, c end 11:00. p for b: end times [10:00,11:00,11:00], start b=10:00 -> p=0
    # dp: include b gives 10+10=20 ids (d,b); exclude gives b alone 10. So d+b chosen.
    assert result6["selected_ids"] == ["d", "b"], f"Test 6 selected failed: {result6['selected_ids']}"

    print("All tests passed!")


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        raw = sys.stdin.read()
        json_data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}))
        sys.exit(1)

    result = process_input(json_data)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```
````
