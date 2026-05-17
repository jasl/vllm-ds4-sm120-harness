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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 85.430096
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 294, "total_tokens": 8724, "completion_tokens": 8430, "prompt_tokens_details": null}`
- Prompt tokens: 294
- Completion tokens: 8430
- Total tokens: 8724

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

```text
We need to write a single-file Python 3 command-line program named `schedule_optimizer.py`. No third-party packages. Code under 1000 lines.

Requirements:
- Read JSON from stdin.
- Parse ISO timestamps without timezone using Python standard library (datetime.fromisoformat).
- Reject sessions where end <= start or value < 0.
- Output JSON with max_value, selected_ids in chronological order, rejected entries with reasons.
- If multiple optimal solutions, choose one with fewer sessions; if tied, lexicographically smaller list of IDs.
- Efficient O(n log n) DP: sort by end time, binary search for last non-overlapping session.
- Include built-in tests with --test flag. Normal mode prints only JSON.

We must output only the complete Python code.

Let's structure:

- Parse args: if "--test" in sys.argv, run tests and print success message, then exit.
- Otherwise, read stdin, parse JSON, process sessions, compute optimal schedule, print JSON output.

Implementation details:

- Define a function `parse_timestamp(s)` that uses `datetime.fromisoformat(s)` and returns a datetime object. We need to compare start/end for ordering and overlap. Since no timezone, it's fine.

- Validation: for each session, check:
  - end > start (timedelta > 0)
  - value >= 0? Actually "value is negative" -> reject. So value >= 0? But value=0 allowed? Probably yes, but needs to be non-negative. However example shows positive. We'll reject if value < 0.
  - Also ensure IDs are strings? Not specified, but we can allow any. But we need to output them. Assume they can be any JSON value, but we can keep as is.

- If validation fails, add to rejected list with reason.

- For valid sessions, we need to sort by end time for DP. Since timestamps can be compared directly.

- DP:
  - Let n = number of valid sessions.
  - Sort by end time.
  - For each i (0-indexed), find p(i) = largest index j < i such that session j's end <= session i's start. Using binary search on end times.
  - Then DP array: dp[i] = max value, count[i] = number of sessions in optimal solution ending at i (or prefix?), and we need to reconstruct with tie-breaking: maximize value, then minimize count, then lexicographically smaller IDs list.

But careful: The DP typically is: dp[i] = max( dp[i-1], value[i] + dp[p(i)] ). But with tie-breaking: we need to compare two choices:
  1. Not include i: dp[i-1] (with its optimal selection for first i-1).
  2. Include i: value[i] + dp[p(i)] (with optimal selection up to p(i)).
We need to compare based on (max value, then fewer sessions, then lexicographically smaller list). Since dp[i] must store not only max value but also the number of sessions and the list of IDs (or at least a way to compare). However storing list for each i would be O(n^2) memory. Better to store dp value, count, and a reference to previous index for reconstruction. For tie-breaking, we need to compare two possible solutions. We can store for each i the optimal solution up to i as (max_value, session_count, best_prev_idx) where best_prev_idx indicates which decision was made (-1 for not include i, or p(i) if include i). And then we can reconstruct from the final state. But for tie-breaking, we need to compare lexicographically of the final list of IDs. If we store only references, we can reconstruct both candidates and compare, but that's expensive. However we can incorporate lexicographic comparison into DP by comparing the ID lists early. But note that ID lists are only for the final decision; we can compare at each step by using the fact that if value and count are equal, we need to compare the ID lists of the two choices. We can store a canonical representation of the ID list (like a tuple) but that would be O(n^2) memory. Since n could be large, but we are limited to 1000 lines, we can maybe store tuples for reconstruction? Or we can implement a comparison function that recursively compares two solutions by walking back through prev pointers. That might be O(n^2) in worst case but for ties only. Since ties might be rare, it's acceptable. We'll implement a function to get the sorted ID list from a prev array and final index. Then we can compare.

