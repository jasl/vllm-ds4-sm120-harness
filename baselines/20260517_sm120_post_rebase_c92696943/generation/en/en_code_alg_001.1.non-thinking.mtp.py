#!/usr/bin/env python3
import json
import sys
from datetime import datetime

def parse_timestamp(ts_str):
    """Parse ISO-like timestamp without timezone info."""
    return datetime.fromisoformat(ts_str)

def validate_sessions(sessions):
    """Validate sessions and separate valid from rejected."""
    valid_sessions = []
    rejected = []

    for session in sessions:
        sid = session.get("id", "unknown")
        reasons = []

        # Check required fields
        if "id" not in session or "start" not in session or "end" not in session or "value" not in session:
            reasons.append("missing required fields")
        else:
            # Parse timestamps
            try:
                start = parse_timestamp(session["start"])
                end = parse_timestamp(session["end"])

                # Check end after start
                if end <= start:
                    reasons.append("end not after start")

                # Check non-negative value
                if session["value"] < 0:
                    reasons.append("negative value")

                if not reasons:
                    valid_sessions.append({
                        "id": sid,
                        "start": start,
                        "end": end,
                        "value": session["value"]
                    })

            except (ValueError, TypeError):
                reasons.append("invalid timestamp format")

        if reasons:
            rejected.append({
                "id": sid,
                "reason": "; ".join(reasons)
            })

    return valid_sessions, rejected

def optimize_sessions(valid_sessions):
    """Weighted interval scheduling with O(n log n) complexity."""
    if not valid_sessions:
        return 0, [], []

    # Sort by end time
    sorted_sessions = sorted(valid_sessions, key=lambda s: s["end"])

    # Store original indices for reconstruction
    n = len(sorted_sessions)
    indices = list(range(n))

    # Precompute p(j): largest index i < j with end_i <= start_j
    start_times = [s["start"] for s in sorted_sessions]
    end_times = [s["end"] for s in sorted_sessions]

    p = [-1] * n
    for j in range(n):
        # Binary search for rightmost session ending <= start of j
        lo, hi = 0, j - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if end_times[mid] <= start_times[j]:
                lo = mid + 1
            else:
                hi = mid - 1
        p[j] = hi

    # DP arrays
    dp = [0] * (n + 1)  # dp[i] = max value using first i sessions (1-indexed)
    choice = [0] * (n + 1)  # 1 if session i-1 is selected, 0 otherwise

    for i in range(1, n + 1):
        j = i - 1  # 0-indexed session
        # Option 1: don't include session j
        not_take = dp[i - 1]
        # Option 2: include session j
        take_val = sorted_sessions[j]["value"] + dp[p[j] + 1]

        if take_val > not_take:
            dp[i] = take_val
            choice[i] = 1
        elif take_val < not_take:
            dp[i] = not_take
            choice[i] = 0
        else:
            # Equal value: choose fewer sessions
            # Count sessions in each option
            count_take = 1
            # Count sessions in take option
            k = p[j] + 1
            while k > 0:
                if choice[k] == 1:
                    count_take += 1
                    k = p[k - 1] + 1
                else:
                    k -= 1

            count_not_take = 0
            k = i - 1
            while k > 0:
                if choice[k] == 1:
                    count_not_take += 1
                    k = p[k - 1] + 1
                else:
                    k -= 1

            if count_take < count_not_take:
                dp[i] = take_val
                choice[i] = 1
            elif count_take > count_not_take:
                dp[i] = not_take
                choice[i] = 0
            else:
                # Same count: choose lexicographically smaller IDs
                # Reconstruct both sequences
                seq_take = []
                k = p[j] + 1
                while k > 0:
                    if choice[k] == 1:
                        seq_take.append(sorted_sessions[k - 1]["id"])
                        k = p[k - 1] + 1
                    else:
                        k -= 1
                seq_take.append(sorted_sessions[j]["id"])
                seq_take.sort()

                seq_not_take = []
                k = i - 1
                while k > 0:
                    if choice[k] == 1:
                        seq_not_take.append(sorted_sessions[k - 1]["id"])
                        k = p[k - 1] + 1
                    else:
                        k -= 1
                seq_not_take.sort()

                if seq_take < seq_not_take:
                    dp[i] = take_val
                    choice[i] = 1
                else:
                    dp[i] = not_take
                    choice[i] = 0

    # Reconstruct solution
    selected = []
    i = n
    while i > 0:
        if choice[i] == 1:
            selected.append(sorted_sessions[i - 1])
            i = p[i - 1] + 1
        else:
            i -= 1

    selected.reverse()  # Chronological order (already sorted by end time, but reverse reconstruction)
    # Actually they are in reverse order of end times, so reverse again for chronological
    selected.sort(key=lambda s: s["start"])

    max_value = dp[n]
    selected_ids = [s["id"] for s in selected]

    return max_value, selected_ids, selected

def run_tests():
    """Built-in tests."""
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
    max_val, ids, _ = optimize_sessions(valid)
    assert max_val == 8, f"Test 1 failed: expected 8, got {max_val}"
    assert set(ids) == {"a", "b"}, f"Test 1 failed: ids mismatch {ids}"
    tests_passed += 1

    # Test 2: Negative value rejection
    total_tests += 1
    data = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert len(rejected) == 1 and "negative" in rejected[0]["reason"]
    tests_passed += 1

    # Test 3: End not after start
    total_tests += 1
    data = {
        "sessions": [
            {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert len(rejected) == 1 and "end not after start" in rejected[0]["reason"]
    tests_passed += 1

    # Test 4: Empty input
    total_tests += 1
    data = {"sessions": []}
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids, _ = optimize_sessions(valid)
    assert max_val == 0 and ids == []
    tests_passed += 1

    # Test 5: Tie-breaking with fewer sessions
    total_tests += 1
    data = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    max_val, ids, _ = optimize_sessions(valid)
    assert max_val == 5, f"Test 5 failed: expected 5, got {max_val}"
    assert len(ids) == 1, f"Test 5 failed: expected 1 session, got {len(ids)}"
    tests_passed += 1

    # Test 6: Invalid timestamp
    total_tests += 1
    data = {
        "sessions": [
            {"id": "z", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert len(rejected) == 1 and "invalid timestamp" in rejected[0]["reason"]
    tests_passed += 1

    # Test 7: Missing fields
    total_tests += 1
    data = {
        "sessions": [
            {"id": "w", "start": "2026-05-01T09:00:00", "value": 5}
        ]
    }
    valid, rejected = validate_sessions(data["sessions"])
    assert len(rejected) == 1 and "missing required fields" in rejected[0]["reason"]
    tests_passed += 1

    print(f"All {tests_passed}/{total_tests} tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    # Read JSON from stdin
    try:
        raw_data = sys.stdin.read()
        data = json.loads(raw_data)
    except (json.JSONDecodeError, KeyboardInterrupt):
        print(json.dumps({"error": "Invalid JSON input"}))
        sys.exit(1)

    if "sessions" not in data:
        print(json.dumps({"error": "Missing 'sessions' key"}))
        sys.exit(1)

    # Validate sessions
    valid_sessions, rejected = validate_sessions(data["sessions"])

    # Run optimization
    max_value, selected_ids, _ = optimize_sessions(valid_sessions)

    # Build output
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
