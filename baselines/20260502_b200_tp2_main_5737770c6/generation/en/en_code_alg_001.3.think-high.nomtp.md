# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 30.704312
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 4033, "completion_tokens": 3739, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 3739
- Total tokens: 4033

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
from typing import List, Dict, Optional, Tuple

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"

class Session:
    __slots__ = ('id', 'start', 'end', 'value')

    def __init__(self, sid: str, start: datetime, end: datetime, value: int):
        self.id = sid
        self.start = start
        self.end = end
        self.value = value

def parse_iso_timestamp(ts: str) -> Optional[datetime]:
    """Parse ISO timestamp without timezone info. Return None if invalid."""
    if 'T' not in ts:
        return None
    try:
        return datetime.strptime(ts, ISO_FORMAT)
    except ValueError:
        return None

def validate_sessions(raw_data: Dict) -> Tuple[List[Session], List[Dict]]:
    """Validate and parse sessions. Return (valid_sessions, rejected_entries)."""
    sessions_raw = raw_data.get("sessions", [])
    valid_sessions: List[Session] = []
    rejected: List[Dict] = []

    for idx, entry in enumerate(sessions_raw):
        sid = entry.get("id")
        start_str = entry.get("start")
        end_str = entry.get("end")
        value = entry.get("value")
        errors = []

        # Check id exists
        if not sid or not isinstance(sid, str):
            errors.append("missing or invalid id")
        else:
            sid = str(sid)

        # Parse start
        start = None
        if not start_str or not isinstance(start_str, str):
            errors.append("missing or invalid start")
        else:
            start = parse_iso_timestamp(start_str)
            if start is None:
                errors.append("invalid start format")

        # Parse end
        end = None
        if not end_str or not isinstance(end_str, str):
            errors.append("missing or invalid end")
        else:
            end = parse_iso_timestamp(end_str)
            if end is None:
                errors.append("invalid end format")

        # Validate value
        if value is None or not isinstance(value, (int, float)):
            errors.append("missing or invalid value")
        else:
            value = int(value)
            if value < 0:
                errors.append("negative value")

        # Check end > start if both are valid
        if start and end and end <= start:
            errors.append("end not after start")

        if errors:
            rejected.append({"id": sid, "reason": "; ".join(errors)})
        else:
            valid_sessions.append(Session(sid, start, end, value))

    return valid_sessions, rejected

def find_predecessors(sessions: List[Session]) -> List[int]:
    """For each session, find the last session that ends before it starts (O(n log n))."""
    end_times = [(s.end, i) for i, s in enumerate(sessions)]
    end_times.sort(key=lambda x: x[0])
    ends_sorted = [et[0] for et in end_times]
    indices_map = [et[1] for et in end_times]

    pred = [-1] * len(sessions)
    for i, s in enumerate(sessions):
        # Binary search on sorted end times for start time
        lo, hi = 0, len(ends_sorted)
        while lo < hi:
            mid = (lo + hi) // 2
            if ends_sorted[mid] <= s.start:
                lo = mid + 1
            else:
                hi = mid
        # lo is first index with end > start -> predecessor index is lo-1
        if lo > 0:
            # Find original index of that latest ending session
            pred[i] = indices_map[lo - 1]
    return pred