Alternative: Use DP with (value, count, list) but only store for each i when needed. Since n up to maybe 10^5, storing list for each i is too heavy. But the problem doesn't specify scale; we just need to be efficient O(n log n). We can store (value, count, next_decision) and for tie-breaking compare using a function that gets the list of IDs by following prev. Since we need lexicographic order of final selected IDs, we can compare at the end between two candidates that have same value and count. But actually the DP decision at each step might need to choose between including or not. That choice might affect not only final value/count but also the set of IDs. For tie-breaking at the final step, we can compute the two candidate lists and compare. However, the DP recurrence uses dp[i-1] and dp[p(i)]; these dp values might themselves have multiple optimal solutions with different counts/lists. We need to choose the best among the two options at each step according to the tie-breaking criteria. So we need to compare the two full solutions (the one from dp[i-1] and the one from value[i]+dp[p(i)]) using the criteria. That means we need to be able to compare two solutions at each i. If we only store (value, count) and a reference, we can't compare lists without reconstructing both. But we can store for each i the best solution as (value, count, list_of_ids). However that list_of_ids is the entire selected IDs for prefix up to i, which for i large is O(n). If we store these as lists, total memory O(n^2). Not acceptable for large n. But perhaps the problem expects moderate n? Or we can store the IDs as a tuple of IDs (strings) for each dp state, but that's still O(n^2) memory. However we can compress using a persistent data structure? Too complex.

Better approach: Since we only need to compare the two options (include i vs exclude i) at each i, and both options' solutions are represented by dp[i-1] and (dp[p(i)] + i). To compare them, we need to compare their entire ID lists. But we can compare the ID lists lexicographically without materializing them fully if we have a way to compare two solutions based on their "prefix" (i.e., the order of IDs). Since both solutions are for the same prefix (first i sessions), the ID lists will be in chronological order (sorted by end time). The lexicographic comparison of the entire list can be done by scanning both lists simultaneously until a difference. That would take O(n) time per comparison, leading to O(n^2) total in worst case. But if there are many ties, it could be heavy. Given constraints not specified, we might assume ties are rare. However to be safe, we can implement a more efficient comparison using hashing or storing the ID list as a tuple but only for states where dp value changes? Actually we can store for each i the best solution's ID list as a tuple of IDs, but we can share common prefixes using a binary tree? Overkill.

Given the problem is from a coding challenge, they likely expect a simpler approach: sort by end, compute p(i) with binary search, then DP storing value and count, and for reconstruction, we can store decision (prev). Then when we need to break ties (same value and count), we need to compare the ID lists of two solutions. We can do this at the final stage: after DP, we have the optimal value and count. But there might be multiple indices with same value and count (e.g., dp[n-1] vs another? Actually the dp[n-1] stores the optimal for all sessions. But there could be multiple ways to achieve that same max value and count within the same optimal solution? No, dp[i] is defined as optimal for first i sessions. But there might be multiple optimal solutions overall. For example, sessions with same values and same end times. The dp recurrence at each step picks one of the two options (include or exclude). If both options have same value and count, we need to pick the one with lexicographically smaller list of IDs. So at that point, we need to compare the full lists. However, we can compare recursively by traversing the prev pointers. Since the lists are in order, we can compare element by element while following prev pointers. This will take O(length of lists) per comparison. In worst case, if many ties, it could be O(n^2). But for typical small n, it's okay. The problem doesn't specify huge inputs.

Given the constraint "under 1000 lines", we can implement a straightforward DP with decision array and then compare lists when necessary using a compare function that walks the pointers. We'll implement a function `get_selected_ids(prev, final_index, sessions_sorted)` that returns a list of IDs in order (chronological). Then in DP, when value and count tie, we compare the two candidate lists by reconstructing both partially? That would be expensive if done many times. Instead, we can defer the tie-breaking to after DP: we find all final states that achieve the max value? Actually the DP only stores one optimal for each prefix. But if there are ties at a given prefix, we need to choose the best according to criteria. So we must break ties at each step. So we need to compare at each step. We can compute the candidate lists for the two choices and compare. Since each comparison may require O(n) time, worst-case O(n^2). But we can optimize by storing the ID list as a tuple, but only for states that are the result of a tie? That's complex.

Let's think of a simpler approach: Since we want lexicographically smallest list of IDs, and IDs are presumably strings, we can treat the ID list as a string of concatenated IDs separated by a delimiter. Lexicographic order of lists is equivalent to lexicographic order of concatenated IDs (with delimiter that doesn't appear in IDs). But we still need to store the concatenated string for each dp state, which is O(n^2) memory if stored explicitly. However, we can store for each state a reference to the previous state and the ID of the included session (if any). Then the string can be built by following references. For comparing two strings, we need to walk both references simultaneously. That's again O(n) per comparison. But we can store the concatenated string as a Python string (immutable, shared? No, each state would have its own string). Memory O(n^2). Not good.

