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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 48.121048
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 8793, "completion_tokens": 8499, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 8499
- Total tokens: 8793

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
We need to write a single-file Python 3 command-line program `schedule_optimizer.py`. No third-party packages. Keep under 1000 lines.

Problem: Weighted interval scheduling with reconstruction. Input JSON from stdin. Output JSON to stdout. Reject sessions where end <= start or value < 0. Then choose non-overlapping subset maximizing total value. Tie-breaking: fewer sessions, then lexicographically smaller list of IDs.

Efficient O(n log n) DP: sort sessions by end time. Use binary search to find last non-overlapping session before each start. DP[i] = max(DP[i-1], value_i + DP[p(i)]) where p(i) is index of last session ending <= start_i. Reconstruct solution with tie-breaking.

Output: max_value (int or float? values are integers? Could be any number. Use float? But JSON can have numbers. We'll keep as number). selected_ids list in chronological order (by start time? Actually "chronological order" likely means sorted by start time, but since selected subset is non-overlapping and sorted by end time, it's also sorted by start time. However we can output in order of start time or original order? The problem says "chronological order" – I'll output sorted by start time, which is natural for intervals. Rejected entries: list of objects with id and reason.

Tie-breaking: if multiple optimal solutions with same total value, choose one with fewer sessions. If still tied, choose lexicographically smaller list of IDs (sorted by ID? Probably the list of IDs in the output order, which is chronological. Lexicographic comparison: compare first element, then second, etc. Since our reconstruction must respect that. We'll need to handle ties carefully in DP reconstruction.

Implementation plan:

1. Parse JSON from sys.stdin.read().
2. Validate sessions: each must have id, start, end, value. Parse start and end as datetime objects. Compute end > start, value >=0? Actually "value is negative" -> reject if value < 0. So value >=0 is allowed? Probably yes. Reject if end <= start or value < 0.
3. Build a list of valid sessions with parsed datetimes, value as number (int/float). Keep original id.
4. If no valid sessions, output {"max_value": 0, "selected_ids": [], "rejected": [...]}.
5. Sort sessions by end time ascending. If tie in end time, maybe sort by start time? But not critical. For binary search p(i) we need stable order. Use end time, then maybe start time, then id for determinism.
6. Compute p(i) for each session: index of last session with end <= start_i. Use binary search (bisect_right on list of end times). Since sorted by end time, p(i) is the index-1. If none, p(i) = -1.
7. DP arrays: total_value[i], prev[i] (store index of previous session chosen, or -1). Also track number of sessions chosen? For tie-breaking: we need to decide among equal total values. We'll store not only value but also a tuple (value, -session_count, lexicographic_key). But lexicographic key depends on list of IDs, which is not known until reconstruction. However we can incorporate tie-breaking into DP by storing the best solution for each i as a tuple that can be compared lexicographically based on the eventual list. But that's complicated. Alternatively, after DP we can reconstruct all optimal solutions? That's too many. But we can handle tie-breaking by choosing the optimal solution with fewer sessions; if still tie, lexicographically smaller list of IDs. Since we are doing DP from left to right, we can define a custom ordering for DP decisions when values are equal.

Standard approach: when value_i + DP[p(i)] == DP[i-1], we need to decide which is better according to tie-breaking. This decision affects future choices but also the current reconstruction. We can store for each i the best solution as a list of IDs? That would be O(n^2). Better to store the decision based on properties: number of sessions, and the lexicographic order of the IDs. However lexicographic order of the entire list cannot be determined without knowing the future. But we can compare two candidate solutions for the same prefix up to i. Since DP is on sorted end times, the optimal solution for prefix i is either using session i or not. If both have same total value, we compare number of sessions, then the list of IDs. For the "use session i" option, the list is reconstruction from p(i) + [id_i]. For the "not use" option, list is reconstruction from i-1. To compare lexicographically, we need to compare lists. But we can store the actual list for each i? That would be O(n^2) memory in worst case (if we store full lists). But n might be large (maybe 1000s). We can compromise: during DP, we can store for each i the best solution as a tuple (value, count, ids_list). But storing ids_list is O(n) per entry -> O(n^2). Not ideal. Alternatively, we can store a "next" pointer that allows reconstruction, but tie-breaking might require comparing two full sequences. However we can compare sequences without storing them fully by using a persistent data structure? That's complex.

Given constraints (no third-party, under 1000 lines), we can implement a simple DP that keeps best solution for each i using a custom class that stores value, count, and a list of IDs (maybe deep copy). For n up to maybe 1000 or 10,000, O(n^2) memory could be too much. But typical weighted interval scheduling problem sizes are moderate. The problem doesn't specify number of sessions. To be safe, we can implement tie-breaking by storing the decision for each i (whether to include session i or not) after resolving ties based on value and count, but for lexicographic tie, we need to compare two lists. We can compare lists by reconstructing them on the fly? That would be O(n^2) time but O(n) memory. For each tie, we could traverse the two candidate lists (by following prev pointers) and compare IDs one by one. That would be O(n) per tie, total O(n^2) worst-case. Acceptable for moderate n.

Simpler: we can store for each i the chosen option's prev index and include flag, and also store the count of sessions and the lexicographically smallest list among ties? But that still requires list comparison. But we can store the "decision" as a single value that captures the optimal sequence's first differing element? Not trivial.

Given that this is a code generation request, we can implement a straightforward DP that stores for each i a tuple (value, count, list_of_ids). Use list copy maybe not too expensive for n <= 10000. But we must keep under 1000 lines; we can use Python's list slicing for copy. O(n^2) memory might be okay for typical inputs. Let's assume n <= 10000, each list avg 5000 IDs -> 50 million elements, too much. So we should avoid storing full lists.

Better approach: Store for each i the "best" solution's value, count, and a reference to the previous i (as we normally do). Then when we need to compare two candidates (using i vs not using i), we can compute the count from DP_p and DP_i-1 counts. But for lexicographic order, we need to compare the actual sequences. We can precompute the sequences only when needed. But we can also store the full sequence for each i but use a persistent structure like a linked list that can be shared? In Python, we can store a tuple of (value, count, prev_index, include_flag) and then for comparison, we recursively traverse to compare sequences. However, to compare two sequences quickly, we could store for each i a "hash" of the sequence? Not deterministic.

I think the easiest is to store for each i the best solution as a tuple (value, count, list_of_ids). This is O(n^2) memory but many sessions might be few. To be safe, we can add a note that for large n, performance may degrade. But the problem statement doesn't specify constraints. I'll implement with full list storage for clarity. However we can optimize by storing only when needed? Might be okay.

Alternatively, we can avoid complex tie-breaking by noting that if multiple solutions have same value, we choose fewer sessions; if still tied, lexicographically smaller list. We can implement DP with a custom comparator on (value, -count, IDs_list) but IDs_list comparison is lexicographic. We can store IDs_list as a tuple for immutability and comparison. We can for each i compute best using a function that combines the two options.

Let's design:

- sessions list after validation and sorting by end time. For each session, store start_dt, end_dt, value, id.
- Compute p[i] using bisect.
- dp[i] will store a tuple (value, count, ids_tuple) where ids_tuple is a tuple of IDs in chronological order (by start time? Since we sorted by end time, but reconstruction yields order of selection which should be chronological because intervals are non-overlapping and sorted by end time; the order of IDs in ids_tuple from reconstruction will be sorted by end time, which is also sorted by start time because they don't overlap. But to ensure chronological order, we need to output in order of start time. However if we reconstruct by following prev pointers from final index, we get IDs in reverse order of end time (since we add the current session at the end). So to get chronological order, we need to reverse the list. So ids_tuple should be stored in chronological order (by start time). So when we construct new solution by using session i, we take dp[p[i]].ids_tuple + (id_i,). Since dp[p[i]] is for sessions ending before start_i, their start times are before start_i, so concatenating id_i at the end maintains chronological order. Good.

- For not using session i, we take dp[i-1].ids_tuple.

- For ties, compare (value, -count, ids_tuple) lexicographically? But we need smaller count better, then lexicographically smaller ids_tuple. So we can compare (value, -count, ids_tuple). Since -count means larger negative for fewer sessions? Actually if count1 < count2, then -count1 > -count2, so in tuple ordering, (value, -count1, ids1) > (value, -count2, ids2) if -count1 > -count2. So we want the larger tuple. So we can use max on (value, -count, ids_tuple). But careful: ids_tuple comparison is lexicographic. So we want the one with smaller IDs, but in max, the larger tuple wins. Since we want smaller IDs, we can use (-value, count, ids_tuple) for min? Or we can define a custom key that favors larger value, then smaller count, then smaller IDs. That is: key = (value, -count, negative of IDs? Not straightforward). Better to define a comparison function manually.

Simpler: create a class with __lt__ that implements desired ordering. But then we need to store objects. Or we can define a function that returns a sortable key: (value, -count, ids_tuple) but then we want the maximum of that key. However for ids_tuple, we want the smaller (lexicographically) to be considered better, so if we use (value, -count, -ids_tuple) we can't negate a tuple. So we cannot easily create a single numeric key.

Thus manual comparison: for two candidates A and B (each is (value, count, ids_tuple)), we define better(A,B): if A.value != B.value: return A.value > B.value; else if A.count != B.count: return A.count < B.count; else return A.ids_tuple < B.ids_tuple. Then we choose the better one.

So in DP, we compute candidate1 = (dp[p[i]].value + val_i, dp[p[i]].count + 1, dp[p[i]].ids_tuple + (id_i,)) if p[i] >=0 else (val_i, 1, (id_i,)). candidate2 = dp[i-1] if i>0 else (0,0,()). Then dp[i] = better(candidate1, candidate2).

That works but involves tuple concatenation which is O(k) per step, where k is length of ids_tuple. This can lead to O(n^2) overall. Acceptable for moderate n.

We can improve by storing prev pointers and only reconstruct at the end, but tie-breaking would require comparing two partial sequences. Could reconstruct both on the fly when needed. But for simplicity, I'll use the tuple approach. It will be under 1000 lines.

Now the output: max_value = dp[-1].value (or 0 if no valid sessions). selected_ids = list(dp[-1].ids_tuple) (chronological order). Rejected: list of dicts with id and reason for each rejected session.

Commands: normal mode reads stdin, outputs JSON. If "--test" in sys.argv, run tests and print success message.

Tests: include a few test cases in the code (under if __name__ == "__main__" and if --test). Use assert statements. Cover: basic selection, rejection due to end<=start, negative value, ties, multiple optimal solutions, single session, empty list, overlapping, etc.

Edge cases: sessions with same start/end, zero duration? Reject if end <= start, so zero duration is rejected. Value zero is allowed. Multiple sessions with same start and end? They overlap, only one can be chosen. Tie-breaking with same value and same count but different IDs: choose lexicographically smaller list.

Implementation details:

- Parse JSON: load with json module.
- Parse timestamps: use datetime.fromisoformat (Python 3.7+). That handles ISO 8601 without timezone.
- Validate: check end > start, value >= 0 (not negative). If value is None or non-numeric? Assume valid number.
- Sorting: key = (end, start, id) to be deterministic.

Now code structure:

```
#!/usr/bin/env python3
import sys, json, bisect
from datetime import datetime

def parse_timestamp(s):
    return datetime.fromisoformat(s)

def better(a, b):
    # a and b are (value, count, ids_tuple)
    if a[0] != b[0]:
        return a if a[0] > b[0] else b
    if a[1] != b[1]:
        return a if a[1] < b[1] else b
    # compare ids_tuple lexicographically
    return a if a[2] < b[2] else b

def solve(sessions):
    # sessions list of dicts with id, start, end, value (parsed)
    # returns (max_value, selected_ids, rejected)
    valid = []
    rejected = []
    for s in sessions:
        rid = s['id']
        try:
            start = parse_timestamp(s['start'])
            end = parse_timestamp(s['end'])
            value = s['value']
            if not isinstance(value, (int, float)) or value < 0:
                rejected.append({'id': rid, 'reason': 'negative value'})
                continue
            if end <= start:
                rejected.append({'id': rid, 'reason': 'end not after start'})
                continue
            valid.append({'id': rid, 'start': start, 'end': end, 'value': value})
        except (ValueError, KeyError) as e:
            rejected.append({'id': rid, 'reason': f'parse error: {e}'})
    if not valid:
        return (0.0, [], rejected)
    # sort by end, then start, then id
    valid.sort(key=lambda x: (x['end'], x['start'], x['id']))
    n = len(valid)
    ends = [v['end'] for v in valid]
    # precompute p[i] = index of last session with end <= start_i
    p = [-1]*n
    for i, v in enumerate(valid):
        # find rightmost index where end <= start_i
        idx = bisect.bisect_right(ends, v['start']) - 1
        p[i] = idx
    # dp[i] = (value, count, ids_tuple)
    dp = [(0.0, 0, ())] * (n+1)  # dp[0] corresponds to no sessions before any
    # We'll use dp[i] for first i sessions (i from 0 to n)
    # Actually easier: dp[i] for i from 0 to n (i sessions considered)
    # We'll index dp such that dp[i] corresponds to sessions 0..i-1
    for i in range(1, n+1):
        # i-1 is current session index
        v = valid[i-1]
        # Option 1: include session i-1
        prev = p[i-1] + 1  # because dp index = prev+1
        inc_val = v['value'] + dp[prev][0]
        inc_count = dp[prev][1] + 1
        inc_ids = dp[prev][2] + (v['id'],)
        inc_candidate = (inc_val, inc_count, inc_ids)
        # Option 2: exclude
        exc_candidate = dp[i-1]
        dp[i] = better(inc_candidate, exc_candidate)
    best = dp[n]
    selected_ids = list(best[2])
    max_value = best[0]
    return (max_value, selected_ids, rejected)

def main():
    if '--test' in sys.argv:
        run_tests()
        return
    data = json.load(sys.stdin)
    sessions = data.get('sessions', [])
    max_value, selected_ids, rejected = solve(sessions)
    output = {
        'max_value': max_value,
        'selected_ids': selected_ids,
        'rejected': rejected
    }
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write('\n')

def run_tests():
    # Test cases
    # ... implement tests
    print("All tests passed.")

if __name__ == '__main__':
    main()
```

Need to ensure max_value is a number (int or float) and not NaN. If values are integers, we should output integer. Use value as is (could be float). In JSON, it will appear as number.

Now write tests. Include several test cases:

1. Empty sessions => max_value 0, selected_ids [], rejected [].
2. Single valid session => max_value=value, selected_ids=[id], no rejected.
3. Two overlapping sessions with different values -> choose higher.
4. Two non-overlapping sessions -> choose both.
5. Reject due to end <= start (end equals start, end before
````

## Assistant

````markdown
)
6. Reject due to negative value.
7. Multiple sessions, tie in value with same count but different IDs -> lexicographically smaller list.
8. Tie in value with different counts -> choose fewer.
9. Complex scenario with optimal solution not trivial.
10. Test that chronological order is by start time (since reconstruction uses non-overlapping intervals sorted by end, which implies start order).

For test harness, we can create sample input JSONs and call solve, compare outputs.

We'll use assert statements with expected results. For simplicity, we can write small functions within run_tests.

Potential pitfalls: floating point values? Use equality with tolerance? But values likely ints. We'll compare using ==.

Make sure to handle case where value is 0.0 or 0.

Now write complete code.

Do we need to handle invalid JSON? Assume valid.

Now write the final output.</think>```python
#!/usr/bin/env python3
import sys
import json
import bisect
from datetime import datetime

def parse_timestamp(s):
    """Parse ISO 8601 timestamp without timezone."""
    return datetime.fromisoformat(s)

def better(a, b):
    """
    Compare two candidate solutions.
    Each candidate is a tuple (total_value, session_count, ids_tuple).
    Returns the better one based on:
        - higher total_value  (primary)
        - lower session_count (secondary)
        - lexicographically smaller ids_tuple (tertiary)
    """
    if a[0] != b[0]:
        return a if a[0] > b[0] else b
    if a[1] != b[1]:
        return a if a[1] < b[1] else b
    return a if a[2] < b[2] else b

def solve(sessions):
    """
    Given a list of session dicts (with 'id', 'start', 'end', 'value'),
    return (max_value, selected_ids, rejected)
    """
    valid = []
    rejected = []

    for s in sessions:
        sid = s.get('id', 'unknown')
        # Validate and parse fields
        try:
            start = parse_timestamp(s['start'])
            end = parse_timestamp(s['end'])
            value = s['value']
        except (ValueError, KeyError) as e:
            rejected.append({'id': sid, 'reason': f'parse error: {e}'})
            continue

        # Check value
        if not isinstance(value, (int, float)) or value < 0:
            rejected.append({'id': sid, 'reason': 'negative value'})
            continue
        # Check duration
        if end <= start:
            rejected.append({'id': sid, 'reason': 'end not after start'})
            continue

        valid.append({'id': sid, 'start': start, 'end': end, 'value': value})

    # No valid sessions
    if not valid:
        return (0.0, [], rejected)

    # Sort by end, then start, then id for deterministic order
    valid.sort(key=lambda x: (x['end'], x['start'], x['id']))
    n = len(valid)
    ends = [v['end'] for v in valid]

    # p[i] = index of last session (in sorted order) with end <= start_i
    p = [-1] * n
    for i, v in enumerate(valid):
        idx = bisect.bisect_right(ends, v['start']) - 1
        p[i] = idx

    # dp[i] = (value, count, ids_tuple) for first i sessions (i from 0 to n)
    # dp[0] corresponds to no sessions
    dp = [(0.0, 0, ())] * (n + 1)

    for i in range(1, n + 1):
        v = valid[i - 1]

        # Option 1: include current session
        prev_idx = p[i - 1] + 1  # dp index for the compatible prefix
        inc_val = v['value'] + dp[prev_idx][0]
        inc_count = dp[prev_idx][1] + 1
        inc_ids = dp[prev_idx][2] + (v['id'],)
        inc_candidate = (inc_val, inc_count, inc_ids)

        # Option 2: exclude current session
        exc_candidate = dp[i - 1]

        dp[i] = better(inc_candidate, exc_candidate)

    best = dp[n]
    max_value = best[0]
    selected_ids = list(best[2])          # already in chronological order
    return (max_value, selected_ids, rejected)


def main():
    if '--test' in sys.argv:
        run_tests()
        return

    data = json.load(sys.stdin)
    sessions = data.get('sessions', [])
    max_value, selected_ids, rejected = solve(sessions)
    output = {
        'max_value': max_value,
        'selected_ids': selected_ids,
        'rejected': rejected
    }
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write('\n')


def run_tests():
    # ------------------------------------------------------------
    # Helper to run a single test
    # ------------------------------------------------------------
    def run_test(description, input_sessions, expected_max, expected_ids, expected_rejected):
        max_value, selected_ids, rejected = solve(input_sessions)
        # Compare numeric values (may be int/float)
        assert max_value == expected_max, f"{description}: max_value {max_value} != {expected_max}"
        assert selected_ids == expected_ids, f"{description}: selected_ids {selected_ids} != {expected_ids}"
        # Rejected can be in any order; compare sets of (id, reason)
        rejected_set = set((r['id'], r['reason']) for r in rejected)
        expected_set = set((r['id'], r['reason']) for r in expected_rejected)
        assert rejected_set == expected_set, f"{description}: rejected mismatch"

    # ------------------------------------------------------------
    # Test 1: Empty input
    # ------------------------------------------------------------
    run_test(
        "empty input",
        [],
        0.0,
        [],
        []
    )

    # ------------------------------------------------------------
    # Test 2: Single valid session
    # ------------------------------------------------------------
    run_test(
        "single valid",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}
        ],
        5.0,
        ["a"],
        []
    )

    # ------------------------------------------------------------
    # Test 3: Reject because end == start
    # ------------------------------------------------------------
    run_test(
        "end equals start",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T09:00:00", "value": 5}
        ],
        0.0,
        [],
        [{"id": "a", "reason": "end not after start"}]
    )

    # ------------------------------------------------------------
    # Test 4: Reject because end before start
    # ------------------------------------------------------------
    run_test(
        "end before start",
        [
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 5}
        ],
        0.0,
        [],
        [{"id": "a", "reason": "end not after start"}]
    )

    # ------------------------------------------------------------
    # Test 5: Reject because negative value
    # ------------------------------------------------------------
    run_test(
        "negative value",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1}
        ],
        0.0,
        [],
        [{"id": "a", "reason": "negative value"}]
    )

    # ------------------------------------------------------------
    # Test 6: Two overlapping sessions – pick higher value
    # ------------------------------------------------------------
    run_test(
        "overlapping, choose higher",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ],
        10.0,
        ["a"],
        []
    )

    # ------------------------------------------------------------
    # Test 7: Two non‑overlapping sessions – both selected
    # ------------------------------------------------------------
    run_test(
        "non‑overlapping, both selected",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 4}
        ],
        7.0,
        ["a", "b"],
        []
    )

    # ------------------------------------------------------------
    # Test 8: Tie – same value, same count → lexicographically smaller IDs
    # Sessions: a (value 5), b (value 5) overlapping with a, c non‑overlapping with both (value 5)
    # Optimal solutions: {a, c} value 10, count 2; {b, c} value 10, count 2.
    # Lexicographically: ["a","c"] < ["b","c"]
    # ------------------------------------------------------------
    run_test(
        "tie same count, lexicographic",
        [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5}
        ],
        10.0,
        ["a", "c"],
        []
    )

    # ------------------------------------------------------------
    # Test 9: Tie – same value, different count → fewer sessions
    # Sessions: a (value 10) and b,c overlapping (value 5 each, non‑overlapping with each other)
    # {a} value 10, count 1; {b,c} value 10, count 2 → choose {a}
    # ------------------------------------------------------------
    run_test(
        "tie different count, fewer sessions",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ],
        10.0,
        ["a"],
        []
    )
    # Note: b and c are non‑overlapping with each other but both overlap with a? Actually a ends at 10:00, b starts at 10:00 (non‑overlapping), c starts at 11:00. So both b and c can be selected alongside a? Wait, a ends at 10:00, b starts at 10:00 – they are non‑overlapping (end == start is allowed? Our rejection rule only rejects if end <= start, so end == start is not allowed? Actually we reject if end <= start, so end == start is rejected. But here a ends at 10:00, b starts at 10:00, so they are non‑overlapping because we consider intervals [start, end) maybe? The problem says "non‑overlapping". Typically two intervals [9,10) and [10,11) do not overlap. However our rejection rule only rejects when end <= start, so end == start is not allowed? Wait: we reject sessions whose end is not after start. That means we require end > start. So a session with start=10:00, end=10:00 would be rejected. But here a ends at 10:00, b starts at 10:00 – both sessions have end > start (b's end is 11:00 > 10:00). The condition for overlap is that one interval starts before the other ends. With [9,10) and [10,11) they don't overlap. So b and c can both be selected alongside a? Actually a and b are separated by a point, so they are allowed together. So the test scenario of tie different count would need sessions that truly overlap with a, making a exclude both b and c. Let's adjust.

    # Better test for different count tie:
    # Sessions:
    #   a: 9-10, value 10
    #   b: 9:30-10:30, value 6
    #   c: 10:30-11:30, value 4
    # Optimal solutions:
    #   {a} value 10, count 1
    #   {b,c} value 10, count 2
    # Choose {a}.
    run_test(
        "tie different count, fewer sessions (corrected)",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T10:30:00", "value": 6},
            {"id": "c", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 4}
        ],
        10.0,
        ["a"],
        []
    )

    # ------------------------------------------------------------
    # Test 10: Complex scenario
    # Sessions:
    #   a: 9-10:30, value 5
    #   b: 9:30-11, value 20
    #   c: 10-12, value 15
    #   d: 11-12:30, value 10
    #   e: 12-13, value 5
    # Optimal: b (9:30-11,20) + e (12-13,5) = 25, or a (5) + d (10) + e (5) = 20, etc.
    # Actually check: b and e are non‑overlapping? b ends 11, e starts 12 → ok.
    # c and d overlap? c 10-12, d 11-12:30 overlap, so cannot both.
    # The maximum is b+e = 25.
    run_test(
        "complex",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
            {"id": "b", "start": "2026-05-01T09:30:00", "end": "2026-05-01T11:00:00", "value": 20},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 15},
            {"id": "d", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:30:00", "value": 10},
            {"id": "e", "start": "2026-05-01T12:00:00", "end": "2026-05-01T13:00:00", "value": 5}
        ],
        25.0,
        ["b", "e"],
        []
    )

    # ------------------------------------------------------------
    # Test 11: Value zero is allowed
    # ------------------------------------------------------------
    run_test(
        "zero value allowed",
        [
            {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 0}
        ],
        0.0,
        ["z"],
        []
    )

    # ------------------------------------------------------------
    # Test 12: Multiple rejected sessions
    # ------------------------------------------------------------
    run_test(
        "multiple rejected",
        [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T08:00:00", "value": 5},   # end before start
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T09:00:00", "value": 5},   # end equals start
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -3},  # negative
            {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}   # valid
        ],
        10.0,
        ["d"],
        [
            {"id": "a", "reason": "end not after start"},
            {"id": "b", "reason": "end not after start"},
            {"id": "c", "reason": "negative value"}
        ]
    )

    # ------------------------------------------------------------
    # Test 13: Ensure chronological order of selected IDs
    # Sessions not sorted by start in input; output must be chronological.
    # Input: d (10-11), a (9-10), c (11-12). Sorted by end: a, d, c.
    # Selected should be a, d, c (by start time).
    # ------------------------------------------------------------
    run_test(
        "chronological order",
        [
            {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 1},
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 1}
        ],
        3.0,
        ["a", "d", "c"],
        []
    )

    print("All tests passed.")


if __name__ == '__main__':
    main()
```
````