def weighted_interval_scheduling(sessions: List[Session]) -> Tuple[int, List[str]]:
    """DP solution for weighted interval scheduling. Returns (max_value, optimal_ids)."""
    if not sessions:
        return 0, []

    # Sort sessions by end time
    indexed_sessions = list(enumerate(sessions))
    indexed_sessions.sort(key=lambda x: x[1].end)
    sorted_indices = [idx for idx, _ in indexed_sessions]
    sorted_sessions = [s for _, s in indexed_sessions]

    # Create mapping from sorted order back to original for ID retrieval
    orig_to_sorted = {orig: sorted_idx for sorted_idx, orig in enumerate(sorted_indices)}

    # Find predecessors in sorted order
    pred_sorted = [-1] * len(sorted_sessions)
    # We'll work with sorted sessions directly
    # Re-index predecessors to sorted indices
    pred_original = find_predecessors(sorted_sessions)
    for i, p in enumerate(pred_original):
        if p != -1:
            pred_sorted[i] = orig_to_sorted[p]

    # DP arrays: (value, session_count, next_chosen, lex_key)
    # Lex key is a tuple of session IDs in reverse order for tie-breaking
    dp_val = [0] * (len(sorted_sessions) + 1)
    dp_count = [0] * (len(sorted_sessions) + 1)
    dp_choice = [None] * (len(sorted_sessions) + 1)  # list of IDs for the optimal solution from i onward

    # We'll compute dp from end to start (reverse order)
    # dp_val[i] = max value from sessions i..n-1
    # We'll use 1-indexed for simplicity: dp_val[i] for i in [0..n]
    # dp_val[n] = 0

    n = len(sorted_sessions)
    dp_val[n] = 0
    dp_count[n] = 0
    dp_choice[n] = []

    # We'll store for each state the full list of IDs for tie-breaking
    # This is O(n^2) in worst case but n is moderate; we can optimize with linked lists
    # but for clarity we use lists.

    # To keep O(n log n) overall, we store decisions and reconstruct after
    decision = [None] * n  # True if pick session i, False if skip

    for i in range(n - 1, -1, -1):
        # Option 1: skip session i
        skip_val = dp_val[i + 1]
        skip_cnt = dp_count[i + 1]
        skip_ids = dp_choice[i + 1]

        # Option 2: take session i
        pred = pred_sorted[i]
        take_idx = pred + 1 if pred != -1 else i + 1  # adjust for empty predecessor
        # Actually: if pred == -1, then we can take this session and then consider dp_val[0]? No.
        # Alternative: we define dp_val[i] for suffix starting at i.
        # If we take session i, next available is (pred + 1) in sorted order
        next_idx = pred + 1 if pred != -1 else 0
        # But we need to ensure we don't double count: dp_val for suffix starting at i considers i..n-1.
        # The next available after taking i is the first session after pred.
        # Since dp_val is for suffix, we need dp_val for suffix starting at next_idx.
        # However dp_val[j] is defined as max from j..n-1. So next_idx must be > i?
        # No, pred could be before i, next_idx <= i. We need dp_val for a NEW suffix.
        # This standard approach works if we sort by end time and compute forward.
        # Let's switch to forward DP: dp[i] = max value considering first i sessions (sorted).

    # Reset: use forward DP (standard weighted interval scheduling)
    # dp[i] = max value using sessions 0..i (sorted by end)
    dp = [0] * (n + 1)  # dp[0] = 0 (no sessions)
    chosen = [[] for _ in range(n + 1)]  # list of IDs for dp[i]
    count = [0] * (n + 1)

    for i in range(1, n + 1):
        session = sorted_sessions[i - 1]
        # Option skip
        skip_val = dp[i - 1]
        skip_ids = chosen[i - 1]
        skip_cnt = count[i - 1]

        # Option take
        pred = pred_sorted[i - 1]
        take_val = session.value + (dp[pred + 1] if pred != -1 else 0)
        take_ids = (chosen[pred + 1] if pred != -1 else []) + [session.id]
        take_cnt = count[pred + 1] if pred != -1 else 0
        take_cnt += 1

        # Compare: higher value wins; tie -> fewer sessions; tie -> lexicographically smaller list
        if take_val > skip_val:
            dp[i] = take_val
            chosen[i] = take_ids
            count[i] = take_cnt
        elif take_val < skip_val:
            dp[i] = skip_val
            chosen[i] = skip_ids
            count[i] = skip_cnt
        else:  # equal value
            if take_cnt < skip_cnt:
                dp[i] = take_val
                chosen[i] = take_ids
                count[i] = take_cnt
            elif take_cnt > skip_cnt:
                dp[i] = skip_val
                chosen[i] = skip_ids
                count[i] = skip_cnt
            else:  # equal count
                # Lexicographically smaller list of IDs
                take_sorted = sorted(take_ids)
                skip_sorted = sorted(skip_ids)
                if take_sorted < skip_sorted:
                    dp[i] = take_val
                    chosen[i] = take_ids
                    count[i] = take_cnt
                else:
                    dp[i] = skip_val
                    chosen[i] = skip_ids
                    count[i] = skip_cnt

    max_val = dp[n]
    optimal_ids = chosen[n]
    # The IDs are in reverse order of processing; need chronological order by start time
    # Get original sessions for these IDs
    id_to_session = {s.id: s for s in sessions}
    ordered_sessions = [id_to_session[sid] for sid in optimal_ids]
    ordered_sessions.sort(key=lambda s: s.start)
    ordered_ids = [s.id for s in ordered_sessions]

    return max_val, ordered_ids

def run_tests() -> None:
    """Run built-in tests."""
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic case
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 4}
        ]
    }
    valid, rejected = validate_sessions(data)
    total_tests += 1
    assert len(valid) == 3 and len(rejected) == 0, "Test 1 failed"
    max_val, ids = weighted_interval_scheduling(valid)
    total_tests += 1
    assert max_val == 8, f"Test 1 value: expected 8 got {max_val}"
    total_tests += 1
    assert ids == ['a', 'b'], f"Test 1 ids: expected ['a','b'] got {ids}"
    tests_passed += 3

    # Test 2: Reject invalid
    data2 = {
        "sessions": [
            {"id": "x", "start": "invalid", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 3},
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]
    }
    valid2, rejected2 = validate_sessions(data2)
    total_tests += 1
    assert len(valid2) == 0, "Test 2: no valid sessions"
    total_tests += 1
    assert len(rejected2) == 3, f"Test 2: expected 3 rejected, got {len(rejected2)}"
    tests_passed += 2

    # Test 3: Tie-breaking - same value, fewer sessions wins
    data3 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    valid3, _ = validate_sessions(data3)
    max_val3, ids3 = weighted_interval_scheduling(valid3)
    total_tests += 1
    assert max_val3 == 5, f"Test 3 value: expected 5 got {max_val3}"
    total_tests += 1
    # Should pick single session (c) not two sessions
    assert len(ids3) == 1, f"Test 3: expected 1 session, got {ids3}"
    tests_passed += 2

    # Test 4: Lexicographic tie-breaking
    data4 = {
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 2}
        ]
    }
    valid4, _ = validate_sessions(data4)
    max_val4, ids4 = weighted_interval_scheduling(valid4)
    total_tests += 1
    # Both 'a' and 'b' give value 3 (lexicographically 'a' wins) or 'a'+'c' gives 5
    expected_ids = ['a', 'c']
    assert ids4 == expected_ids, f"Test 4: expected {expected_ids} got {ids4}"
    tests_passed += 1

    # Test 5: Empty input
    data5 = {"sessions": []}
    valid5, rejected5 = validate_sessions(data5)
    max_val5, ids5 = weighted_interval_scheduling(valid5)
    total_tests += 1
    assert max_val5 == 0 and ids5 == [], f"Test 5 failed"
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed.")

def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    try:
        raw_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        sys.exit(1)

    valid_sessions, rejected = validate_sessions(raw_data)
    max_value, selected_ids = weighted_interval_scheduling(valid_sessions)

    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
```
````