Alternative: Since we need only the final output, we can use a tie-breaking rule that doesn't require comparing lists at each step if we can prove that a simple deterministic rule (e.g., choose the option that includes the session with smaller ID when values and counts are equal) yields lexicographically smallest final list? Not necessarily. Because the list order is chronological; including a session might push out others, affecting later IDs. Lexicographic comparison of list depends on all elements.

Maybe we can implement DP with tuple (value, count, list_of_ids) but we can store list_of_ids as a shared immutable sequence using a "rope" data structure? Or we can store as a tuple of IDs, but each state's tuple is a new tuple that extends the previous tuple by appending the session ID. That would be O(n^2) memory because each tuple is of length O(n) and there are O(n) of them. That's too much for large n.

Given the typical weighted interval scheduling problem, tie-breaking is often done by choosing the one with fewer sessions, and if still tied, any is fine. But the problem explicitly requires lexicographically smaller list of IDs, so we must handle it.

Perhaps we can optimize by noticing that the number of distinct values and counts might be limited, and ties may be rare. We'll implement the straightforward comparison using reconstruction at each tie. We'll assume sessions count is not huge. Also we can note that for DP, we need to compare the two candidate solutions at each i. Instead of reconstructing the full lists each time, we can compare them lazily: we can compare the last ID first? Since lists are chronological, the last ID in the list is the largest end time. For two solutions for the same prefix i, their IDs are all from sessions with end <= end[i]. The lexicographic order compares first elements. We could maintain a hash or fingerprint of the list? Not reliable.

Let's implement a simpler approach: At each dp[i], we compute three alternatives:
- Option A: exclude i -> dp[i-1]
- Option B: include i -> (value[i] + dp[p(i)].value, dp[p(i)].count + 1, dp[p(i)].list + [id[i]]).
But we can avoid storing full list by storing a decision pointer and the count. Then when tie-breaking, we compare the final lists only for the overall optimal solution, not at each step. Wait, but the tie-breaking at each step affects future dp states. If we don't break ties correctly at each step, the final optimal might be suboptimal according to the criteria. So we must break ties correctly at each inner step.

But we can break ties using a deterministic rule that doesn't require full list comparison if we can prove that the lexicographic order is consistent with a simpler rule. For example, if two solutions have same value and count, the one that ends with a smaller ID might be lexicographically smaller? Not necessarily: list [a,b] vs [a,c] are compared lexicographically: first element same, then compare second: b vs c. So the last ID matters after all previous ones. But the previous ones are determined by dp[p(i)] and dp[i-1]. The tie-breaking rule at each step affects the entire list. There might be a way to propagate a "canonical" representation.

Another idea: Since the IDs are given, we can assign a total order to sessions based on their IDs (lexicographic). Then we can incorporate that into the DP by using a tuple of (value, count, -index of last session?) Not straightforward.

Given the difficulty, maybe we can simplify by assuming that the tie-breaking requirement is only for the final optimal solution, and we can after DP find all optimal solutions (by backtracking all possibilities with same value and count) and then pick the lexicographically smallest list. That would be exponential in worst case. Not good.

Maybe we can use a DP with (value, count, best_id_list) but store the ID list as a tuple (which is hashable) and use memoization? That's heavy.

Let's consider the constraints from the problem statement: "Write a single-file Python 3 command-line program ... Keep the code under 1,000 lines." This is typical for a coding challenge where n might be up to 10^4 or 10^5, and storing ID lists per DP state might be acceptable if the IDs are short and n is moderate, but O(n^2) memory is 10^10 for n=10^5, not acceptable. However, Python overhead for tuples would be huge. So likely they expect a solution that doesn't store lists but uses a comparison function that walks the previous pointers. And they assume ties are rare.

I'll implement with DP storing (value, count, prev_index) for each i, and also a flag indicating whether include or exclude (or store previous index directly: if include, prev_index = p(i); if exclude, prev_index = i-1). Then when comparing two options (A from dp[i-1] and B from value[i]+dp[p(i)]), if value and count are equal, I need to compare the full ID lists of A and B. I'll write a function `compare_lists(prev_array, index1, index2, sessions_sorted)` that returns -1, 0, 1 by traversing both solutions and comparing IDs. It will generate the list of IDs in order for both and compare. This function might be called many times (O(n) in worst case). Each call could be O(n) leading to O(n^2). But with binary search, we have O(n log n) DP steps, but tie-breaking adds extra cost. Acceptable for moderate n.

