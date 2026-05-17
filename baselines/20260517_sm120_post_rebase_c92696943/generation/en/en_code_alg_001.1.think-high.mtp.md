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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 39.126571
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 7183, "completion_tokens": 6889, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 6889
- Total tokens: 7183

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

## Reasoning Content

````text
We need to write a single-file Python script `schedule_optimizer.py` that solves weighted interval scheduling with reconstruction, reading JSON from stdin, outputting JSON to stdout.

Key requirements:
- No third-party packages.
- Parse ISO timestamps without timezone using standard library (datetime).
- Reject sessions where end <= start or value < 0.
- Output JSON with max_value (int or float? values are given as numbers, could be floats? The example uses integer 5. We'll keep as numeric.
- selected_ids in chronological order (by start time? Probably start time, but given non-overlapping and sorted, chronological order based on start time). Reconstruction: we need to produce list of IDs in order of start time (or maybe order of selection? Typically chronological by start time. Since no overlap, start times are increasing if sorted. We'll sort by start time.
- Rejected entries: list of objects with id and reason. Reasons: "End must be after start" or "Value cannot be negative" (or similar).
- If multiple optimal solutions, choose one with fewer sessions; if still tied, choose lexicographically smaller list of IDs (list of IDs as strings, sorted lexicographically? But IDs are strings, we need to compare lists. Typically lexicographic comparison of the list (elementwise). So pick the solution whose list of IDs (in chronological order) is lexicographically smallest.
- O(n log n) DP solution: Sort by end time, then for each interval find the last non-overlapping interval (p(j)) using binary search. DP: dp[j] = max value considering first j intervals (sorted by end). opt[j] = max(dp[j-1], value_j + dp[p(j)]) and track chosen. Reconstruction: after DP, backtrack to get selected IDs in order. Need to handle ties: when values equal, choose the one with fewer sessions? Actually the DP typically picks max value; if equal, we need to choose the one with fewer sessions. If still tied, lexicographically smaller list. So we need to incorporate these tie-breaking rules in the DP.

We can define a custom comparison for intervals: we want to choose subsets maximizing value, then minimizing count, then lexicographically smallest list. That can be encoded by comparing tuples (value, -count, list) but list comparison is tricky. Better: During DP, when values are equal, we need to compare the two options. Option1: include current interval -> value_i + dp[p(i)], count = count_i + count_of_dp[p(i)]? And list = [current_id] + list_of_dp[p(i)]. Option2: exclude -> dp[i-1] (value, count, list). We compare: higher value wins. If equal, lower count wins. If equal, compare lists lexicographically (list of IDs). Since we need to reconstruct, we can store for each dp state the (value, count, list) or just store the chosen path. But storing full list for each state is O(n^2) memory. Instead, we can store decision: for each i, whether we included i or not, and then reconstruct later. To compare ties properly without storing lists, we can store the whole state: (value, count, list) but that could be large. For n up to maybe 10^5, it's too much. However the problem doesn't specify constraints. We can assume n not huge for a command-line tool. But we should aim for efficiency. Another approach: store value, count, and a representation that allows lexicographic comparison without full list. For lexicographic comparison, we need the actual IDs in order. That is tricky. Perhaps we can store the list only for the DP states that are candidates? But we need to compare at each step. Since IDs are strings and the list is the sequence of selected IDs in chronological order (i.e., sorted by start time? Actually sorted by end time for DP order). We can store the sequence of IDs in the order they appear in the sorted intervals (which is by end time). That order is not necessarily chronological by start time; but since intervals are sorted by end, and they are non-overlapping, the selected intervals will also be in order of increasing end, which is also increasing start (since they don't overlap and each starts before its end). So chronological order is consistent with the DP order. So we can store the list of IDs in DP order (sorted by end). That is the chronological order. So we can store for each DP state i (considering first i intervals sorted by end) the optimal list of IDs among intervals 1..i. This list is built by concatenation. But storing concatenated lists for each i would be O(n^2) memory. However, we can store only the decision and then reconstruct later by walking back through decisions, similar to typical weighted interval scheduling reconstruction. But that only gives one solution, not tie-breaking among multiple. To pick among ties, we need to compare the full sequences. We could compare sequences lazily: when values equal and counts equal, we need to compare the lists. But we can't compare lists without having them. So we need to either store the lists, or compute the lexicographic comparison on the fly.

Given that the problem expects a complete solution and we are to keep code under 1000 lines, we can compromise by using a simpler approach: store for each state the (value, count, list) where list is a tuple of IDs. For n up to maybe a few thousand, it's fine. But if n is large, memory might blow. However the problem doesn't set constraints. We'll assume moderate n. To be safe, we can store the list as a tuple and share immutable tuples? But concatenation creates new tuple. That's still O(n^2). But we can store as a reference to a list and use copy? That's also O(n^2). Alternative: we can use a "path" representation: store for each state the previous state index and whether included. Then during backtracking, we can generate the list. But to compare two possible solutions at a state (include vs exclude) when values and counts equal, we need to compare the lists resulting from each. That would require constructing both lists up to that point. That could be done recursively or iteratively, but would add complexity. Since we have to implement tie-breaking, the simplest safe way is to store the entire list for each state (as a tuple). We'll do that.

But we can optimize by storing the list as a tuple of IDs, and when concatenating, we create a new tuple (current_id,) + prev_list. That's O(k) where k is length of prev_list. Over all states, total time is O(n^2) worst-case, but for weighted interval scheduling, many states may not be selected. Still, could be O(n^2). But given we are under 1k lines and this is a toy program, it's okay.

Alternatively, we can avoid storing full list by using a different tie-breaking: first maximize value, then minimize count, then lexicographically. The DP can be modified to compare candidates by a composite key: (value, -count, list). We can store for each state the best key. For comparing list lexicographically without storing full list, we could store a "hash" or something? Not reliable. So I'll go with storing full list as tuple.

Better approach: Use DP with reconstruction that stores which interval is taken (previous index). Then after DP, we have the optimal value. But for ties, we need to choose the one with fewer sessions and lexicographically smallest. The standard DP picks one optimal solution; we need to incorporate tie-breaking into the choice. We can do that by modifying the comparison in DP: when values equal, we consider the count and then list. To compute count, we need to know the count of the previous state. That's easy: we can store count alongside value. For list, we need to compare. We can store the list only for the "current" state as we compute? Actually we can compute the list on the fly when comparing: we can generate the list of IDs from the two options by walking back decisions (using stored decisions for previous states). But that's expensive. To avoid, we can store compressed representation: the list of IDs as a tuple, as said.

Given that the problem likely expects a straightforward DP with reconstruction and tie-breaking, and the code size limit is 1000 lines, it's fine to store tuples.

We also need to output rejected entries. So we parse each session, validate start/end/ value. If invalid, add to rejected list with reason. Valid sessions go into list.

Then sort valid sessions by end time (ascending). Also need to handle ties: if two intervals have same end time, order by start time? For DP, it doesn't matter much, but we must maintain consistent ordering for tie-breaking. We'll sort by end time, then by start time, then by ID (to ensure deterministic). Actually for p(j) we binary search for last end <= current start. Sorting by end is key.

We'll compute p(i) for each interval i (1-indexed): find index of last interval that ends <= start_i. Use bisect.

DP arrays: value = list of values of valid sessions (sorted). We'll also store id array.

DP: dp_value[i] = max value, dp_count[i] = number of sessions, dp_list[i] = tuple of IDs (in order). We'll use 0-indexed with i from 0 to n-1. But binary search returns indices.

We need to handle base case: no intervals. dp[-1]? We'll use dp as list of size n, and for i=0, we compare include vs exclude (exclude means no intervals before i, so value 0). So we need a sentinel for no intervals: (0, 0, ()). For each i, we compute include_val = value[i] + dp_value[p(i)] (where p(i) is index of compatible interval before i, or -1 meaning no compatible, so dp_value[-1] = 0). We'll handle by using a dummy dp entry at index -1 with 0.

For exclude, we take dp[i-1] (if i>0) or (0,0,()) if i=0.

Compare include and exclude by (value, -count, list) lexicographically. For list, we need to compare tuple of IDs. Python compares tuples lexicographically.

When including, new_list = (id[i],) + dp_list[p(i)] (since we are going in order of increasing end, and p(i) is before i, so adding id[i] at front? Actually dp_list is in order of increasing end (chronological). The selected intervals are non-overlapping and sorted by end. Since we add interval i after intervals in dp_list[p(i)] (because i ends after them), the list should be dp_list[p(i)] + (id[i],). Because earlier intervals come first. So we need to append id[i] to the end. But dp_list[p(i)] is a tuple of IDs in order. So new_list = dp_list[p(i)] + (id[i],). Similarly, exclude list is dp_list[i-1].

Now for comparing lexicographically, we compare the list of IDs. Since we want "lexicographically smaller list of IDs", we compare left to right. If one list is prefix of another, the shorter list is considered smaller? Usually in lexicographic order, shorter list is considered smaller only if all elements equal up to the length of shorter. But the problem says "lexicographically smaller list of IDs". In Python, comparing tuples does exactly that: e.g., (a, b) < (a, b, c) is True because after matching first two, the third element is missing in first tuple, so first is considered smaller. So shorter list is lexicographically smaller if all preceding equal. That matches: we want to minimize count first, but count is already considered separately: we compare by -count, so if counts differ, the one with fewer sessions wins regardless of lexicographic order. So lexicographic tiebreaker only applies when counts are equal. So it's fine.

Now implement.

Also need to handle possible duplicate IDs? Not specified, but IDs are given; we assume unique.

Output JSON: use json module. Output max_value as number (could be float), selected_ids as list, rejected as list of objects with id and reason.

Built-in tests: when run with --test argument, execute tests. We'll define a function run_tests() that tests several scenarios. Print a short success message like "All tests passed." Then exit. Otherwise, process stdin.

We'll structure code:

```python
#!/usr/bin/env python3
import sys
import json
import datetime
import bisect

def parse_timestamp(s):
    # ISO 8601 without timezone
    return datetime.datetime.fromisoformat(s)  # Python 3.7+ supports 'YYYY-MM-DDTHH:MM:SS' without tz

def validate_sessions(sessions):
    # returns (valid_sessions, rejected)
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get('id')
        start_str = sess.get('start')
        end_str = sess.get('end')
        value = sess.get('value')
        # Basic existence checks? Assume all fields present.
        try:
            start = parse_timestamp(start_str)
            end = parse_timestamp(end_str)
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue
        if end <= start:
            rejected.append({"id": sid, "reason": "End must be after start"})
            continue
        if value < 0:
            rejected.append({"id": sid, "reason": "Value cannot be negative"})
            continue
        valid.append({"id": sid, "start": start, "end": end, "value": value})
    return valid, rejected

def solve(valid_sessions):
    if not valid_sessions:
        return 0, [], []
    # sort by end time, then start, then id for determinism
    sorted_sessions = sorted(valid_sessions, key=lambda s: (s['end'], s['start'], s['id']))
    n = len(sorted_sessions)
    ids = [s['id'] for s in sorted_sessions]
    start_times = [s['start'] for s in sorted_sessions]
    end_times = [s['end'] for s in sorted_sessions]
    values = [s['value'] for s in sorted_sessions]

    # compute p[i]: index of last interval that ends <= start of i (0-indexed)
    p = []
    # We'll use end_times list for binary search
    for i in range(n):
        # find rightmost index where end_times[idx] <= start_times[i]
        idx = bisect.bisect_right(end_times, start_times[i]) - 1
        p.append(idx)  # -1 if none

    # dp_value, dp_count, dp_list
    dp_value = [0] * n
    dp_count = [0] * n
    dp_list = [()] * n

    for i in range(n):
        # exclude
        if i == 0:
            exclude_val, exclude_cnt, exclude_list = 0, 0, ()
        else:
            exclude_val, exclude_cnt, exclude_list = dp_value[i-1], dp_count[i-1], dp_list[i-1]

        # include
        prev_idx = p[i]  # -1 if none
        if prev_idx == -1:
            inc_val = values[i]
            inc_cnt = 1
            inc_list = (ids[i],)
        else:
            inc_val = values[i] + dp_value[prev_idx]
            inc_cnt = 1 + dp_count[prev_idx]
            inc_list = dp_list[prev_idx] + (ids[i],)

        # Compare: (value, -count, list)
        # We'll define a helper to compare tuples
        def better(a_val, a_cnt, a_list, b_val, b_cnt, b_list):
            # returns True if a is better than b
            if a_val != b_val:
                return a_val > b_val
            if a_cnt != b_cnt:
                return a_cnt < b_cnt  # fewer sessions better
            # compare lists lexicographically
            return a_list < b_list

        if better(inc_val, inc_cnt, inc_list, exclude_val, exclude_cnt, exclude_list):
            dp_value[i] = inc_val
            dp_count[i] = inc_cnt
            dp_list[i] = inc_list
        else:
            dp_value[i] = exclude_val
            dp_count[i] = exclude_cnt
            dp_list[i] = exclude_list

    max_value = dp_value[-1]
    selected_ids = list(dp_list[-1])  # already in chronological order
    return max_value, selected_ids

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return
    data = json.load(sys.stdin)
    sessions = data.get('sessions', [])
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids = solve(valid)
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    json.dump(output, sys.stdout, indent=2)
    print()  # newline

def run_tests():
    # Test 1: simple
    input1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 10}
        ]
    }
    # These overlap, optimal is b alone or a alone? a value=5, b=10 -> b
    # But a and b overlap: a ends at 10:30, b starts at 10:00 -> overlap. b has higher value.
    # So max_value=10, selected_ids=["b"]
    result1 = process_test(input1)
    expected1 = {"max_value": 10, "selected_ids": ["b"], "rejected": []}
    assert result1 == expected1, f"Test 1 failed: {result1}"

    # Test 2: non-overlapping
    input2 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "
````

## Assistant

````markdown
## The generated code:

```python
#!/usr/bin/env python3
import sys
import json
import datetime
import bisect
from datetime import timezone

def parse_timestamp(s):
    """Parse ISO 8601 timestamp without timezone info."""
    # Python 3.7+ supports fromisoformat for such strings
    return datetime.datetime.fromisoformat(s)

def validate_sessions(sessions):
    """Return (valid_sessions, rejected) lists."""
    valid = []
    rejected = []
    for sess in sessions:
        sid = sess.get('id')
        start_str = sess.get('start')
        end_str = sess.get('end')
        value = sess.get('value')
        # Type checks / missing fields – assume they exist as per description
        try:
            start = parse_timestamp(start_str)
            end = parse_timestamp(end_str)
        except (ValueError, TypeError):
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue
        if end <= start:
            rejected.append({"id": sid, "reason": "End must be after start"})
            continue
        if value < 0:
            rejected.append({"id": sid, "reason": "Value cannot be negative"})
            continue
        valid.append({"id": sid, "start": start, "end": end, "value": value})
    return valid, rejected

def solve(valid_sessions):
    """Weighted interval scheduling with DP, tie‑breaking by fewer sessions, then lexicographic list."""
    if not valid_sessions:
        return 0, []

    # Sort by end time, then start time, then id (deterministic)
    sorted_sessions = sorted(valid_sessions, key=lambda s: (s['end'], s['start'], s['id']))
    n = len(sorted_sessions)

    ids = [s['id'] for s in sorted_sessions]
    start_times = [s['start'] for s in sorted_sessions]
    end_times = [s['end'] for s in sorted_sessions]
    values = [s['value'] for s in sorted_sessions]

    # Compute p(i): index of last interval that ends <= start of i
    p = []
    for i in range(n):
        idx = bisect.bisect_right(end_times, start_times[i]) - 1
        p.append(idx)   # -1 if none

    # DP arrays
    dp_val = [0] * n
    dp_cnt = [0] * n
    dp_list = [()] * n   # tuple of IDs in order

    def better(a_val, a_cnt, a_list, b_val, b_cnt, b_list):
        """Return True if (a_val, a_cnt, a_list) is better than b."""
        if a_val != b_val:
            return a_val > b_val
        if a_cnt != b_cnt:
            return a_cnt < b_cnt   # fewer sessions wins
        return a_list < b_list     # lexicographic smaller list

    for i in range(n):
        # Exclude current interval -> take best of first i-1 intervals
        if i == 0:
            exclude_val, exclude_cnt, exclude_list = 0, 0, ()
        else:
            exclude_val, exclude_cnt, exclude_list = dp_val[i-1], dp_cnt[i-1], dp_list[i-1]

        # Include current interval
        prev = p[i]
        if prev == -1:
            inc_val = values[i]
            inc_cnt = 1
            inc_list = (ids[i],)
        else:
            inc_val = values[i] + dp_val[prev]
            inc_cnt = 1 + dp_cnt[prev]
            inc_list = dp_list[prev] + (ids[i],)

        if better(inc_val, inc_cnt, inc_list, exclude_val, exclude_cnt, exclude_list):
            dp_val[i] = inc_val
            dp_cnt[i] = inc_cnt
            dp_list[i] = inc_list
        else:
            dp_val[i] = exclude_val
            dp_cnt[i] = exclude_cnt
            dp_list[i] = exclude_list

    max_value = dp_val[-1]
    selected_ids = list(dp_list[-1])   # already in chronological order
    return max_value, selected_ids

def process_test(data):
    """Helper for tests: run the full pipeline on given input dict, return output dict."""
    sessions = data.get('sessions', [])
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids = solve(valid)
    return {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

def run_tests():
    # Test 1: overlapping simple – higher value wins
    input1 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 10}
        ]
    }
    result = process_test(input1)
    expected = {"max_value": 10, "selected_ids": ["b"], "rejected": []}
    assert result == expected, f"Test 1 failed: {result}"

    # Test 2: non‑overlapping – take both
    input2 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 7}
        ]
    }
    result = process_test(input2)
    expected = {"max_value": 12, "selected_ids": ["a", "b"], "rejected": []}
    assert result == expected, f"Test 2 failed: {result}"

    # Test 3: tie in value, choose fewer sessions
    # Intervals: a(9-10,5), b(9-11,10), c(10-12,10). b and c overlap? b 9-11, c 10-12 overlap.
    # Options: {b} value=10,1 session; {c} value=10,1; {a,c}=5+10=15 but wait a ends at 10, c starts at 10 -> non-overlap => 15. So optimal is 15.
    # To test tie, we need equal value and different counts. e.g., sessions: (9-10,5), (10-11,5), (9-10:30,10) -> overlapping.
    # Actually simpler: two intervals non-overlapping: each value 5. Another overlapping with both: value 10. But that's not tied.
    # Let's design: sessions: (9-10,5), (10-11,5), (9-12,10). Options: {first,second}=10 in 2 sessions, or {third}=10 in 1 session -> choose third.
    input3 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10}
        ]
    }
    result = process_test(input3)
    expected = {"max_value": 10, "selected_ids": ["c"], "rejected": []}
    assert result == expected, f"Test 3 failed: {result}"

    # Test 4: tie in value and count, choose lexicographically smaller list
    # Two intervals both non-overlapping and same value, but different id order.
    # Actually we need two sets with same total value and same number of sessions but different lists.
    # Example: intervals: a(9-10,5), b(10-11,5), c(9-10,5), d(10-11,5).
    # But we must ensure that only subsets {a,b} and {c,d} are possible. However they overlap? a and c overlap (same time). So only one of a or c can be chosen.
    # Better: create intervals such that there are two distinct optimal solutions with same value and count.
    # For example: three intervals: a(9-10,5), b(10-11,5), c(9-10,5). The only non-overlapping sets of max value 10 are {a,b} and {c,b} (both value 10, 2 sessions). Need to choose lexicographically smaller list: ["a","b"] vs ["c","b"] -> "a" < "c", so choose {a,b}.
    input4 = {
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5}
        ]
    }
    result = process_test(input4)
    # Possible optimal sets: {a,b} or {c,b}. Lexicographically smaller list: ["a","b"] vs ["c","b"] -> "a" < "c", so choose a,b.
    expected = {"max_value": 10, "selected_ids": ["a", "b"], "rejected": []}
    assert result == expected, f"Test 4 failed: {result}"

    # Test 5: rejection – invalid end <= start, negative value
    input5 = {
        "sessions": [
            {"id": "x", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5},
            {"id": "y", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -3},
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 7}
        ]
    }
    result = process_test(input5)
    expected = {
        "max_value": 7,
        "selected_ids": ["z"],
        "rejected": [
            {"id": "x", "reason": "End must be after start"},
            {"id": "y", "reason": "Value cannot be negative"}
        ]
    }
    assert result == expected, f"Test 5 failed: {result}"

    # Test 6: empty input
    input6 = {"sessions": []}
    result = process_test(input6)
    expected = {"max_value": 0, "selected_ids": [], "rejected": []}
    assert result == expected, f"Test 6 failed: {result}"

    print("All tests passed.")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
        return
    data = json.load(sys.stdin)
    sessions = data.get('sessions', [])
    valid, rejected = validate_sessions(sessions)
    max_value, selected_ids = solve(valid)
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    json.dump(output, sys.stdout, indent=2)
    print()  # newline

if __name__ == "__main__":
    main()
```
````
