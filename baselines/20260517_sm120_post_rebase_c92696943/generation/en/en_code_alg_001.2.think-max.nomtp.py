#!/usr/bin/env python3

import sys
import json
from datetime import datetime
from bisect import bisect_right

def parse_timestamp(s):
    """Parse ISO 8601 timestamp string, handling optional 'Z' suffix."""
    if not isinstance(s, str):
        raise ValueError("Timestamp must be a string")
    if s.endswith('Z') or s.endswith('z'):
        s = s[:-1] + '+00:00'
    return datetime.fromisoformat(s)


def process(input_str):
    data = json.loads(input_str)
    raw_sessions = data.get('sessions', [])

    valid_sessions = []
    rejected = []

    for sess in raw_sessions:
        sid = sess.get('id')
        start_str = sess.get('start')
        end_str = sess.get('end')
        value = sess.get('value', 0)

        reasons = []

        # Try to parse timestamps
        start_dt = end_dt = None
        try:
            start_dt = parse_timestamp(start_str)
        except (ValueError, TypeError):
            reasons.append("Invalid start timestamp")
        try:
            end_dt = parse_timestamp(end_str)
        except (ValueError, TypeError):
            reasons.append("Invalid end timestamp")

        if reasons:
            rejected.append({"id": sid, "reason": "; ".join(reasons)})
            continue

        # Validate business rules
        if end_dt <= start_dt:
            reasons.append("End must be after start")
        if value < 0:
            reasons.append("Value cannot be negative")

        if reasons:
            rejected.append({"id": sid, "reason": "; ".join(reasons)})
        else:
            valid_sessions.append({
                "id": sid,
                "start": start_dt,
                "end": end_dt,
                "value": value
            })

    # Sort valid sessions by end time, then start time, then ID (for determinism)
    valid_sessions.sort(key=lambda s: (s["end"], s["start"], s["id"]))

    n = len(valid_sessions)

    # Pre‑extract fields for speed
    end_times = [s["end"] for s in valid_sessions]
    start_times = [s["start"] for s in valid_sessions]
    values = [s["value"] for s in valid_sessions]
    ids = [s["id"] for s in valid_sessions]

    # Compute prev[i] : last job index (0‑based) that ends <= start of job i
    prev = []
    for i in range(n):
        # number of jobs with end <= start_i
        idx = bisect_right(end_times, start_times[i]) - 1
        prev.append(idx)   # -1 means none

    # dp[i] = (value, count, ids_tuple) for the best solution using first i jobs
    # dp[0] = empty set
    dp = [(0, 0, ())]

    for i in range(1, n + 1):
        job_idx = i - 1

        # Option: skip job i
        exclude = dp[i - 1]

        # Option: take job i
        p = prev[job_idx]
        dp_prev = p + 1          # dp index for the non‑overlapping prefix
        inc_val = values[job_idx] + dp[dp_prev][0]
        inc_cnt = dp[dp_prev][1] + 1
        inc_ids = dp[dp_prev][2] + (ids[job_idx],)
        include = (inc_val, inc_cnt, inc_ids)

        # Choose best according to: max value → min count → lexicographically smallest ids
        # Use min with key = (-value, count, ids_tuple)
        best = min((exclude, include), key=lambda x: (-x[0], x[1], x[2]))
        dp.append(best)

    # Extract final solution
    max_value, _, selected_ids_tuple = dp[n]
    selected_ids = list(selected_ids_tuple)

    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }


def run_tests():
    def test_case(description, input_json, expected):
        result = process(input_json)
        assert result == expected, \
            f"Test '{description}' failed:\n  result={result}\n  expected={expected}"

    # 1  Single valid session
    test_case("single valid",
              '{"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T10:30:00", "value": 5}]}',
              {"max_value": 5, "selected_ids": ["a"], "rejected": []})

    # 2  Two non‑overlapping sessions
    test_case("two non‑overlapping",
              '{"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T10:00:00", "value": 3}, '
              '{"id": "b", "start": "2026-05-01T10:00:00", '
              '"end": "2026-05-01T11:00:00", "value": 4}]}',
              {"max_value": 7, "selected_ids": ["a", "b"], "rejected": []})

    # 3  Overlapping, pick higher value
    test_case("overlapping pick higher",
              '{"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T10:30:00", "value": 5}, '
              '{"id": "b", "start": "2026-05-01T10:00:00", '
              '"end": "2026-05-01T11:00:00", "value": 10}]}',
              {"max_value": 10, "selected_ids": ["b"], "rejected": []})

    # 4  Overlapping same value → lexicographically smaller ID
    test_case("overlapping same value",
              '{"sessions": [{"id": "b", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T10:30:00", "value": 5}, '
              '{"id": "a", "start": "2026-05-01T10:00:00", '
              '"end": "2026-05-01T11:00:00", "value": 5}]}',
              {"max_value": 5, "selected_ids": ["a"], "rejected": []})

    # 5  Same total value, fewer sessions wins
    test_case("same value fewer sessions",
              '{"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T11:00:00", "value": 10}, '
              '{"id": "b", "start": "2026-05-01T11:00:00", '
              '"end": "2026-05-01T13:00:00", "value": 10}, '
              '{"id": "c", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T13:00:00", "value": 20}]}',
              {"max_value": 20, "selected_ids": ["c"], "rejected": []})

    # 6  Lexicographic tie‑break with same value and same count
    test_case("lexicographic tie‑break",
              '{"sessions": [{"id":"a","start":"2026-05-01T09:00:00",'
              '"end":"2026-05-01T10:00:00","value":1},'
              '{"id":"b","start":"2026-05-01T10:00:00",'
              '"end":"2026-05-01T11:00:00","value":1},'
              '{"id":"c","start":"2026-05-01T09:00:00",'
              '"end":"2026-05-01T10:30:00","value":1},'
              '{"id":"d","start":"2026-05-01T10:30:00",'
              '"end":"2026-05-01T11:30:00","value":1}]}',
              {"max_value": 2, "selected_ids": ["a", "b"], "rejected": []})

    # 7  Invalid: negative value
    test_case("negative value",
              '{"sessions": [{"id": "x", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T10:00:00", "value": -1}]}',
              {"max_value": 0, "selected_ids": [],
               "rejected": [{"id": "x", "reason": "Value cannot be negative"}]})

    # 8  Invalid: end not after start
    test_case("end not after start",
              '{"sessions": [{"id": "x", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T09:00:00", "value": 5}]}',
              {"max_value": 0, "selected_ids": [],
               "rejected": [{"id": "x", "reason": "End must be after start"}]})

    # 9  Both invalid (combined reason)
    test_case("both invalid",
              '{"sessions": [{"id": "x", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T09:00:00", "value": -1}]}',
              {"max_value": 0, "selected_ids": [],
               "rejected": [{"id": "x",
                             "reason": "End must be after start; Value cannot be negative"}]})

    # 10 Mix of valid and invalid sessions
    test_case("mixed valid and invalid",
              '{"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T10:00:00", "value": 5}, '
              '{"id": "b", "start": "2026-05-01T10:00:00", '
              '"end": "2026-05-01T09:00:00", "value": 5}]}',
              {"max_value": 5, "selected_ids": ["a"],
               "rejected": [{"id": "b", "reason": "End must be after start"}]})

    # 11 All zero‑value sessions → empty set is better (fewer sessions)
    test_case("all zero value",
              '{"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", '
              '"end": "2026-05-01T10:00:00", "value": 0}, '
              '{"id": "b", "start": "2026-05-01T10:00:00", '
              '"end": "2026-05-01T11:00:00", "value": 0}]}',
              {"max_value": 0, "selected_ids": [], "rejected": []})

    # 12 Empty session list
    test_case("empty list",
              '{"sessions": []}',
              {"max_value": 0, "selected_ids": [], "rejected": []})

    print("All tests passed.")


def main():
    if '--test' in sys.argv:
        run_tests()
    else:
        input_data = sys.stdin.read()
        result = process(input_data)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