We can optimize by storing for each dp state a "hash" or "fingerprint" of the ID list? Possibly use rolling hash to compare lexicographically in O(log n) with binary search? Not trivial.

Given the time, I'll implement with explicit list reconstruction for tie-breaking but only when value and count tie. Since value and count are integers, ties might be rare. We'll also try to cache the ID list for states that are compared multiple times? Not necessary.

I'll implement a DP with sorting by end time, binary search for p(i), then DP recurrence with tie-breaking. We'll store:
- dp_value[i]: max value for prefix up to i
- dp_count[i]: number of sessions in that optimal solution
- dp_prev[i]: index in sorted list of the previous session in the solution (or -1 if none). For exclude, dp_prev[i] = dp_prev[i-1]? Actually we need to know the solution for the chosen option. We can store a "choice" array: choice[i] = 0 for exclude, 1 for include. Then to reconstruct, we follow the choices. Alternatively, store a "prev" that points to the index of the dp state that represents the prefix right before the last session. For include: prev = p(i); for exclude: prev = i-1. Then we can reconstruct by repeatedly going to prev until -1. But then the dp state at index i represents the solution for the prefix up to i. So dp_prev[i] = j such that dp[j] is the state before including the last session (if included) or the state for the prefix without i. That works.

We also need to store the last session ID for reconstruction. Actually we can reconstruct by: start at i = n-1 (last index of sorted). While i >= 0: if choice[i] == include, then add sessions[i].id, then i = p(i); else i = i-1. That gives the list in reverse chronological order. Then reverse.

We'll store choice[i] as boolean or int.

Now for comparison: To compare two candidate solutions (A from dp[i-1] and B from value[i]+dp[p(i)]) when dp_value and dp_count equal, we need to compare the full list of IDs of A and B. But A is the optimal solution for prefix i-1 (stored via choice and dp_prev), and B is the optimal solution for prefix p(i) with session i added.
```

## Assistant

````markdown
```python
#!/usr/bin/env python3
"""
schedule_optimizer.py

Weighted interval scheduling with reconstruction, tie-breaking, and built-in tests.
"""

import sys
import json
from datetime import datetime
from bisect import bisect_right

def parse_iso_datetime(s):
    """Parse ISO-8601 datetime string without timezone info."""
    return datetime.fromisoformat(s)

def validate_sessions(sessions):
    """Validate sessions, return (valid_sessions, rejected_list)."""
    valid = []
    rejected = []
    for session in sessions:
        sid = session.get("id")
        start_str = session.get("start")
        end_str = session.get("end")
        value = session.get("value")
        # Check required fields
        if not all(k in session for k in ("id","start","end","value")):
            rejected.append({"id": sid, "reason": "Missing required field"})
            continue
        # Parse timestamps
        try:
            start = parse_iso_datetime(start_str)
            end = parse_iso_datetime(end_str)
        except Exception:
            rejected.append({"id": sid, "reason": "Invalid timestamp format"})
            continue
        # Validate order
        if end <= start:
            rejected.append({"id": sid, "reason": "End not after start"})
            continue
        # Validate value
        if value < 0:
            rejected.append({"id": sid, "reason": "Negative value"})
            continue
        valid.append({
            "id": sid,
            "start": start,
            "end": end,
            "value": value
        })
    return valid, rejected

def compute_optimal_schedule(valid_sessions):
    """DP with tie-breaking: max value, min sessions, lexicographically smallest IDs."""
    if not valid_sessions:
        return 0, [], []

    # Sort by end time
    sessions = sorted(valid_sessions, key=lambda s: s["end"])
    n = len(sessions)
    start_times = [s["start"] for s in sessions]
    end_times = [s["end"] for s in sessions]
    values = [s["value"] for s in sessions]
    ids = [s["id"] for s in sessions]

    # p[i] = largest index j < i such that end[j] <= start[i], else -1
    p = [-1] * n
    for i in range(n):
        # binary search on end_times
        idx = bisect_right(end_times, start_times[i]) - 1
        p[i] = idx

    # dp arrays
    dp_val = [0] * n
    dp_cnt = [0] * n
    # choice[i] = 0 -> exclude, 1 -> include
    choice = [0] * n

    # Base case i=0
    dp_val[0] = values[0]
    dp_cnt[0] = 1
    choice[0] = 1  # include first session

    # Helper to reconstruct list of IDs for a prefix ending at index idx (inclusive)
    # Returns list of IDs in chronological order.
    def get_ids(idx):
        ids_list = []
        i = idx
        while i >= 0:
            if choice[i] == 1:
                ids_list.append(ids[i])
                i = p[i]
            else:
                i = i - 1
        ids_list.reverse()
        return ids_list

    # Helper to compare two ID lists lexicographically
    def list_less(a, b):
        return a < b

    for i in range(1, n):
        # Option 0: exclude i
        opt0_val = dp_val[i-1]
        opt0_cnt = dp_cnt[i-1]
        # Option 1: include i
        if p[i] == -1:
            opt1_val = values[i]
            opt1_cnt = 1
        else:
            opt1_val = values[i] + dp_val[p[i]]
            opt1_cnt = dp_cnt[p[i]] + 1

        # Compare by value, then count, then lexicographic IDs
        if opt1_val > opt0_val:
            # include is better
            dp_val[i] = opt1_val
            dp_cnt[i] = opt1_cnt
            choice[i] = 1
        elif opt1_val < opt0_val:
            dp_val[i] = opt0_val
            dp_cnt[i] = opt0_cnt
            choice[i] = 0
        else:  # equal value
            if opt1_cnt < opt0_cnt:
                dp_val[i] = opt1_val
                dp_cnt[i] = opt1_cnt
                choice[i] = 1
            elif opt1_cnt > opt0_cnt:
                dp_val[i] = opt0_val
                dp_cnt[i] = opt0_cnt
                choice[i] = 0
            else:  # equal value and count
                # Compare ID lists
                # Construct both lists (could be expensive but ties expected rare)
                list0 = get_ids(i-1)
                list1 = get_ids(p[i]) if p[i] != -1 else []
                list1 = list1 + [ids[i]]
                if list_less(list1, list0):
                    dp_val[i] = opt1_val
                    dp_cnt[i] = opt1_cnt
                    choice[i] = 1
                else:
                    dp_val[i] = opt0_val
                    dp_cnt[i] = opt0_cnt
                    choice[i] = 0

    # Final optimal solution is at index n-1
    final_index = n - 1
    max_value = dp_val[final_index]
    selected_ids = get_ids(final_index)
    return max_value, selected_ids, sessions

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    data = json.load(sys.stdin)
    sessions = data.get("sessions", [])
    valid_sessions, rejected = validate_sessions(sessions)
    max_value, selected_ids, _ = compute_optimal_schedule(valid_sessions)
    output = {
        "max_value": max_value,
        "selected_ids": selected_ids,
        "rejected": rejected
    }
    print(json.dumps(output, indent=2))

# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------
def run_tests():
    import io

    def test_simple():
        data = {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:30:00", "value": 3},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 4}
            ]
        }
        sessions = data["sessions"]
        valid, rejected = validate_sessions(sessions)
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        assert max_val == 9, f"Expected 9, got {max_val}"
        assert sel_ids == ["a", "c"], f"Expected ['a','c'], got {sel_ids}"
        assert len(rejected) == 0

    def test_overlap():
        data = {
            "sessions": [
                {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10},
                {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 5}
            ]
        }
        valid, rejected = validate_sessions(data["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        assert max_val == 10, f"Expected 10, got {max_val}"
        assert sel_ids == ["x"], f"Expected ['x'], got {sel_ids}"

    def test_tie_break_count():
        # Two schedules with same value, different counts
        data = {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
            ]
        }
        # All non-overlapping, total value 15. Could pick all 3 (count=3) or pick two? Actually all three are non-overlapping? Check: a ends at 10:00, b starts at 10:00 (end==start not allowed, but b start is exactly a end, so they are non-overlapping because end <= start? Actually condition: end must be > start. a end=10:00, b start=10:00 -> start == end, so they don't overlap. Similarly b end=11:00, c start=11:00 -> non-overlapping. So all three can be selected: value 15, count 3. There's no tie. But we can test tie where two schedules have same total value but different counts.
        # Use value 9 for two sessions vs one session with value 9.
        data2 = {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 4},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 9}
            ]
        }
        valid, rejected = validate_sessions(data2["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        # Options: include c => value 9, count 1. Include a+b => value 9, count 2. Tie on value, choose fewer sessions => count 1.
        assert max_val == 9, f"Expected 9, got {max_val}"
        assert sel_ids == ["c"], f"Expected ['c'], got {sel_ids}"

    def test_tie_break_lex():
        # Same value and count, choose lexicographically smaller list of IDs
        data = {
            "sessions": [
                {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 10}
            ]
        }
        valid, rejected = validate_sessions(data["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        # Options: include c => value 10 (lose). Include a+b => value 10. So tie on value (10), count 2. Two possibilities: [a,b] (chronological order a then b) or [b,a]? But chronological order: a from 10-11, b from 9-10. Sorted by end: b ends at 10, a ends at 11. So the DP will consider sessions in order: b (ends 10), a (ends 11). The only way to get both is include a and b. The reconstructed list will be [b, a] (since b ends earlier). But lexicographically [a,b] vs [b,a] -> [a,b] smaller because 'a'<'b'. However, can we get [a,b]? That would require a to end before b, but a ends at 11, b at 10. So chronological order forces b before a. So the only list is [b,a]. So tie-breaking not applicable. We need a scenario where two different sets of sessions with same value and count produce different ID lists in chronological order.
        # Example: three sessions: a (9-10, val 1), b (10-11, val 1), c (9-11, val 2). Also add d (9-10, val 1) maybe.
        data3 = {
            "sessions": [
                {"id": "x", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1},
                {"id": "y", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 1},
                {"id": "z", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 2},
                {"id": "w", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 1}
            ]
        }
        valid, rejected = validate_sessions(data3["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        # Options:
        # - Include z: value 2, count 1.
        # - Include x and y: value 2, count 2. More sessions, worse.
        # - Include x and w? They overlap (both 9-10), cannot.
        # So no tie.
        # Let's design a tie with same count: e.g., two sessions with total value 5 each, but both non-overlapping with a third session that gives 5? Need distinct sets.
        # Use sessions: a (9-10, 5), b (10-11, 5), c (9-11, 10)? That gives 10 vs 10 with different counts. Not good.
        # To have same value and same count, consider three sessions: a (9-10, 3), b (10-11, 3), c (9-11, 6). Or a (9-10, 3), b (10-11, 3), c (9-11, 6). Again 6 vs 6 with different counts.
        # Need two sets of two sessions each with same total value and no overlap.
        # Sessions: a (9-10, 5), b (10-11, 5), c (9-10:30, 5), d (10:30-11:30, 5). Set1: {a,b} value 10, Set2: {c,d} value 10, both count 2.
        # Ensure chronology: a ends 10, b starts 10 => ok; c ends 10:30, d starts 10:30 => ok.
        # IDs: Set1: [a,b], Set2: [c,d]. Lexicographically [a,b] < [c,d] because 'a'<'c'.
        data4 = {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
                {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "d", "start": "2026-05-01T10:30:00", "end": "2026-05-01T11:30:00", "value": 5}
            ]
        }
        valid, rejected = validate_sessions(data4["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        assert max_val == 10, f"Expected 10, got {max_val}"
        # Expected selected: [a,b] because lexicographically smaller.
        assert sel_ids == ["a","b"], f"Expected ['a','b'], got {sel_ids}"

    def test_rejected():
        data = {
            "sessions": [
                {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5},
                {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:30:00", "value": 3},
                {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": -1},
                {"id": "d", "start": "2026-05-01T12:00:00", "end": "2026-05-01T12:00:00", "value": 2},
                {"id": "e", "start": "not_a_date", "end": "2026-05-01T13:00:00", "value": 2}
            ]
        }
        valid, rejected = validate_sessions(data["sessions"])
        assert len(valid) == 1 and valid[0]["id"] == "a"
        reasons = [r["reason"] for r in rejected]
        assert "End not after start" in reasons
        assert "Negative value" in reasons
        assert "End not after start" in reasons  # for d (end==start)
        assert "Invalid timestamp format" in reasons

    def test_empty():
        data = {"sessions": []}
        valid, rejected = validate_sessions(data["sessions"])
        max_val, sel_ids, _ = compute_optimal_schedule(valid)
        assert max_val == 0
        assert sel_ids == []
        assert rejected == []

    # Run all tests
    test_simple()
    test_overlap()
    test_tie_break_count()
    test_tie_break_lex()
    test_rejected()
    test_empty()
    print("All tests passed!")

if __name__ == "__main__":
    main()
```
````
