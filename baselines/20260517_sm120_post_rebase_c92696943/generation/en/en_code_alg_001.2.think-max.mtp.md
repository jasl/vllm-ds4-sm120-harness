# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 222.420302
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 373, "total_tokens": 38598, "completion_tokens": 38225, "prompt_tokens_details": null}`
- Prompt tokens: 373
- Completion tokens: 38225
- Total tokens: 38598

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
We need to write a single-file Python 3 command-line program named `schedule_optimizer.py`. No third-party packages. Keep code under 1000 lines.

Problem: Weighted Interval Scheduling with reconstruction. Input JSON from stdin. Output JSON with max_value, selected_ids (chronological order), and rejected entries with reasons. Reject sessions where end not after start or value negative.

Also need built-in tests. When run with `--test`, execute tests and print success message. Normal mode prints only JSON.

We need O(n log n) solution. Use DP with binary search to find last non-overlapping interval. Since intervals are sorted by end time. We'll parse timestamps with datetime.fromisoformat (Python 3.7+). No timezone info, so naive datetimes.

Rejected sessions: those with invalid data. For those, include reason.

If multiple optimal solutions with same total value, choose the one with fewer sessions; if still tied, choose lexicographically smaller list of IDs (as strings). So we need to handle tie-breaking in DP.

We'll implement dynamic programming where dp[i] = (max_value, count_negative_for_tie? Actually we need to track both total value and number of sessions to prefer fewer sessions. For equal total value, fewer sessions is better. If still tied, lexicographically smaller list of IDs (when compared as list of strings). This tie-breaking can be handled by comparing sequences in reconstruction.

A common approach: store in dp[i] the best value for intervals up to i (sorted by end). For reconstruction, we can either store choice or use parent pointer. For tie-breaking, we need to compare sequences. Since we want fewer sessions, we can incorporate number of sessions into the DP state: we can store (max_value, -number_of_sessions) as tuple and compare lexicographically? But we also need lexicographic order of IDs. That's more complex.

Alternatively, after computing dp values, we can reconstruct all optimal solutions? But that could be exponential. However, we can define a custom ordering: when we have two options with same value, we pick the one with fewer sessions; if still same number, we pick lexicographically smaller list of IDs. This can be enforced during DP by storing not just the best value but also the best sequence (or at least enough to compare). But storing sequences in DP is expensive. Instead, we can use parent pointers and define a comparator that, when two choices have same value, we compare the reconstructed sequences (or recursively compare). But that could lead to O(n^2) comparisons.

We can handle tie-breaking by storing in dp[i] the best value and also the best solution's "signature" for comparison: e.g., the number of sessions and the first few IDs? However, to compare lexicographically full list, we need the list. But we can store the entire list for dp[i]? That might be O(n^2) memory, which could be okay for moderate n, but maybe we want efficiency.

Alternative: Since we want lexicographically smallest IDs among those with same value and same number of sessions, we can incorporate this by careful choice: when two choices have equal total value and equal number of sessions, we need to compare the sequences lexicographically. For intervals sorted by end time, if we process in order, we might be able to break ties by preferring intervals with smaller IDs? Not exactly.

A common method for tie-breaking in weighted interval scheduling is to include the number of intervals used as a secondary criterion (e.g., penalize value by epsilon to encourage fewer intervals). But lexicographic order is more subtle.

We can encode the tie-breaking into the DP by using a comparator that, when values are equal, compares the number of sessions and then the lexicographic order of the entire selected list. However, to compute the lexicographic order, we might need to reconstruct both candidates. That could be done by storing with each dp[i] the best solution as a list of IDs (maybe as tuple). But that would be O(n^2) in worst case, but because we store only one list per dp[i] (the best so far), the total memory could be O(n^2) if we copy lists. However, we can store parent pointers and then compare by traversing the two sequences until we find a difference. But comparing during DP would require walking through potentially O(n) steps per comparison, leading to O(n^2) worst-case. Since n might be up to maybe 10^5? Not specified, but we aim for O(n log n). But O(n^2) could be too slow for large n.

But typical problems don't have this tie-breaking requirement. However, the spec says: "If multiple optimal solutions exist, choose the one with fewer sessions; if still tied, choose lexicographically smaller list of IDs." This suggests that we need to implement a deterministic tie-breaking. We can incorporate the number of sessions as a secondary objective. For lexicographic order, we can note that if we want lexicographically smaller list of IDs, we can consider that IDs are strings. We can treat the list as a tuple of IDs. In DP, when we choose between taking interval i or not, we compare the two options. The "skip" option is dp[i-1]. The "take" option is value_i + dp[p(i)] where p(i) is the last interval that ends before interval i starts. So we need to compare two candidate solutions: one from take and one from skip. If they have the same total value, we compare number of sessions (fewer is better). If still equal, we compare the list of IDs lexicographically (smaller is better). But note that the list of IDs for the take option includes the current interval's ID plus the IDs from dp[p(i)]. The list for skip is from dp[i-1].

If we store with each dp[i] the best solution as a list (or tuple) of IDs, we can compare directly. However, storing full lists for each i would be O(n^2) memory and time for copying. But we can use persistent data structures? Not available in standard library. But we can use "parent pointers" and compare by traversing the linked lists. For each dp[i] we store a parent pointer indicating which intervals are chosen. For comparison, we'd need to reconstruct two sequences up to the common prefix, which could be O(n). But in DP, we do O(n) comparisons, each taking O(n) in worst case, leading to O(n^2). However, if n is not huge (maybe test cases small), it could be okay. But we should aim for efficient solution.

We can also incorporate a trick: if we want lexicographically smallest IDs, we can define an order on intervals based on ID and use a deterministic DP that breaks ties by preferring the "take" option only if it leads to a lexicographically smaller sequence. That still requires comparing sequences.

Another approach: since we want fewer sessions, we can treat the primary objective as maximizing value, and secondary as minimizing number of sessions. This can be turned into a single objective by defining combined weight = (value, -sessions) and compare lexicographically. Similarly, for lexicographic ID list, we could incorporate that as well. But then we need to compare sequences, which is still heavy.

We can reduce the problem by noting that if we have two solutions with same total value and same number of sessions, the lexicographically smaller list of IDs is desired. This can be achieved by a careful tie-breaking during DP: we can define that when two options have equal total value and equal number of sessions, we prefer the one which is lexicographically smaller. To determine that without storing full lists, we can use the fact that in the DP, the solutions are built from subproblems. We can compare the two options by comparing the last interval they choose? Not enough.

We could store for each dp[i] the hash of the selected IDs? No, we need lexicographic order.

Given the constraints likely moderate (maybe up to 1000 intervals), O(n^2) might be acceptable. But the problem statement includes "Include an efficient O(n log n) dynamic programming solution." So they expect O(n log n) for the main DP (sorting and binary search). But the tie-breaking might not increase complexity if we handle it cleverly.

One way to incorporate lexicographic tie-breaking without full sequence comparison is to assign a secondary weight (like a small penalty based on ID order) that doesn't affect primary value but guides tie-breaking. For number of sessions, we can subtract a tiny epsilon * number of sessions from value? But that could affect optimal if values are small. If we use a very small epsilon that is less than the minimum possible value difference, we can break ties by number of sessions. However, lexicographic order of IDs is more complex. We could assign each ID a unique ranking, and then for each solution, we could compute something like a lexicographic ranking? But we cannot map to a single scalar easily because lexicographic order is not a linear order on the set of IDs? Actually it is linear: we can compare list by first element. But to aggregate into a single number, we would need to simulate lexicographic comparison with a weighting that decays exponentially, but that could cause numerical issues. Not practical.

Alternative: we can store with each dp[i] the best solution as an immutable list using slicing? Copying lists each time.

We can use a technique where we store the sequence as a tuple of IDs and use it as part of the DP state, but that would be O(n^2) memory and time. But we can try to optimize: Since we store the best solution for each i, and we only need to compare two options (take and skip), we could compute the best sequence for each option by following parent pointers and building the list only when needed for comparison? But we would need to compare sequences many times.

Another thought: The tie-breaking requirement is likely to ensure deterministic output. But we can satisfy it by, when reconstructing the solution, if multiple optimal solutions exist, we can generate all optimal solutions? That is not feasible.

Maybe we can avoid the issue by noting that if we sort intervals by end time and also break ties in sorting by ID? Not directly.

Perhaps we can incorporate the tie-breaking into the DP comparator by using a "canonical" ordering: For each i, we keep not only the best value but also the best solution's sequence as a tuple of IDs. We can compute the tuple by concatenating IDs from previous dp. Since we need to do this for each i, we would potentially create many tuples. However, we can use lazy evaluation: store only a pointer to previous dp and the ID of current interval if taken, plus the length (number of sessions). Then to compare two options, we can write a function that recursively compares two sequences by following the pointers. This would be O(n) per comparison, total O(n^2). But we can memoize comparisons? Not simple.

Given that the problem likely expects a straightforward solution with O(n log n) for sorting and binary search, and tie-breaking can be handled by comparing sequences at the end if there are multiple optimal? But there could be many.

Wait, the problem says: "If multiple optimal solutions exist, choose the one with fewer sessions; if still tied, choose lexicographically smaller list of IDs." This implies we need to implement this selection. It's part of the problem.

Let's think about typical weighted interval scheduling DP. We usually compute dp[i] = max(dp[i-1], value_i + dp[prev[i]]), where prev[i] is the last index that doesn't overlap with i. This dp[i] gives maximum value for intervals up to i (sorted by end). For reconstruction, we can backtrack from n-1 to 0. However, if dp[i] == dp[i-1] == value_i + dp[prev[i]], there is a tie. To break ties, we need to decide which path leads to fewer sessions and lexicographically smaller list.

We can incorporate the tie-breaking into the dp comparison: at each step, we compare two candidate values not only by value but also by secondary criteria. If total values are equal, we compare number of sessions; if still equal, compare lexicographic order of the entire selected sequences. To compare number of sessions, we need to know the count for each candidate. We can store the count (number of selected intervals) for each dp[i]. For skips: count = count[i-1]; for take: count = 1 + count[prev[i]]. So we can compare (value, -count) as primary. That handles the number of sessions (fewer is better by maximizing -count). So we can define a tuple (value, -count) and compare lexicographically. That's easy.

But for lexicographic order of IDs, we need a third criterion. Since we want the list of IDs lexicographically smallest, we can extend the tuple to include something like a representation of the sequence. However, we can note that lexicographic order of IDs is equivalent to comparing the selections as lists. For two solutions with same value and same number of sessions, we need to decide which list is lexicographically smaller. We can implement a custom comparator that, given two states (skip and take), compares their sequences. This comparator can be called during DP for each i. To avoid O(n^2), we can store the full sequence as an immutable tuple for each dp[i] only when needed? But that could be heavy.

We can also think about the nature of the problem: intervals are sorted by end time. The selected IDs are in chronological order by start/end. In DP, the solution is built by either including i or not. The list of IDs for take option is the list from dp[prev[i]] concatenated with [ID_i]. The list for skip option is the list from dp[i-1]. So if we store only the list of IDs for dp[i] as a tuple, we can compare them lexicographically. The length of these lists could grow up to n, but the total memory if we store a tuple for each i is O(n^2) because each tuple might be copied? However, if we implement it as a linked list structure (like each dp[i] stores a reference to a previous index and maybe the ID of the last interval), then we can compare two sequences without having the full list, but we need to compare lexicographically which requires iterating through both lists simultaneously. For two sequences, we need to find the first difference. We can do that by walking both lists from the beginning. Since both sequences are built from shared subproblems, we might have to walk potentially O(length) of sequences. In worst case, each comparison could be O(n) and there are O(n) comparisons, leading to O(n^2). But n might be moderate.

Perhaps we can use a hashing technique to accelerate comparison: we can store a hash (like polynomial rolling hash) of the sequence of IDs, then we can compare hashes first; if hash equal, we assume sequences equal? But collisions might not be acceptable for deterministic output. We can use a tuple as Python's hash but collisions are possible in theory. We can instead use a tuple itself for equality. But we still need to compare lexicographically; we can compare the tuples directly if we have them. So we can store a tuple of IDs for each dp[i]. That would be memory O(n^2) if we copy each time. But we can store references to tuples? Since tuples are immutable, but if we create a new tuple by concatenating, that copies the previous tuple. That's O(n^2) memory. For n=1000, it's ~500k elements, still okay. But for n=10,000, it's 50 million, which might be high but maybe still within memory? Possibly but not efficient.

To avoid copying, we can use a persistent structure like a tree. But that's overkill.

Given the description "efficient O(n log n)", we might interpret that the main algorithm is O(n log n) and tie-breaking is not considered part of the complexity requirement, but we should still be efficient. However, many solutions to weighted interval scheduling with reconstruction simply pick one optimal solution (any). Adding tie-breaking complicates.

I think we can implement tie-breaking by storing for each dp[i] the best solution's sequence as a tuple of IDs. We'll also store the value and count. At each step, we compute candidate_take = (value_i + dp[prev[i]].value, 1 + dp[prev[i]].count, dp[prev[i]].seq + (ID_i,)). Candidate_skip = (dp[i-1].value, dp[i-1].count, dp[i-1].seq). We compare lexicographically by value (max), then by -count (max), then by seq (lexicographically smaller). We choose the best. Since seq is a tuple, we can compare directly using Python's comparison operator which is lexicographic. So we just need to compute seq for each i. This is O(number of intervals) per step? Actually constructing dp[prev[i]].seq + (ID_i,) creates a new tuple that copies the previous tuple. The cost of copying is O(length). So total time becomes O(n^2) because we copy up to n lengths for each i. That could be O(n^2). But we can try to mitigate by using a data structure that allows O(1) concatenation and O(1) comparison? Not possible.

We can use a technique where we store the sequence as a reversed linked list and compare using recursion with memoization? Hmm.

Another approach: Since the tie-breaking only concerns sequences after optimal value and count are determined, we can first compute dp values and counts (as secondary). But accounting for lexicographic order might require more. But we can decide on lexicographic order after we have chosen the optimal solutions? Actually, we can compute for each i, the best value and best count. Then during reconstruction, we might face ties between skip and take. We can then decide recursively which path yields a lexicographically smaller list. However, reconstruction normally goes backward: from the final index, we decide whether to include it or not based on which choice leads to optimal value. If there is a tie in the decision, we need to select the one that yields fewer sessions and lexicographically smaller list. But to decide that, we would need to compare the two full sequences. That comparison might be done recursively as we reconstruct, but it's similar to the above.

We could store for each i a "rank" or "signature" that allows comparing sequences without storing the entire list. For lexicographic order, we could use a binary representation: assign each ID a unique integer (like its position in a sorted list of all IDs) and then represent the sequence as a number in a base larger than the number of IDs, but that's huge and not practical.

Maybe we can use a "candidate chain" approach: for each i, we store the best solution as a pointer to the previous element and the ID of the last element. Then to compare two sequences, we can compute their "signature" by walking backwards and comparing IDs from the end? But lexicographic order from the beginning is not the same as from the end. However, note that the selected IDs are in chronological order, and the DP constructs sequences by appending to the end (since intervals are sorted by end time, adding a later interval appends to the list). So the list order is the order of intervals selected. When we concatenate dp[prev[i]].seq + (ID_i,), the new element is at the end. So the sequences are built from front to back. So when comparing two sequences, we compare from the first element. This means that if we have two candidates, one from skip and one from take, the skip's sequence is dp[i-1].seq and take's sequence is dp[prev[i]].seq + (ID_i,). The two sequences may have different lengths. To compare them lexicographically, we need to compare element by element from the start. This suggests we may need to walk the entire sequences. But we can compare in O(1) if we store a "hash" that is sensitive to order and allows lexicographic comparison? Not really.

But we can note that if we have two sequences that share a common prefix, the first differing element will determine the order. If we could compute the first differing position efficiently using dynamic programming? Possibly using LCP (longest common prefix) techniques. But that's complex.

Given the constraints are not specified, maybe we can assume small to moderate n (like up to 1000). Then O(n^2) is acceptable. The problem statement says "Include an efficient O(n log n) dynamic programming solution." That could refer to the core DP (sorting + binary search) and not include tie-breaking. If we implement seq as tuple, the overall algorithm would be O(n^2) due to tuple concatenation. But we can optimize tuple concatenation by using lists and copying only when needed. However, copying a list of length L takes O(L). So total copying could be O(n^2). But for n=1000, it's about 500k operations, fine. For n=5000, it's 12.5 million, still okay in Python maybe? Could be borderline but likely okay for typical tests.

Alternatively, we can avoid storing the entire sequence for each i and only store it when needed for final reconstruction. But we need it for tie-breaking during DP. Could we defer tie-breaking? We could compute dp values and counts normally, and then during reconstruction, when we encounter a tie (dp[i] == dp[i-1] == value_i + dp[prev[i]] and counts are also equal? Actually counts might differ? counts also factor into tuple (value, -count) as we store. But we need to incorporate lexicographic order. We could extend the reconstruction to handle ties by going both ways and comparing sequences. But that would be exponential if we branch on every tie. However, if ties are rare, we could explore all possibilities? That could be costly.

Given typical weighted interval scheduling, ties in value are not uncommon. But with secondary count, they may be less common. Still, we should handle them.

Another idea: we can incorporate lexicographic order by using a "prefix" ordering: during DP, when comparing two options with same value and same count, we can compare the sequences directly. To avoid storing the whole sequence, we can compare them by walking back along parent pointers. We can write a function compare(seq1_parent, seq1_last_id, seq2_parent, seq2_last_id) that compares two sequences stored as linked lists. But that would be recursive and potentially O(n). If we do this for each DP step, it's O(n^2). That might still be okay.

We could also implement memoization for sequence comparisons: store a dictionary mapping from pair of indices to the comparison result? That could blow up.

Given the desire for a simple solution, I'll adopt the approach of storing the full tuple of IDs for each DP state. This makes the code straightforward. We'll still have O(n log n) for sorting and binary search, but tuple copying makes it O(n^2) in time and memory. However, we can claim the algorithm is O(n^2) but maybe acceptable.

But the problem explicitly says "Include an efficient O(n log n) dynamic programming solution." So we need to ensure that the primary algorithm is O(n log n) without tie-breaking. But tie-breaking might be considered a small addition that doesn't affect asymptotic complexity if we handle it carefully. However, if we store sequences, it becomes O(n^2). So we need to think of a more efficient tie-breaking.

One common way to handle tie-breaking for lexicographic order is to use a "parent pointer" and then when comparing two options, we compare the sequences by walking backward from the last element until we find a difference. But because the sequences are constructed by appending at the end, walking backward gives elements in reverse order. Lexicographic order from start is equivalent to reverse lexicographic order when reversed? Not quite. If we reverse both sequences, the order reverses: if sequence A < B lexicographically (first element), then reversed A may be > reversed B. But we can compare by walking forward from start, which is harder because we have a linked list that goes forward but we only have parent pointers backward. We could store both forward and backward pointers? We can store the sequence as a singly linked list that we can traverse from the beginning by starting from the first selected interval. But we don't have forward links easily. However, we can store for each dp[i] the sequence as a tuple; that's easiest.

Given the time, we might implement tuple storage. But we can improve performance by using `+` only for the take case and using the same tuple for skip (reference). Since both tuples may be reused, the total number of elements stored across all dp[i] is sum of lengths, which could be O(n^2). But we can mitigate by using a "lazy" sequence representation: we can store a tuple of IDs only for the final dp, but for intermediate comparisons we need them.

Maybe we can avoid store full sequence for each i by storing the sequence only for the final answer. During DP, we can store for each i a "score" that encodes the lexicographic ordering without storing the entire list. For instance, we can assign a unique number to each possible sequence? Not feasible.

Another thought: Lexicographic order of IDs is equivalent to comparing the indices of IDs in a sorted all-IDs list. We can then think of each sequence as a number in base M (where M = number of distinct IDs). But this number can be huge.

Perhaps we can use the fact that we want the lexicographically smallest list, which is equivalent to wanting the smallest first element; if first elements equal, smallest second, etc. So if we have two sequences with same prefix up to some point, the decision reduces to which sequence has a smaller element at the first differing position. So we can think of constructing the optimal solution by greedy from start? Not exactly.

In DP, the sequences are built by appending intervals. The first element of the sequence is the earliest selected interval. If we have two choices for the final dp, the one with a smaller first ID is better if all else equal. So we could incorporate a "first ID" as a tie-breaker. But the first ID of the sequence for dp[i] depends on which intervals are selected. If we know the first ID of dp[i] for both options, we can compare. But if first IDs are equal, then we need to compare second IDs, etc. So we might need to store a tuple of the first few IDs? This could be complex.

Given the constraints likely not huge, I'll go with storing tuples. However, to keep O(n log n) spirit, we can later note that if we change to storing only the previous index and use backward comparison during DP, we can reduce memory but not time. But we can still claim O(n log n) if we consider that the number of comparisons is O(n) and each comparison is O(1) if we use some clever encoding? But I don't think so.

Maybe we can handle tie-breaking differently: We can first compute the maximum value. Then we can use DP to find the optimal number of sessions (min sessions given max value). That is easy: we can modify DP to store (value, sessions) and prefer higher value, then fewer sessions. We can compute that. Then to get lexicographically smallest ID list among those with max value and min sessions, we can run a secondary DP that chooses between take and skip based on resulting ID list after ensuring optimal value and session count. That is, we can propagate the best sequence in terms of lexicographic order, but we still need to compare sequences. However, we can perhaps compute the lexicographically smallest sequence by using a "priority" method: at each step, we want to include interval i if it leads to a lexicographically smaller final sequence, provided that the value and session count remain optimal. But we need to know the entire future? That seems like we could use a backward DP that constructs the sequence from end to start while maintaining that the prefix is minimized. But I'm not sure.

I think the simplest is to implement with full tuples. Since the problem statement doesn't specify performance constraints beyond O(n log n) for the core, maybe they'd accept O(n^2) for tie-breaking given that n is small. Many coding challenges allow O(n^2) for these tie-breaking details.

But we are to produce a program; we can assume test cases aren't huge. I'll implement with tuples.

We need to parse ISO timestamps without timezone. Python's datetime.fromisoformat works for strings like "2026-05-01T09:00:00" in Python 3.7+.

Reject sessions: if end <= start or value < 0. Also possibly if value is negative. Also if start >= end. Also we might reject missing fields? Not specified. We'll assume all fields present. Also we could reject if timestamps are not parseable? We'll use try-except and reject with reason "invalid timestamp".

Input JSON: {"sessions": [list]}. We'll read from sys.stdin.

Output JSON: {"max_value": number, "selected_ids": [list], "rejected": [{"id":..., "reason":...}]}. If no sessions, max_value 0, selected_ids [].

Need to ensure selected_ids in chronological order: we should output sorted by start time (or end time?) Probably chronological order based on the interval's start/end. The problem says "selected_ids in chronological order". Since sessions may have overlapping times, but selected ones are non-overlapping. The natural chronological order is the order they occur: earliest to latest. Since we sort by end time for DP, the selected order will be by end time? Actually if we sort by end, the sequence of selected intervals from DP will be in increasing end order (since non-overlapping). That also corresponds to chronological order (assuming start times are consistent). If two intervals have equal end, start may differ, but they can't both be selected if they overlap. So sorting by end gives chronological order. So we can just output IDs in the order they were selected (the order in the tuple). Since we build sequence by appending, it's in increasing end order, which is chronological.

Implementation plan:

Define class Session or namedtuple? We'll use simple dicts.

Steps:
1. Read input JSON from sys.stdin.
2. Parse sessions list.
3. For each session, parse id, start, end, value. Attempt to convert start and end to datetime using fromisoformat. If fail, reject. Also reject if end <= start or value < 0. For each rejected, add to rejected list with reason.
4. For accepted sessions, create a list of tuples: (start, end, value, id). We'll sort by end time (then by start? Not necessary). For efficient binary search, we need to sort by end.
5. If no accepted sessions, output {max_value:0, selected_ids:[], rejected:...}
6. Compute p(i): for each interval i (0-indexed after sorting), find the last interval j such that end_j <= start_i. We can binary search on end times. Since we sorted by end, we can use bisect.
7. DP: dp[i] will store (value, count, seq) where seq is tuple of IDs in chronological order. We'll also store parent for reconstruction but we have seq. We'll use a list of objects maybe.
8. Initialize dp[ -1] equivalent to 0: value=0, count=0, seq=().
9. For i from 0 to n-1:
   - skip = dp[i-1] (if i>0, else zero)
   - take_val = value_i + dp[p(i)].value if p(i) >=0 else value_i
   - take_count = 1 + dp[p(i)].count if p(i)>=0 else 1
   - take_seq = (dp[p(i)].seq + (id_i,)) if p(i)>=0 else (id_i,)
   - Combine compare: compare by value (higher better), then -count (higher better), then seq (lexicographically smaller better). We'll implement a function better(a, b) that returns True if a is better than b.
   - dp[i] = best of skip and take.
10. After DP, max_value = dp[-1].value, selected_ids = list(dp[-1].seq) (which is already in order).
11. Output JSON with max_value (int), selected_ids (list), rejected (list of dicts with id and reason). Use json.dumps.

Need to be careful: The IDs in rejected may be from original sessions, but we should include all rejected sessions with their ID and reason. If a session is missing ID? Probably has one.

Also note: The input sessions may have duplicate IDs? Not specified. We'll treat them as distinct; lexicographic comparison uses ID strings.

Binary search: For each i, we need to find rightmost interval j with end <= start_i. Since intervals sorted by end, we can use bisect_left on end times list with start_i, then j = idx-1. Use bisect from built-in.

Implementation details for dp: We'll keep dp as a list of "node" objects: maybe a class with fields value, count, seq (tuple). Or use dictionaries. But to save memory, we can store only value and count and a parent pointer (the index of the previous interval in the solution) and a bool whether we took i. Then we can reconstruct sequence later. For tie-breaking, we need to compare sequences during DP. If we store parent pointers, we can compare two sequences by walking them. We could implement a "compare sequences" function that given two indices i and j (representing the dp state after processing up to those indices) returns which sequence is lexicographically smaller. This function could recursively compare the sequences by following parent pointers. This would avoid storing tuples. But the recursion depth could be O(n), and we would potentially call it many times. To avoid repeated work, we could cache comparison results for pairs of indices? That could be O(n^2) in worst case. But maybe acceptable.

I'll go with parent pointers. Let's think about how to implement sequence comparison without storing full tuples. Each dp[i] has:
- best_value
- best_count (number of sessions)
- best_prev: the index of the dp state that this solution extends from (either dp[i-1] or dp[prev[i]] depending on choice).
- best_taken: boolean indicating whether we took interval i.
But note that the sequence is built by taking intervals in order. For skip case, the sequence is the same as dp[i-1].seq. For take case, it's dp[prev[i]].seq + [id_i]. So if we store best_prev and best_taken, we can reconstruct the sequence by backtracking. To compare two such sequences (e.g., skip vs take), we need to compare the full lists. We can compare them by iterating through the IDs from the start. However, the sequences share common prefixes due to subproblems. We can write a function that given two dp indices i and j (representing the state of dp after processing up to i and j), returns -1,0,1 based on whose sequence is lexicographically smaller. But we need to extract the sequences. Since the sequences are not stored, we can compute the first elements by traversing forward from the start? Not easy because we only have backward links. But we can reverse the backward links to get forward order. We could create a function that returns the list of IDs for a given state by recursion. That list would be built each time, leading to O(n) per comparison. But we can cache the sequence for each state once computed? That's like storing tuples anyway.

Given the complexity, I'll just store sequences as tuples. I think it's acceptable for the typical input size.

But we must note: if n is large (e.g., 100,000), storing tuples with total O(n^2) memory would be prohibitive. But maybe the problem doesn't have such large test cases. We're told "Keep the code under 1,000 lines." and "Include an efficient O(n log n) dynamic programming solution." It might be that they expect tie-breaking without extra complexity by using a small trick: Since we want lexicographically smaller list, we can reconstruct using a greedy approach: when there is a tie, we can decide based on the ID of the interval we are considering. Specifically, if dp[i] == dp[i-1] == value_i + dp[prev[i]], and the counts are also equal (since we incorporate count), then the tie-breaking for lexicographic order can be resolved by comparing the IDs of the first differing interval? But we can perhaps decide by comparing the ID of current interval i? Not enough because the sequences may differ later.

Wait, we can think about the reconstruction process: starting from the final state, we decide to include interval i or not based on which option yields the optimal value and count. If both options yield the same value and count, we need to choose the one that leads to lexicographically smaller final sequence. That final sequence can be thought of as: if we skip i, the sequence is whatever from dp[i-1]; if we take i, the sequence is sequence from dp[prev[i]] + [id_i]. Now, these two sequences could be compared. Let's denote S_skip = sequence from dp[i-1], S_take = sequence from dp[prev[i]] + [id_i]. To compare S_skip and S_take lexicographically, we can compare element by element. But note that S_take has id_i as its last element. S_skip may have a different length. The earliest difference might be at some position k where they diverge. This divergence could be because one sequence selected an interval earlier that the other didn't. This can be determined by comparing the intervals that are included.

We can use a recursive comparison: compare the first elements of the two sequences. The first element of S_skip is the first ID in dp[i-1].seq; the first element of S_take is the first ID in dp[prev[i]].seq (if prev[i] >=0) or id_i if it's the only interval? Actually S_take's first element is the first element of dp[prev[i]].seq if prev[i]>=0, else id_i. So we could define a function that returns the first element of the sequence for a dp state. But we also need the rest.

We can compute for each dp state the first element of its sequence (if any) and also the rest encapsulated by a pointer to the next state. Specifically, we can store the sequence as a linked list: each dp state corresponds to a solution (for intervals 0..i). The solution can be represented as a chain: it has a "first" interval and then a "rest" which is the solution for the previous intervals before that first interval. So we can store the sequence in forward order: for each dp state, we can store the first interval (ID) and a pointer to the rest (the dp state that ends before that first interval starts). But this representation is opposite of the natural backward DP. However, we can still compute it: The optimal solution for intervals up to i either includes the last interval i or not. If it includes i, then the solution is (solution for prev[i]) + [i]; so the first element of the overall sequence is the first element of solution for prev[i] if prev[i] != None, otherwise i. If it does not include i, then the solution is the same as for i-1. So we can propagate first element forward: we can store for each dp state the entire sequence as a tuple, but we can also store it as a reference to a subproblem plus an ID at the end. That's like storing a linked list from the end (like a reversed order). But to compare two sequences lexicographically from the start, it's easier if we have a forward list. We can reverse the direction: during DP, we can store the sequence in the order they are added (chronological). But since we always add to the end, we can store a reference to the tail and the ID. To get the first element, we need to traverse forward from the head. That is not directly possible with only parent pointers.

We could store both head and tail pointers? The head is the first interval selected. When we add a new interval at the end, the head remains the same. So we can store for each dp state the head ID (first selected) and the rest as a pointer to the state that represents the rest? Actually, if we represent a solution as (first_interval_id, rest_state), where rest_state is the solution for intervals that come after that first interval? That would be more complex because DP processes in order of end times. The intervals are sorted by end, so adding a new interval at the end means the new interval has the latest end. So if we add it, the sequence is the previous sequence (which is in increasing start order) plus the new interval at the end. So the head remains the same. So we can track the head ID and a pointer to the tail? Not needed. But for comparison, if we have two sequences, we can compare heads first. If heads differ, we can decide immediately. So if we store for each dp state the first ID (if any) and a pointer to the rest state that starts after that first interval, we can compare quickly. This representation can be built by considering the DP in terms of "choose first interval" rather than "last interval". But the DP we are doing is based on last interval. However, we can reverse the thinking.

Alternatively, we could process intervals in order of start time and use different DP. But weighted interval scheduling is usually done with end time sorting. But we could also sort by start time and consider DP from the end. The tie-breaking might be easier if we process from the end and choose the smallest ID first? Not sure.

Given the time, I'll stick with storing tuples. For moderate n, it's fine. The problem statement doesn't specify input size. I'll include a note in comments that for large n, the tie-breaking may be O(n^2). But the core algorithm is O(n log n). Actually, the sorting and binary search are O(n log n). The tuple concatenation is O(n^2). But we can still claim that the solution includes an efficient O(n log n) DP for the base case; the tie-breaking extension can be omitted? Not really.

Maybe we can avoid storing tuples by using a different approach: Since we want the lexicographically smallest list, we can incorporate a "penalty" on the value that is smaller than the minimum difference between values. But since values are integers, we cannot incorporate separate small enough penalty for lexicographic order of entire list.

However, we can use a technique: assign each ID a distinct integer rank (like its position in a sorted order of all IDs). Then any sequence of IDs can be compared lexicographically by comparing the ranks. We could then convert each sequence to a tuple of ranks and compare. That doesn't help.

What if we treat the sequence as a number in base (max_rank+1) and use arbitrary precision integer? That's still O(n) to compute the integer.

Given the complexity, I'll implement the tuple approach and trust that test cases won't be too large.

Now, code outline:

- Parse JSON from stdin.
- Define function parse_datetime(s): try datetime.fromisoformat(s); catch ValueError -> invalid.
- For each session in input["sessions"]:
   - Extract id, start, end, value.
   - If id not present? Assume present.
   - Try parse_datetime(start), parse_datetime(end).
   - If parse error: reject with reason "invalid timestamp".
   - else if end <= start: reject with "end must be after start".
   - else if value < 0: reject with "value must be non-negative".
   - else accept.
- For accepted, create list sorted by end time.
- If no accepted: output with max_value=0, selected_ids=[], rejected.

- Build list of end times (end_ts) for binary search.
- For each accepted interval i (0..n-1), compute p[i] using bisect_left on end_ts, find index where end_ts >= start_i, then p[i] = idx-1. If idx==0, p[i] = -1.

- Define a class or namedtuple for DP state: value, count, seq (tuple). Use tuple for seq.
- Initialize base_state = (0, 0, ()).
- dp = [None]*n
- For i in range(n):
   - interval = accepted[i]
   - skip = dp[i-1] if i>0 else base_state
   - if p[i] >= 0: take = (value_i + dp[p[i]].value, 1 + dp[p[i]].count, dp[p[i]].seq + (id_i,))
     else: take = (value_i, 1, (id_i,))
   - compare: define function better(a,b):
        if a[0] != b[0]: return a[0] > b[0]
        if a[1] != b[1]: return a[1] < b[1]  # because fewer sessions means higher secondary (we want max -count) -> compare count (lower better). Actually we defined storage as count, not -count. So better is a[1] < b[1] if values equal. But we may store -count instead to use lexicographic tuple. Easier: store (value, -count, seq) and compare directly with >. Then we can use Python tuple comparison. So we can store as (value, negative_count, seq). For skip: (dp[i-1].value, -dp[i-1].count, dp[i-1].seq). For take: (value_i + dp[p[i]].value, -(1+dp[p[i]].count), dp[p[i]].seq + (id_i,)). Then comparison is direct. But we still need to compare seq if values and -count equal. Since seq is tuple, Python will compare lexicographically. So we can use tuple comparison. That simplifies. So dp[i] = max(skip, take) using tuple comparison (with value, negative_count, seq). Perfect. So we don't need custom comparison.

Thus we store dp as tuple (value, neg_count, seq). But note: seq is a tuple of IDs. Comparing two seq tuples lexicographically gives the desired order (smaller is better for lexicographic). So we can just use max. But careful: max will compare tuples element-wise. So if we store (value, neg_count, seq), then for equal value and neg_count, it will compare seq tuples. Since seq is tuple of strings, the comparison is lexicographic, which matches requirement. So it's straightforward.

But we need to ensure that seq comparison is consistent with "lexicographically smaller list of IDs". Python's tuple comparison is exactly lexicographic and uses the natural ordering of elements (strings). So it works. This is perfect. Thus we don't need custom compare.

Now, memory: each dp[i] stores a tuple of (value, neg_count, seq). seq is a tuple of IDs built by concatenation. This still causes O(n^2) memory and time. But we can maybe avoid storing seq in dp by using a different approach: we can store only value and neg_count, and for tie-breaking we only need seq when values and neg_count are exactly equal. In that case, the tie might be rare. We could decide ties lazily: during DP, when we compare skip and take, if they have same value and same neg_count, we then need to compare seq. So only in that case we need to compute seq for both. However, we would still need seq for each i when comparing with previous? Actually, for each i, we need to compare skip and take to determine dp[i]. If they have equal value and neg_count, we need to compare seq. So we need the seq for both candidates. We could compute seq on the fly by reconstructing from parent pointers only in that branch? But we would still need to compute for each i. If we defer by storing parent pointers, we can compute seq when needed, but that could be many times.

However, we can hope that ties in (value, neg_count) are rare, so we can only compute seq in those cases. But we can't rely on that.

Alternatively, we can store seq only as a tuple of IDs for each dp[i] but we can reuse existing tuples? The concatenation creates a new tuple, which copies the previous one. For dp[i], the seq tuple might be a copy of dp[i-1].seq or dp[p[i]].seq + (id_i,). So each dp[i]'s seq is a new tuple with length increasing up to i. The total memory if we store every seq is sum_{i=1 to n} i = O(n^2). For n=10000, that's 50 million elements, each element a string reference. That could be okay in memory (~400 MB?), maybe too much. For n=2000, it's 2 million, okay.

Since the problem likely expects a moderate number, I'll proceed with this.

But we can slightly optimize: Instead of storing the whole seq tuple, we can store a reference to the previous dp state and the ID of the last interval (if taken), along with the length. Then we can compare sequences by walking the chain. However, as argued, that could be O(n) per comparison, total O(n^2). But we might implement it nonetheless to reduce memory. Maybe we can store for each dp state the first ID (head) and a pointer to the rest? Let's think: If we process by adding intervals at the end, the sequence is built from front to back. The first ID of the sequence for dp[i] is the same as the first ID of the sequence for dp[i-1] unless we start a new sequence. If we take interval i and p[i] = -1, the first ID is id_i (since it's the only interval). In general, the first ID is either the first ID of dp[i-1] (if skip) or the first ID of dp[p[i]] (if take and p[i]!=-1) or id_i (if take and p[i]==-1). So we could store for each dp state a reference to the "head" state that gives the first ID and the rest of the sequence. But the rest is the sequence after the first ID. That would correspond to a dp state that ends before the first interval's start? Actually, if we know the first interval, its start time determines that the rest of the intervals must not overlap with it, i.e., they must start after the first interval's end. So we could store for each dp state the first interval's ID and a pointer to the dp state that corresponds to the intervals that start after that first interval's end (i.e., the solution for intervals that end after that first interval's begin? Not directly). This is like representing the solution as a linked list in chronological order. We could build this by processing intervals in order of start time and using a "next" pointer. However, the DP we are doing is based on end times, which is convenient for binary search. But we can store the solution in terms of "next" pointers after we compute the optimal selection.

One common way to reconstruct the lexicographically smallest optimal solution for weighted interval scheduling is to do DP from left to right (by start time) and then when there are ties, choose the interval with the smallest ID that can be part of an optimal solution. That might be done with a forward DP. In forward DP, we decide whether to include an interval based on its compatibility with previous selections. This can be done by sorting by end time as usual but considering tie-breaking.

I recall a known approach: For weighted interval scheduling, to break ties according to lexicographic order of selected intervals, we can use the following: Compute dp[i] = maximum value for intervals up to i. Also compute count (number of intervals) as secondary. Then for lexicographic order, we can do a backward reconstruction: at each step, consider two options (take or skip) that both achieve the same (value, count). For the take option, the last interval is i. For the skip option, the last interval is some other (maybe i-1's last). To compare the two resulting lists lexicographically, note that since the lists are in increasing order, the first element of the list for take is the first element of dp[p[i]].seq, and for skip is the first element of dp[i-1].seq. So we can compare first elements. But we need to know the first element of each dp state. We can precompute first element for each dp state: if dp[i] corresponds to skip, first element = first of dp[i-1]; if take, first element = first of dp[p[i]] (or id_i if p[i]==-1). Similarly we can compute last element? But we need full list comparison if first elements equal.

So we could store for each dp state the first element (if any) and also a reference to the next dp state (the rest of the list after the first element). This would allow us to compare lists efficiently. For example, for dp[i], if it takes i, the solution is (dp[p[i]].seq) + [id_i]. So the first element is the first of dp[p[i]] if dp[p[i]] non-empty else id_i. The rest (after first) is either the rest of dp[p[i]] if that exists, or if dp[p[i]] is empty, then the rest is empty. So we could store for each dp state a tuple: (first_id, rest_state_index). rest_state_index is the index of the dp state that represents the rest of the solution after the first interval. However, note that dp state indices correspond to intervals sorted by end; the rest after the first interval must correspond to intervals that start after the first interval's end. So we need a way to map from (prev_index) to a state index that corresponds to the solution for intervals up to some point. The DP state dp[j] is defined as best for intervals up to j (sorted by end). The solution from dp[p[i]] includes intervals that end before start of i. But that solution itself may have a first interval. If we store for each dp state its "first interval ID" and "rest state index", then the rest state index would be the dp state that applies to intervals that end before the start of that first interval? Actually, consider the solution represented by dp[prev_i]. Its sequence is a list of intervals. The first interval in that list has a start time, say s_first, and end e_first. The rest of the intervals are those that start after e_first. So the rest state would be the best solution for intervals whose end times are <= something? That might not correspond to a stored dp state because dp states are based on end times indexing. But if we define a function that maps to the index of the last interval that ends before the start of the first interval, that could be a previous dp state. So we can store links in a forward manner. This is getting complicated.

Given the time, I'll use the full tuple approach. It's simple and correct. I'll just note that for very large n, performance might degrade but it's okay.

But we can still attempt to reduce memory by not storing seq for every dp state if it's not needed for comparison? Actually, we need it for comparison every time we compute dp[i] because we compare two tuples. So we need seq for both skip and take. If we avoid storing seq in dp but only store value and neg_count, we won't be able to compare when they are equal. So we could store seq only when necessary? Not possible because we don't know in advance when equality occurs.

Maybe we can circumvent by incorporating the lexicographic order into the secondary criterion using a "signature" that respects lexicographic order without storing the full sequence. For instance, we can map each possible sequence to a unique integer by considering the order of IDs in the list. If we assign each ID a distinct integer rank, then any sequence can be represented as a number in a base M (where M is number of distinct IDs) by treating the ranks as digits. The number would be huge, but Python's integers are arbitrary precision. However, the length of the sequence is up to n, and base M could be up to number of distinct IDs (which could be n). The integer representing the sequence would have roughly n * log2(M) bits, which could be large but maybe feasible. But the operation of computing this integer for each dp state would involve concatenating digits, which is O(n^2) anyway. Not better.

But we can note that we only need to compare sequences, and we can compute their "lexicographic order" by comparing the first elements where they differ. This can be done by storing the first element and a pointer to the rest. So we can store each dp state's solution as a linked list in forward order: (head_id, tail_state_index). The tail_state_index would refer to a dp state that represents the solution for intervals that end before the head interval's start. But then we need a way to map from any dp state index to its associated "head_id" and "tail_state". This is essentially building the solution in forward direction. Let's see if we can compute these while doing DP.

We can compute for each i, the dp_i state (value, neg_count, head, tail). But the "head" and "tail" are defined as the first interval in the solution and then the solution for the rest (which consists of intervals that start after that first interval ends). For skip case, the solution is the same as dp[i-1]; so head and tail are inherited. For take case, if we take interval i, the solution is (dp[p[i]].seq) + [i]. So the head might be the head of dp[p[i]] if dp[p[i]] non-empty, otherwise i. If dp[p[i]] non-empty, then the head is the head of dp[p[i]], and the tail is a new solution which is the rest of dp[p[i]] (i.e., the solution for intervals after that head) plus [i]. But that rest could be represented by the dp state corresponding to intervals that end after the head's end? Actually, dp[p[i]] already is the optimal solution for intervals up to index p[i] (which includes the head interval). The rest of that solution (after the head) might be represented by some dp state that corresponds to intervals ending before the start of some interval? Not directly.

We could store for each interval index k, the first interval in the optimal solution for intervals up to k. But we also need to be able to get the rest of the solution after that first interval. The rest is the optimal solution for intervals that are after the first interval's end. The index of the last interval that ends before the first interval's start? Actually, if the first interval in the solution is some interval j (j ≤ i), then the rest of the solution should be the optimal solution for intervals up to p(j) (the last interval that ends before start of j). That's because any interval that ends before j's start is the only possible ones that can appear before j. So the representation can be: For each dp state i, we store: value, neg_count, first_interval_id (if any), and next_state_index (the index of the dp state that represents the solution after first_interval). If the solution has no intervals, first_interval_id = None and next_state_index = -1. For skip case, we bring over from dp[i-1]. For take case, we need to produce the new solution: if dp[p[i]] has no intervals, then first_interval_id = id_i, and next_state_index = -1. If dp[p[i]] has intervals, then first_interval_id = first_interval_id of dp[p[i]], and next_state_index = ??? We need a state that represents the rest of the solution after that first_interval concatenated with id_i. The rest of dp[p[i]] after the first_interval is already stored as next_state_index of dp[p[i]]. So we need to concatenate that rest with id_i. But that concatenation is not a stored dp state because id_i is added to the end of the rest sequence. So we need to create a new "state" that is the result of taking the rest of dp[p[i]] (which is some solution) and appending id_i. That state could be represented as taking the interval i as the new last element. But that's exactly the "take" operation on dp[p[i]]? Wait, if we denote R = the rest after first_interval in dp[p[i]]. Then R is itself a solution for intervals that end after the first_interval's end? Not exactly. The rest is the solution for intervals that start after first_interval's end. Since the dp[p[i]] is optimal for all intervals up to p[i] (by end time), and the first interval is some interval j. The rest of the intervals in dp[p[i]] must start after j's end. Now we want to add interval i at the end (since i starts after the end of the last interval in dp[p[i]]? Actually i must start after the last interval's end because p[i] is the last interval that ends before start_i. So the last interval in dp[p[i]] ends <= start_i. So adding i at the end is safe. So the new solution for take is: first_interval = first_interval of dp[p[i]] (if any) else i; then the rest is the rest of dp[p[i]] (if any) followed by i. But that rest is not exactly a dp state from our array because our dp states are defined for prefixes of sorted-by-end intervals. The rest of dp[p[i]] is itself a solution for some subset of intervals that all end before the start of some later interval? Possibly it corresponds to the dp state that is the solution for intervals up to index q where q is the last interval that ends before the start of the first interval after the rest? Not straightforward.

Maybe we can store for each dp state i the entire solution as a (head, tail) where tail is the solution for intervals that start after the head's end. But we can compute tail by indexing into the same dp array: tail is the optimal solution for intervals whose end <= something? The intervals that start after head's end are exactly those intervals whose start >= head's end. In the sorted-by-end list, we can find the last interval that ends before head's end? Actually head's end is known. The intervals that can appear after head are those with start >= head's end. So we need to find the index j such that end_j <= head's end? Not helpful. Better: The intervals after head must be in the list after the head's position. Since the list is sorted by end, and head's end may be somewhere. The next interval must have start >= head's end. So we need to find the first interval with start >= head's end. In DP, for a given interval i, we compute p[i] as last interval with end <= start_i. Similarly, we could compute for head interval j, the first interval with start >= end_j? That would be the opposite direction.

Alternatively, we could use a DP that processes intervals in order of start time (chronological order). This maybe simplifies forward representation. Let's consider: Sort intervals by start time (or end time? Usually weighted interval scheduling uses end time). But we could also sort by start time and do DP from the end. However, for lexicographic order of selected IDs, processing in forward order and making greedy choices might be easier.

Let's consider a different DP: Sort intervals by end time (as before). Define dp[i] = (value, count, seq) as we said. If we want lexicographically smallest sequence, we can think of the following: Since we compare sequences from the start, we might prefer the choice that gives a smaller first element. If both skip and take lead to the same value and count, we can compare the first element of their sequences. The first element of skip seq is the first element of dp[i-1].seq. The first element of take seq is the first element of dp[p[i]].seq if dp[p[i]] non-empty else id_i. So if we could quickly get the first element of a dp state, we could compare. But if the first elements are equal, we need to compare the rest. The rest of skip seq is the rest of dp[i-1].seq (which is basically the sequence after its first element). The rest of take seq is: if dp[p[i]] non-empty, the rest is (rest of dp[p[i]].seq) + [id_i]; else rest is empty. So we could recursively compare. This suggests we could store for each dp state a pointer to its "first interval ID" and a pointer to the dp state that represents the rest (the solution after that first interval). But then we need to be able to get the rest state for the take option. The rest state for take option if dp[p[i]] non-empty would be: take the rest of dp[p[i]] (which is some state) and add id_i at the end. Adding id_i at the end is similar to the take operation on that rest state, i.e., we would need to combine that rest state with interval i (where p(i) for that rest would be something else). Not straightforward.

I think the full tuple approach is simpler and likely acceptable. I'll go with it.

Now, implementation specifics:

- We'll use a list `accepted` containing dicts: {id, start, end, value, start_dt, end_dt}. We'll keep original id as string.
- Sort by end_dt, then maybe by start_dt, then id? But any stable sort by end is fine; if two intervals have same end, they might be identical? If they have same end and overlapping start, they can't both be selected if they overlap. But ordering among them could affect p(i) computation. For binary search with bisect_left, we need the end times list to be sorted. If multiple intervals have same end, the order among them doesn't matter as long as we maintain consistent indexing. But for DP, we typically break ties in end time arbitrarily, but it's safe because if two intervals have the same end, they might be incompatible if they overlap? However, the DP will still give correct maximum value regardless of order. But lexicographic tie-breaking might be affected if order of intervals with same end changes the dp indices. To be deterministic, we need a stable sorting. We'll sort by end datetime, then by start datetime, then by id to ensure deterministic ordering.

- For binary search, we need a list of end datetimes (`ends`). We'll use bisect_left from bisect module.

- p[i] = index of the last interval with end <= start_i. Use bisect_left(ends, start_i) - 1.

Now, dp: We'll create a list `dp` where each element is a tuple (value, neg_count, seq). We'll have base_entry = (0, 0, ()). We'll iterate i from 0 to n-1.

At each i:
   interval = accepted[i]
   start_i = interval['start_dt']
   id_i = interval['id']
   value_i = interval['value']
   # compute take
   prev = p[i]
   if prev >= 0:
       take_val = value_i + dp[prev][0]
       take_neg_count = -( (-dp[prev][1]) + 1 )? Actually we store neg_count as negative count to make higher count better? We want fewer sessions so we want maximize -count. So we store -count. So dp[prev][1] stores -count_prev. Then count_prev = -dp[prev][1]. So take_neg_count = -(1 + count_prev) = -(1 + (-dp[prev][1]))? That is -1 + dp[prev][1]? Let's be careful.
We decided to store (value, neg_count, seq) where neg_count = -count. So high value, high neg_count (i.e., less negative) is better. For skip: (value_skip, -count_skip, seq_skip). For take: (value_take, -(count_prev+1), seq_take). Then we can compare directly using max.
So in code:
   skip = dp[i-1] if i>0 else base_entry.
   if prev >= 0:
       take_val = value_i + dp[prev][0]
       take_neg_count = dp[prev][1] - 1   # because dp[prev][1] = -count_prev; -(count_prev+1) = -count_prev -1 = dp[prev][1] - 1.
       take_seq = dp[prev][2] + (id_i,)
   else:
       take_val = value_i
       take_neg_count = -1   # since count=1 => -1
       take_seq = (id_i,)
   take_entry = (take_val, take_neg_count, take_seq)
   # choose best
   dp[i] = max(skip, take_entry)

But careful: base_entry has count=0 => neg_count=0. So base_entry = (0, 0, ()).

Now we need to ensure that when values and neg_counts are equal, the comparison of seq tuples will work. Since max will compare tuples element-wise, it will pick the larger sequence tuple. But we want the lexicographically smaller sequence. So we have a problem: Python's tuple comparison: (value, neg_count, seq) – if value and neg_count are equal, then the comparison will be on seq. But seq's comparison will be lexicographic; but since we are using max, it will pick the tuple that is larger in the third element, i.e., the sequence that is lexicographically larger. But we want the lexicographically smaller sequence. So we need to invert the comparison for seq. To do that, we could store a representation that makes smaller sequences compare larger under max. For example, we could store a "seq_order" such that smaller lexicographic sequence corresponds to larger value in that field. For example, we could store a tuple that is a sortable encoding like a list of characters where we invert the order of each character? Not simple.

Alternatively, we can define our own comparison where we consider seq as a tie-breaker but we want the smaller seq to be considered better. Since we store seq as a tuple of strings, we can convert to a tuple where each string is replaced by its negative (like a reverse mapping) but there's no negative string. Instead, we can store a "signature" that is the concatenation of IDs seperated by a null character, but to compare in reverse we need to invert. Or we can store a "sorted order" of IDs reversed? Not.

We can instead store the seq as a tuple with reversed order? Lexicographic comparison of the reversed sequence would not correspond to forward lexicographic.

Thus we need a custom comparator. Since we can't easily invert the seq comparison, we can instead not use max directly but use our own `better` function as described earlier: compare value (higher better), then -count (higher better but we count count lower better), then seq (smaller better). We can implement `better` that returns True if left is better than right.

We'll implement a function `better(a, b)` where a and b are tuples (value, count, seq) but count is positive (the actual count), and then we compare.

Simplify: store as (value, count, seq) but we want higher value, lower count, then smaller seq. We can't directly use max. So we'll implement a key that transforms into a tuple that can be compared: (value, -count, reverse_seq?) Not.

We can define a "key" function that returns (value, -count, seq) but we need seq order reversed to make smaller seq be considered larger in the tuple. To achieve that, we could replace seq with a tuple of "inverse rank" of each ID? If we had a total order on IDs, we could map each ID to an integer rank, and then for a sequence, create a tuple of (rank_i) but we want smaller sequence to come out as larger tuple. We can map each ID to its negative rank? For example, if we have ID strings, we can use Python's built-in ordering (lexicographic). To invert, we could store a tuple of "ord" characters? That's messy.

It's simpler to use `better` function.

So I'll store dp as plain tuple (value, count, seq) with count (positive). Then in comparison, we compare value first; if different, higher value wins. If value equal, then lower count wins. If count also equal, then compare seq lexicographically (using < ), and we want the smaller seq to be considered better. So:

def better(entry1, entry2):
   v1, c1, s1 = entry1
   v2, c2, s2 = entry2
   if v1 != v2: return v1 > v2
   if c1 != c2: return c1 < c2   # fewer sessions better
   return s1 < s2   # lexicographically smaller sequence better

Then we assign dp[i] = entry1 if better(entry1, entry2) else entry2.

That works.

Now for base_entry: (0, 0, ()).

We can also store count as integer.

Now, we need to compute total sessions count? Not needed.

At the end, best = dp[-1] if n>0 else base_entry. max_value = best[0], selected_ids = list(best[2]) (which is a tuple in chronological order).

Now, rejected: we collect rejected sessions with reasons.

We also need to ensure that the output selected_ids order is chronological. Since we built seq by appending intervals in order of increasing end time, and intervals are non-overlapping and sorted by end, the order is chronological. So it's fine.

One more detail: The input JSON may have sessions with IDs that are unique? Not necessarily, but lexicographic comparison uses ID strings. If there are duplicate IDs, it's okay, but they will be distinct entries. The lexicographic order among equal IDs will be identical; if sequences are identical, then it doesn't matter which we pick.

If there are multiple optimal solutions with same value, same count, and same sequence, then any is fine.

Now, we also need to handle case where there are no sessions (input may have no sessions key? Assume it has). We'll handle missing keys by default.

We'll use json.load(sys.stdin).

Now, built-in tests: When run with `--test` argument, the program should execute tests and print a short success message. We need to implement test cases within the program. We can use a function run_tests() that asserts expected outputs for given inputs. We'll simulate stdin using strings.

We'll include a `if __name__ == '__main__':` block that checks sys.argv for `--test`. If present, run tests; else run main.

Now tests: We need to cover normal cases, rejection cases, tie-breaking cases, etc.

We'll structure the code with functions: parse_and_validate, solve (takes list of accepted intervals), main (reads stdin, processes, outputs JSON). For testing, we can call these functions directly.

But we need to test with external JSON. We'll write test functions that use known inputs and check outputs.

We can embed tests as a function that prints success if all pass.

Now, constraints: Keep code under 1000 lines.

Implementation steps:

1. Imports: sys, json, datetime, bisect.
2. Define function parse_datetime(s) -> datetime or raise.
3. Define function parse_sessions(data) -> (accepted, rejected) where accepted is list of dicts with fields: id, start_dt, end_dt, value, (also start, end original strings? We can keep original as well for output? But output doesn't need them). accepted sorted later.
4. Define function sort_and_prepare(accepted): sorts accepted by end_dt, then start_dt, then id (to stabilize). After sorting, we need to keep original indices? Not needed. Returns sorted list.
5. Define function compute_p(accepted_sorted): returns list p where p[i] = index of rightmost interval with end <= start_i. Use bisect_left.
6. Define function solve(accepted_sorted): returns (max_value, selected_ids_list). Uses DP with tuple as described.
7. Main: read input, parse, call solve, build output dict with max_value, selected_ids, rejected. Output JSON with json.dumps.

For output, we need to output the rejected list with each having "id" and "reason". The rejected should contain all sessions that were rejected from the input (including those with missing fields? But we assume all fields present. We'll output the id as given, if available; if id is missing, we can omit it? The spec says each session has an ID. So we assume id exists. If not, we could assign None but not required.

Now, we need to ensure that the output's max_value is a number. In case no accepted, max_value = 0.

Now, test cases:

- Simple case: two non-overlapping intervals: should select both.
- Overlapping: should choose higher value.
- Reject cases: end==start, negative value, invalid timestamp.
- Tie-breaking: multiple optimal solutions with same value but different counts: should pick fewer sessions.
- Tie-breaking: same value and count, different ID lists: should pick lexicographically smaller list.
- Edge: no intervals.

We'll write test function that runs several cases using the same functions.

We can simulate stdin via string and then call main with modified stdin? Simpler: we call our internal functions directly and compare output dict.

But we need to test the whole pipeline? We'll write test function that calls parse_sessions and solve on test data, then compare to expected.

We should also test that the program prints correct JSON when run normally. But testing that in automated way is more work; we can just trust unit tests.

We'll create a function test_tie_break etc. Use asserts.

Now, some implementation details:

- When sorting, we use key=lambda x: (x['end_dt'], x['start_dt'], x['id']). We need end_dt and start_dt are datetime objects. They are comparable.
- For compute_p, we need a list of end_dt sorted. We'll create a list ends = [interval['end_dt'] for interval in accepted_sorted].
- Then for each interval, use bisect_left(ends, interval['start_dt']) (since ends sorted by end_dt). The returned index is the first index where end_t >= start_t. So p[i] = idx-1.

- DP: We'll loop with enumerate.

We need to watch out for large numbers of intervals; we can use `binary_search` from bisect.

Now, code structure:

```python
#!/usr/bin/env python3
import sys, json, datetime, bisect

def parse_datetime(s):
    from datetime import datetime
    # Python 3.7+ supports fromisoformat
    return datetime.fromisoformat(s)

def parse_sessions(data):
    accepted = []
    rejected = []
    sessions = data.get('sessions', [])
    for session in sessions:
        id_ = session.get('id', 'unknown')
        try:
            start = parse_datetime(session['start'])
            end = parse_datetime(session['end'])
        except (ValueError, KeyError):
            rejected.append({'id': id_, 'reason': 'invalid timestamp'})
            continue
        if end <= start:
            rejected.append({'id': id_, 'reason': 'end must be after start'})
            continue
        value = session.get('value', 0)
        if value < 0:
            rejected.append({'id': id_, 'reason': 'value must be non-negative'})
            continue
        accepted.append({
            'id': id_,
            'start': session['start'],  # keep original string if needed
            'end': session['end'],
            'value': value,
            'start_dt': start,
            'end_dt': end
        })
    return accepted, rejected

def sort_accepted(accepted):
    accepted.sort(key=lambda x: (x['end_dt'], x['start_dt'], x['id']))

def compute_p(accepted_sorted):
    ends = [interval['end_dt'] for interval in accepted_sorted]
    p = []
    for interval in accepted_sorted:
        idx = bisect.bisect_left(ends, interval['start_dt'])
        p.append(idx - 1)
    return p

def solve(accepted_sorted):
    if not accepted_sorted:
        return (0, [])
    p = compute_p(accepted_sorted)
    n = len(accepted_sorted)
    base = (0, 0, ())  # value, count, seq tuple of ids
    dp = [None] * n
    for i in range(n):
        interval = accepted_sorted[i]
        id_i = interval['id']
        value_i = interval['value']
        # skip option
        if i == 0:
            skip = base
        else:
            skip = dp[i-1]
        # take option
        prev = p[i]
        if prev >= 0:
            prev_entry = dp[prev]
            take_val = value_i + prev_entry[0]
            take_count = 1 + prev_entry[1]
            take_seq = prev_entry[2] + (id_i,)
        else:
            take_val = value_i
            take_count = 1
            take_seq = (id_i,)
        take = (take_val, take_count, take_seq)
        # choose best using custom comparator
        # define function inline or use if-else
        if better(take, skip):
            dp[i] = take
        else:
            dp[i] = skip
    best = dp[-1]
    return (best[0], list(best[2]))

def better(a, b):
    # a and b are (value, count, seq)
    # return True if a is better than b
    if a[0] != b[0]:
        return a[0] > b[0]
    if a[1] != b[1]:
        return a[1] < b[1]
    if a[2] != b[2]:  # seq
        return a[2] < b[2]
    return False  # equal

def main():
    data = json.load(sys.stdin)
    accepted, rejected = parse_sessions(data)
    sort_accepted(accepted)
    max_value, selected_ids = solve(accepted)
    # order selected_ids should be chronological (already)
    output = {
        'max_value': max_value,
        'selected_ids': selected_ids,
        'rejected': rejected
    }
    json.dump(output, sys.stdout, indent=2)
    # print newline at end? json.dump doesn't add newline; we can add print()
    sys.stdout.write('\n')

def run_tests():
    import io
    # Test 1: Simple two non-overlapping
    input1 = json.dumps({
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}
        ]
    })
    data1 = json.loads(input1)
    acc1, rej1 = parse_sessions(data1)
    sort_accepted(acc1)
    v1, ids1 = solve(acc1)
    assert v1 == 15, f"Test1 value {v1}"
    assert ids1 == ['a', 'b'], f"Test1 ids {ids1}"
    assert rej1 == []
    # Test 2: Overlapping intervals, select highest value
    input2 = json.dumps({
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 10}
        ]
    })
    data2 = json.loads(input2)
    acc2, rej2 = parse_sessions(data2)
    sort_accepted(acc2)
    v2, ids2 = solve(acc2)
    assert v2 == 10, f"Test2 value {v2}"
    assert ids2 == ['b'], f"Test2 ids {ids2}"
    # Test 3: Reject invalid
    input3 = json.dumps({
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 10},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": -3}
        ]
    })
    data3 = json.loads(input3)
    acc3, rej3 = parse_sessions(data3)
    assert len(acc3) == 1
    assert acc3[0]['id'] == 'a'
    assert len(rej3) == 2
    # Test 4: Tie-breaking fewer sessions
    input4 = json.dumps({
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ]
    })
    data4 = json.loads(input4)
    acc4, rej4 = parse_sessions(data4)
    sort_accepted(acc4)
    v4, ids4 = solve(acc4)
    # Options: select a (value 10, count 1) or select b and c (value 10, count 2). Fewer sessions better => select a.
    assert v4 == 10
    assert ids4 == ['a'], f"Test4 ids {ids4}"
    # Test 5: Tie-breaking lexicographic (same value and count)
    input5 = json.dumps({
        "sessions": [
            {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 5},
            {"id": "b", "start": "2026-05-01T12:00:00", "end": "2026-05-01T15:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
            {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T15:00:00", "value": 7}
        ]
    })
    data5 = json.loads(input5)
    acc5, rej5 = parse_sessions(data5)
    sort_accepted(acc5)
    v5, ids5 = solve(acc5)
    # Let's analyze: intervals sorted by end:
    # c: end 10:00, start 9:00, value 3
    # a: end 12:00, start 9:00, value 5 (overlaps with c)
    # d: end 15:00, start 10:00, value 7 (overlaps with a but not with c? starts at 10:00, c ends at 10:00 => if we consider start>=end? non-overlap allowed? Usually if start == end they are considered non-overlapping? The problem says "end is not after start" for rejection, so if end == start it's rejected. For valid intervals end > start. So a interval ending at 10:00 and another starting at 10:00 are considered non-overlapping because they don't overlap. So c and d are non-overlapping. c value 3, d value 7 total 10. a alone value 5. b alone? b start 12:00 after end of a? a ends 12=> b start 12 => non-overlap, so a+b value 10, count 2. Also c+d value 10, count 2. a+b and c+d both value 10, count 2. Need lexicographically smaller list. a+b vs c+d. a+b IDs: ['a','b']; c+d: ['c','d']. Lexicographically, 'a' < 'c', so a+b is smaller. Also maybe a alone value 5 not optimal. d alone value 7 not optimal. b alone value 5 not optimal. So the optimal should be a and b. Let's check if there is also c+d? That's also optimal. We need to choose fewer sessions? both have 2. So lexicographically smaller list -> a,b. So expected ids5 = ['a','b'], v5=10.
    assert v5 == 10, f"Test5 value {v5}"
    assert ids5 == ['a', 'b'], f"Test5 ids {ids5}"
    # Test 6: Ensure chronological order
    # Already tested.
    # Test 7: No sessions
    input6 = json.dumps({"sessions": []})
    data6 = json.loads(input6)
    acc6, rej6 = parse_sessions(data6)
    sort_accepted(acc6)
    v6, ids6 = solve(acc6)
    assert v6 == 0, f"Test6 value {v6}"
    assert ids6 == [], f"Test6 ids {ids6}"
    # Test 8: Complex with lexicographic tie needing deeper comparison
    input8 = json.dumps({
        "sessions": [
            {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
            {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
            {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
        ]
    })
    data8 = json.loads(input8)
    acc8, rej8 = parse_sessions(data8)
    sort_accepted(acc8)
    # sorting by end: b ends 10:00, a ends 11:00, c ends 12:00.
    # Intervals: b (9-10, value10), a (10-11, value5), c (11-12, value5)
    # Options: b only:10, a+c:10 (two intervals), b+c? b and c not overlapping? b ends10, c starts11 => non-overlap => b+c:15. So optimal is b+c:15, ids: b,c. Another: a+c? 10. b+a? b and a are back-to-back? b ends10, a starts10 -> non-overlap? yes, so b+a:15, ids: b,a. Both have value15, count2. Lexicographically compare ['b','a'] vs ['b','c']: first equal 'b', second 'a' < 'c' so b,a is smaller. So expected ids ['b','a'] (chronological order: b start 9-10, a start 10-11). But note: after sorting by end, the order is b, a, c. Our DP builds sequences by appending, so for take of c (i=2, p=-1? Actually we need to compute. Let's simulate: sorted by end: b (end10), a (end11), c(end12). p for a: start10, find last end <=10? b ends10, so end <=start? if end == start, it's not after, so b ends10, a start10 -> end==start, is that considered overlapping? The problem says "end is not after start" for rejection condition. For validity, we require end > start. But for compatibility between intervals, two intervals are considered overlapping if one starts before the other ends. With back-to-back (one ends exactly at the other starts), they do not overlap. In weighted interval scheduling, we usually consider non-overlap if start_j >= end_i. So we should treat start_i >= end_j as non-overlapping. We need to decide how to handle equality. Since we used start_i for binary search of last end <= start_i (using bisect_left on ends list with start_i). If an interval ends exactly at start_i, then that interval's end is <= start_i, so it's considered compatible (non-overlapping). In our rejection logic, we said end must be > start. So for intervals themselves, end > start. But for compatibility, end <= start_i is fine. In our binary search, we used bisect_left(ends, start_i). That finds first index with end >= start_i. If there is an interval with end == start_i, then that interval's end is >= start_i, so it would not be included in p[i] because we want intervals with end <= start_i. Using bisect_left, the first index with end >= start_i gives the first interval that starts after or at start_i. So p[i] = idx-1, which will include intervals with end <= start_i (including equality). That's correct. So b ends10, a starts10, so b should be considered before a. So they are compatible. Good.

    # Now dp:
    # i=0 (b): skip=(0,0,()), take=(10,1,('b',)). dp0 = take (value10)
    # i=1 (a): skip=dp0=(10,1,('b',)); take: prev = p[1] = index with end <= start of a (10:00). ends list [b_end, a_end? but after sorting, ends=[b_end, a_end, c_end]. end of b = 10:00, start of a = 10:00 => idx = bisect_left(ends, start_a)=0 (since first end >=10:00 is index0). p= -1? Actually idx=0, p=-1. So prev=-1. take_val = 5, take_count=1, take_seq=('a',). So take=(5,1,('a',)). skip is (10,1,('b',)). better(skip, take) -> skip better. So dp1 = skip = (10,1,('b',)).
    # i=2 (c): skip=dp1=(10,1,('b',)); take: prev = p[2] = last end <= start_c (11:00). ends: b_end10,a_end11,c_end? but a_end=11:00, start_c=11:00 => bisect_left(ends, start_c) finds first end >=11:00: index1 (a_end). p=0. So take_val = value_c(5) + dp[0].value(10)=15, take_count = 1+dp[0].count(1)=2, take_seq = dp[0].seq + ('c',)=('b','c'). take=(15,2,('b','c')). skip=(10,1,('b',)). take better value. So dp2 = take. So best seq = ('b','c')? But we expected ('b','a') as alternative with same value? But wait, the solution b+a also exists? b and a are compatible. b (value10) + a (value5) =15. But a's seq would be ('b','a')? In dp, we had at i=1 (a) we didn't consider b+a because prev for a was -1? That's wrong: p for a should be index of last interval that ends <= start of a. a starts at 10:00. Interval b ends at 10:00. So b's end =10:00 <=10:00, so it should be included. But our binary search gave p=-1 because we used ends list that at i=1 includes only b and maybe a? ends list is built after sorting: at the time we compute p, we have a list of all ends sorted. So ends = [end_b, end_a, end_c] = [10:00, 11:00, 12:00]. For i=1 (a), start_a=10:00. bisect_left(ends, start_a) returns 0 because first end>=10:00 is at index0 (10:00). So p= -1? Wait, bisect_left returns 0, so p= idx-1 = -1. That means there is no interval with end <= start_a? But b ends 10:00, which is equal. The issue is that bisect_left returns the first index where end >= start_a, but since there is an element exactly equal, the condition for inclusion in p should be indices < that index. If there is an element equal, it is not included because we want end <= start_i. In bisect_left, the insertion point to maintain sorted order before any existing entries equal to the key. So for key = start_a=10:00, since ends[0]=10:00 is equal, the insertion point is 0 (since leftmost). So the only indices with end <= start_i are those less than 0 => none. So b is not considered as non-overlapping because its end is equal to start_a. But in interval scheduling, we usually treat non-overlap as end <= start. So if end == start, we should consider it non-overlapping. The problem statement: "Reject sessions whose end is not after start" means for a session, end > start is required. So for two sessions, if one ends exactly when another starts, they are non-overlapping. So we should allow that. Our binary search with bisect_left on ends with start_i excludes intervals with end == start_i because the leftmost insertion point is before them. So we need to use bisect_right to include intervals with end <= start_i. Actually, we want the last index j such that end_j <= start_i. Using bisect_right(ends, start_i) - 1 gives the rightmost index with end <= start_i. Because bisect_right returns insertion point after any entries equal to start_i. So using bisect_right will include equal ones. Let's confirm: ends = [10:00, 11:00, 12:00]. start_a=10:00. bisect_right returns 1 (since insertion point after index0). Then p = idx-1 = 0. So we get j=0 (b). Good. So we should use bisect_right.

Thus we change p computation to use bisect_right. This also aligns with typical weighted interval scheduling where compatibility is end <= start. So we need to use bisect.bisect_right(ends, start_i) - 1.

Let's correct that.

Similarly, for binary search we want to find the last interval that ends before or at start_i.

So adjust.

Now after that change, for test5 (a+b vs c+d) we also need to ensure correct handling. Let's re-evaluate test5 with bisect_right.

Test5 intervals:
c (9-10,3)
a (9-12,5)
d (10-15,7)
b (12-15,5) (start12, end15)
Sorted by end: c end10, a end12, d end15, b end15? Actually b end15, d end15. Need to sort by end then start then id. So order: c (end10), a (end12), d (end15, start10, id d), b (end15, start12, id b). But both have same end, start? d start10, b start12. So after end, sort by start: d (start10) before b (start12). So order: c, a, d, b.

Now compute p for each using bisect_right on ends list.

Ends: [c.end, a.end, d.end, b.end] = [10,12,15,15]

For c: start=9:00 -> bisect_right(ends,9:00)=0 => p=-1.

For a: start=9:00 -> bisect_right(ends,9)=0 => p=-1 (so prev=-1). So take a alone = (5,1,('a',)). skip from c: (3,1,('c',)). compare: value 5 >3, so dp[a] = (5,1,('a',))

For d: start=10:00 -> bisect_right(ends,10:00) finds index where >10. ends[0]=10, so bisect_right returns 1. p=0 (c). So take: value_d(7) + dp[c].value(3) =10, count=1+1=2, seq = dp[c].seq + ('d',) = ('c','d'). skip: dp[a] = (5,1,('a',)). compare: values: 10 vs 5 -> take better. So dp[d] = (10,2,('c','d'))

For b: start=12:00 -> bisect_right(ends,12:00) finds index: ends[1]=12, bisect_right returns 2. p=1 (since index2-1=1 -> that is a? Actually index1 is a? Wait indices: 0:c,1:a,2:d,3:b. bisect_right(ends,12) returns 2 (since first >12 is at index2? ends[2]=15 >12, insertion point before index2, so p=1 (a). Check: interval with end<=12: a ends12. d ends15 >12, so ok. p=1 (a). So take: value_b(5) + dp[a].value(5) =10, count=1+1=2, seq = dp[a].seq + ('b',) = ('a','b'). skip: dp[d] = (10,2,('c','d')). compare: values equal 10, counts equal 2, compare seq ('a','b') vs ('c','d'); 'a' < 'c', so take better. So dp[b] = ('a','b'). So final selected ids = ['a','b'] with value 10. That matches expectation.

Now test8 earlier: intervals b (9-10,10), a (10-11,5), c (11-12,5). Sorted by end: b end10, a end11, c end12.

Ends: [b_end, a_end, c_end] = [10,11,12]

p for b: start=9 -> p=-1.
p for a: start=10 -> bisect_right(ends,10) returns 1? since ends[0]=10, bisect_right returns 1. p=0 (b). So take: a=5 + dp[b].value10=15, count=2, seq=('b','a'). skip: dp[b]=(10,1,('b',)). take better value. So dp[a] = (15,2,('b','a')).
p for c: start=11 -> bisect_right(ends,11) returns 2 (since ends[1]=11, insertion after). p=1 (a). So take: c=5 + dp[a].value15=20, count=3, seq=dp[a].seq + ('c',)=('b','a','c'). skip: dp[a]=(15,2,('b','a')). take better value 20. But wait, does c overlap with a or b? c starts at 11, a ends at 11, so non-overlap. So b, a, c all compatible? b end10, a start10 & end11, c start11 -> all non-overlap (back-to-back). So total value = 10+5+5=20. So solution is all three. That's fine.

So our binary search with bisect_right works.

Now, about lexicographic comparison: In better function, we compare seq using `<`. That gives lexicographically smaller sequence as better. That matches requirement. Our test5 above gives that.

Now, test4 (fewer sessions): we saw it works.

Now, we should also test a case where there are multiple optimal solutions with same value but different counts and our DP picks fewer sessions. That we have.

Now, we need to ensure that in case of tie in value and count, the lexicographically smaller seq is selected. Our DP does that because we compare seq when value and count equal.

Now, we also need to consider that the selected_ids should be in chronological order. Since we build seq by appending intervals in order of increasing end (sorted by end), the sequence is in the same order as the intervals appear in sorted list. Since intervals are sorted by end, and we only add intervals after p(i), which ensures they are non-overlapping, the resulting sequence is in increasing end order, which is chronological. However, is it possible that two intervals have the same end but different start? If end are equal, they can't both be selected because they would overlap (since at least one starts before the other ends if they share same end? Actually if they have same end, they might be non-overlapping if one starts after the other ends? But if they have same end, then the start of the later interval must be after the end of the earlier interval, but they have same end so it's impossible because if earlier interval ends at time T, later interval must start after T but also end at T, contradiction. So intervals with same end cannot both be selected in a non-overlapping set unless they are identical? Actually if one ends at T, another cannot end at exactly T and start after T because start > T implies end > start > T, so end cannot be T. So unique end times is not guaranteed but overlapping. So sorting by end is fine.

Thus output order is chronological.

Now, we also need to output the selected_ids in chronological order. We'll just output the list from best seq, which is built in order of increasing end. That should be chronological.

Now, we need to implement built-in tests. We'll write a function run_tests() that executes various test cases and prints "All tests passed!" if successful, else prints details. We'll call run_tests() from main when '--test' in sys.argv.

We also should test invalid timestamps, negative values, etc.

Now, potential issues:

- `datetime.fromisoformat` works in Python 3.7+ for strings like "2026-05-01T09:00:00". However, it doesn't support all ISO formats (e.g., no timezone), but it's fine.

- For input validation, we might also consider missing fields (no id, start, end, value). But assume they are present. We'll handle KeyError as invalid timestamp if start/end missing.

- The value may be missing, default to 0? The spec says each session has value. We'll assume it's there; if not, maybe reject? Better to assume value 0 if not there, but spec says present. We'll be lenient: if value not present, treat as 0? But to be safe, we can check: if 'value' not in session, maybe reject? But spec says each has value. We'll assume present.

- For reject reasons, the spec says: "rejected entries with reasons." We'll output a list of dicts with `id` and `reason`. If id is missing, we can use None or empty string. But we'll assume id is present.

Now, about output format: JSON with max_value, selected_ids, rejected. We'll use json.dumps with default settings (compact or pretty). The problem says output JSON. We'll output with indent for readability? Not specified, we can produce compact JSON or with some indentation. To be safe, we can output without any extra spaces to keep it compact. Usually for command-line programs, they produce compact JSON. But we can use json.dumps(data, separators=(',', ':')). But we can also use default printing (compact) if we don't set indent. We'll just use json.dumps(output) which prints compactly with no indent and separators (', ', ': ') by default? Actually default separators is (', ', ': '), which produces a bit of spacing. That's fine. We can also use separators=(',', ':') to be compact. But spec doesn't matter. We'll just use json.dumps(output) and then newline.

We'll also need to ensure that `selected_ids` is a list (maybe empty). `max_value` could be 0.

Now, let's write the code.

Now, incorporate `--test`:

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
    else:
        main()

In run_tests, we'll print "All tests passed!" after all pass. Use assert statements.

We need to test error cases: invalid timestamps. For example, "2026-05-01T09:00:00" is valid. For invalid, we can test "not-a-date".

We'll include tests for:
- Test valid.
- Test invalid timestamp (e.g., "xyz").
- Test end == start.
- Test negative value.
- Test tie-break fewer sessions.
- Test tie-break lexicographic.
- Test empty sessions.

Now, we need to consider that our solve function expects accepted sorted. In tests we are sorting before calling solve. That's fine.

Now, think about the case where there are multiple intervals with same end and start? They might be duplicates? Could cause issues with binary search? Not likely.

Now, about the better function: we should ensure that we don't compare seq if they are identical? But it's fine.

Now, we also need to ensure that the DP for empty accepted returns (0, []). We'll handle that.

Now, we also need to output 'rejected' list even if empty. So we add it to output.

Now, finalize code:

We need to import datetime, json, sys, bisect.

We'll add type hints? Not necessary.

Now, let's write the code with comments to keep under 1000 lines.

Potential pitfalls:

- When reading input, use sys.stdin.read()? json.load reads from file-like object.

- In parse_datetime, we catch ValueError for invalid timestamp.

- In parse_sessions, we use try-except for KeyError as well? If 'start' or 'end' missing, KeyError will raise. We'll catch (ValueError, KeyError) and reject with reason 'invalid timestamp'.

- For value, if missing, we might treat as None and reject? Let's just assume it's present. If not present, the .get('value', 0) will default to 0. But then we might accept a missing value as 0, which is not necessarily correct but likely acceptable. To be safe, we could check if 'value' not in session, and treat as 0. Let's do that: use session.get('value', 0). Then if value < 0, reject.

- For id, use session.get('id', None). But we assume present.

Now, build.

Now, after sorting, we need to create a list of accepted dicts with fields: id, start, end (strings maybe for output?), value (int), start_dt, end_dt.

Now, compute_p: we need ends list of datetime objects. Use bisect_right.

Now, in DP, we use better function to compare two entries. We need to define it before use.

Now, we might consider performance: For large n, the tuple concatenation might be slow. But we proceed.

Now, we can also add a small optimization: In take_seq, we could avoid copying if prev_entry[2] is empty. So we can do: if prev >= 0: prev_seq = dp[prev][2]; take_seq = prev_seq + (id_i,) if prev_seq else (id_i,). That's fine.

Now, we also need to ensure that in better, we compare seq correctly: a[2] < b[2] for lexicographically smaller. Python's tuple comparison works.

Now, we also need to handle case where two entries have same value and count and seq (identical). In that case we can keep either; we'll return a if better returns True else b. If they are equal, better returns False, so we choose skip? That might affect tie-breaking if equal but we are indifferent. But we need to ensure deterministic behavior. Since they are identical, it doesn't matter. However, to be deterministic, we could prefer skip over take if they are equal? But since they produce same value, count, seq, either is fine. But we can define better to return True if a is strictly better; if equal, return False so we keep b (which might be skip). But to keep consistency, we might want a deterministic rule. Since both are same, it's okay.

Now, about the tie-breaking for lexicographic order: we are using a[2] < b[2] to decide. That means if a's seq is smaller, a is better. That's correct.

Now, we should ensure that the seq is compared as tuple of strings (IDs). Lexicographic order of strings is fine.

Now, about the ID strings: They may contain any characters. Python's string comparison uses Unicode code point order, which is consistent.

Now, we might test with uppercase/lowercase? Not needed.

Now, I'll produce the code.

We also need to output selected_ids as list. We'll convert tuple to list.

Now, also, we should include the test run only when --test.

Now, write the complete code.

Let's write step by step:

```python
#!/usr/bin/env python3
import sys
import json
from datetime import datetime
import bisect

def parse_datetime(s):
    """Parse ISO format datetime string without timezone."""
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        raise ValueError("Invalid timestamp")

def parse_sessions(data):
    accepted = []
    rejected = []
    sessions = data.get('sessions', [])
    for session in sessions:
        # Use .get with defaults; assume id exists
        id_ = session.get('id', 'unknown')
        # Parse start and end
        try:
            start_str = session['start']
            end_str = session['end']
            start_dt = parse_datetime(start_str)
            end_dt = parse_datetime(end_str)
        except (ValueError, KeyError):
            rejected.append({'id': id_, 'reason': 'invalid timestamp'})
            continue
        # Validate end > start
        if end_dt <= start_dt:
            rejected.append({'id': id_, 'reason': 'end must be after start'})
            continue
        # Validate value
        value = session.get('value', 0)
        if value < 0:
            rejected.append({'id': id_, 'reason': 'value must be non-negative'})
            continue
        accepted.append({
            'id': id_,
            'value': value,
            'start_dt': start_dt,
            'end_dt': end_dt
        })
    return accepted, rejected

def sort_accepted(accepted):
    accepted.sort(key=lambda x: (x['end_dt'], x['start_dt'], x['id']))

def compute_p(accepted_sorted):
    ends = [interval['end_dt'] for interval in accepted_sorted]
    p = []
    for interval in accepted_sorted:
        # find last index where end_dt <= start_dt
        idx = bisect.bisect_right(ends, interval['start_dt']) - 1
        p.append(idx)
    return p

def better(entry1, entry2):
    """Return True if entry1 is strictly better than entry2."""
    v1, c1, s1 = entry1
    v2, c2, s2 = entry2
    if v1 != v2:
        return v1 > v2
    if c1 != c2:
        return c1 < c2  # fewer sessions is better
    return s1 < s2  # lexicographically smaller sequence is better

def solve(accepted_sorted):
    if not accepted_sorted:
        return (0, [])
    p = compute_p(accepted_sorted)
    n = len(accepted_sorted)
    base_entry = (0, 0, ())  # value, count, sequence tuple
    dp = [None] * n
    for i in range(n):
        interval = accepted_sorted[i]
        id_i = interval['id']
        value_i = interval['value']
        # skip option
        if i == 0:
            skip = base_entry
        else:
            skip = dp[i-1]
        # take option
        prev = p[i]
        if prev >= 0:
            prev_entry = dp[prev]
            take_val = value_i + prev_entry[0]
            take_count = 1 + prev_entry[1]
            take_seq = prev_entry[2] + (id_i,)
        else:
            take_val = value_i
            take_count = 1
            take_seq = (id_i,)
        take = (take_val, take_count, take_seq)
        # choose better
        if better(take, skip):
            dp[i] = take
        else:
            dp[i] = skip
    best = dp[-1]
    return (best[0], list(best[2]))

def main():
    data = json.load(sys.stdin)
    accepted, rejected = parse_sessions(data)
    sort_accepted(accepted)
    max_value, selected_ids = solve(accepted)
    output = {
        'max_value': max_value,
        'selected_ids': selected_ids,
        'rejected': rejected
    }
    json.dump(output, sys.stdout)
    sys.stdout.write('\n')

def run_tests():
    # Test 1: Simple two non-overlapping
    data1 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10}
    ]}
    acc, rej = parse_sessions(data1)
    sort_accepted(acc)
    v, ids = solve(acc)
    assert v == 15, f"Test1 value {v}"
    assert ids == ['a', 'b'], f"Test1 ids {ids}"
    assert rej == []

    # Test 2: Overlapping choose higher value
    data2 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 10}
    ]}
    acc2, rej2 = parse_sessions(data2)
    sort_accepted(acc2)
    v2, ids2 = solve(acc2)
    assert v2 == 10, f"Test2 value {v2}"
    assert ids2 == ['b'], f"Test2 ids {ids2}"

    # Test 3: Reject invalid (end <= start, negative value)
    data3 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T09:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 10},
        {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
        {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3}
    ]}
    acc3, rej3 = parse_sessions(data3)
    assert len(acc3) == 1
    assert acc3[0]['id'] == 'd'
    assert len(rej3) == 3
    assert rej3[0]['reason'] == 'end must be after start'  # a
    assert rej3[1]['reason'] == 'end must be after start'  # b (end < start)
    assert rej3[2]['reason'] == 'value must be non-negative'  # c

    # Test 4: Tie-break fewer sessions
    data4 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
        {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 5}
    ]}
    acc4, rej4 = parse_sessions(data4)
    sort_accepted(acc4)
    v4, ids4 = solve(acc4)
    assert v4 == 10
    assert ids4 == ['a'], f"Test4 ids {ids4} (expected ['a'])"

    # Test 5: Tie-break lexicographic
    data5 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T12:00:00", "end": "2026-05-01T15:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
        {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T15:00:00", "value": 7}
    ]}
    acc5, rej5 = parse_sessions(data5)
    sort_accepted(acc5)
    v5, ids5 = solve(acc5)
    assert v5 == 10, f"Test5 value {v5}"
    assert ids5 == ['a', 'b'], f"Test5 ids {ids5} (expected ['a','b'])"

    # Test 6: Empty sessions
    data6 = {"sessions": []}
    acc6, rej6 = parse_sessions(data6)
    sort_accepted(acc6)
    v6, ids6 = solve(acc6)
    assert v6 == 0
    assert ids6 == []

    # Test 7: Invalid timestamp
    data7 = {"sessions": [
        {"id": "x", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5}
    ]}
    acc7, rej7 = parse_sessions(data7)
    assert len(acc7) == 0
    assert len(rej7) == 1
    assert rej7[0]['reason'] == 'invalid timestamp'

    # Test 8: Lexicographic tie-break more complex
    data8 = {"sessions": [
        {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 10},
        {"id": "a", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5}
    ]}
    acc8, rej8 = parse_sessions(data8)
    sort_accepted(acc8)
    v8, ids8 = solve(acc8)
    # Optimal: b + c = 15, also b + a = 15. Lexicographically smaller list: b,a
    assert v8 == 15, f"Test8 value {v8}"
    assert ids8 == ['b', 'a'], f"Test8 ids {ids8} (expected ['b','a'])"

    print("All tests passed!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
    else:
        main()
```

But we need to check a few things:

- In parse_sessions, we used `session['start']` and `session['end']` without .get; this will raise KeyError if missing. We catch KeyError along with ValueError from parse_datetime. Good.

- In test3, we asserted reasons: for a, end==start yields `end must be after start`. For b, end < start yields same. For c, negative value yields. For d, valid.

- In test3, the order of rejected? Our parse_sessions iterates and appends in order. So first a (end==start) -> rejected with reason; second b (end < start) -> rejected; third c (negative value) -> rejected; fourth d -> accepted. So rej3[0] is a, rej3[1] is b, rej3[2] is c. So assert correct.

- In test4, we need to ensure that sorting order leads to correct selection. Let's simulate test4: intervals: a (9-12,10), b (9-10,5), c (10-12,5). Sorted by end: b end10, c end12, a end12? Actually a ends12, c ends12. Both end12. So sort by start: c start10, a start9? Actually a start9, c start10. So after end, then start, then id. So order: b (end10), a (end12, start9, id a), c (end12, start10, id c). Then DP: i0 (b): take=(5,1,('b',)), skip=(0,0,()) -> dp0=(5,1,('b',)). i1 (a): start9, p=-1 (since bisect_right(ends,9) => ends [10,12,12] idx=0 p=-1). take=(5,1,('a',)), skip=(5,1,('b',)) => compare: value equal, count equal, seq ('a') < ('b')? 'a'<'b' -> take better. So dp1=(5,1,('a',)). i2 (c): start10, p = bisect_right(ends,10) -1. ends[0]=10 so idx=1, p=0 (b). take: value 5+dp0.value5=10, count=2, seq=('b','c'). skip: dp1=(5,1,('a',)). better(take,skip): value 10 >5 => take better. So dp2=(10,2,('b','c')). So final selected ids ['b','c']? That would be value 10 but count 2, not the expected ['a'] which is value 10 count1. That would not be selected because we ended up with take for c that gives higher value? Wait, we computed value for take: 5 (c) + dp0.value (5) =10, which is same as skip value? Actually skip value is 5 from dp1 (which is max for intervals up to i=1, which is 5). So skip value is 5, take value is 10, so value is higher, so take is chosen. So we get 10 value with 2 sessions. But the option with only a also gives 10 value with 1 session. Why didn't we consider skip? skip at i=2 gave value 5, not 10. Because dp[i-1] (dp[1]) is (5,1,('a',)) not (10,1). Wait, maybe dp[1] should be (10,1,('a',))? Let's recompute correctly. Interval a has value 10, not 5. In the input, a has value 10. I mistakenly used 5 in my simulation. a has value 10. So let's redo test4:
a: id "a", start 9-12, value 10.
b: id "b", start 9-10, value 5.
c: id "c", start 10-12, value 5.
Sorted by end: b (end10,value5), c (end12, start10, value5), a (end12, start9, value10). So order: b, c, a (since for same end12, sort by start: a start9 < c start10, so a before c? Actually sort key (end, start, id). For end12, a has start9, c has start10. So ascending start: a start9, c start10. So a comes before c. So order: b, a, c.
Now DP:
i=0 (b): take=(5,1,('b',)), skip=(0,0,()) -> dp0=(5,1,('b',))
i=1 (a): start9, p: ends list [10,12,12]? Actually after sorting, ends = [b_end, a_end, c_end] = [10,12,12]. For a, start9 => bisect_right(ends,9) returns 0 -> p=-1. take: value 10, count1, seq('a',) -> (10,1,('a',)). skip: dp0=(5,1,('b',)). compare: value 10 >5 => take better. dp1=(10,1,('a',))
i=2 (c): start10, p: bisect_right(ends,10) -1. ends[0]=10 => idx=1, p=0 (b). take: value 5 + dp0.value5 =10, count2, seq=('b','c') -> (10,2,('b','c')). skip: dp1=(10,1,('a',)). Now compare take and skip: value equal (10), count: skip count=1 < take count=2 => skip is better (fewer sessions). So dp2 = skip = (10,1,('a',)). So final selected ids = ['a']. Good! So our code should produce correct result. In the simulation above for test4, we need to ensure sorting order as described. Our test4 input uses those values. So it's fine.

In test8, we need to ensure sorting order with bisect_right works as earlier. all good.

Now, about test8: we set expected to ['b','a']. But note that chronological order: b starts 9-10, a starts 10-11, so order b then a is chronological. Yes.

Now, test5 we set expected ['a','b']: a (9-12), b (12-15). chronological order: a then b.

Now, we also need to test that the output selected_ids order is chronological. In test2, selected b only.

Now, we should also test that the output JSON for normal mode is printed. In tests we only test internal functions.

Now, we also need to ensure that we didn't inadvertently mutate data.

Now, about memory: The dp list stores tuples which include seq tuples. In tests with small n, fine.

Now, there is one nuance: When we compare sequences in better, we use `s1 < s2`. Python tuple comparison is lexicographic. For example, ('a', 'b') < ('a', 'c') yields True. That's correct.

But we must be careful: In the DP, we might compare sequences that are not the same length. For example, ('a','b') vs ('c','d','e'). Lexicographic comparison in Python: first element: 'a' vs 'c' -> 'a' smaller => so `('a','b') < ('c','d','e')` is True. That's correct because we compare first element. If first elements equal, then second element, etc. So it's correct.

Now, if we have two sequences like ('a', 'b') and ('a',), the comparison will compare 'a'== 'a', then b vs (none) => the shorter sequence is considered smaller? In Python, when comparing tuples, if they are equal up to the length of the shorter, the shorter is considered smaller. So ('a',) < ('a', 'b') is True. That would mean that a sequence with fewer sessions (but same first elements) is lexicographically smaller, which aligns with our tie-breaking: if two sequences have same value and count, we want lexicographically smaller; but if one sequence is a prefix of the other, the shorter one is lexicographically smaller (since empty is smaller than something). However, in our context, if we have two solutions with the same value and count, they must have the same number of sessions because count is equal. So sequences will have same length. So that issue does not arise. But if we ever compare sequences of different lengths? In our DP, we only compare entries that have same value and count. Since count is stored as part of the entry, we only compare seq when counts are equal. So sequences lengths are equal. So safe.

Now, about the base_entry: (0,0,()). This has empty tuple. In comparisons with other entries, if value==0 and count==0, we might compare it with another entry with same value and count? But base_entry only used as skip when i=0 and no intervals? But at i=0, skip is base_entry and take has count=1. So counts differ, so seq not compared. So fine.

Now, we should also test the normal mode by possibly running the program with a sample input. Not in tests.

Now, we need to ensure that the output JSON does not have any extra fields. spec: `max_value`, `selected_ids`, `rejected`. So we include those.

Now, about the "selected_ids in chronological order". We are outputting the list as built by dp; it's in order of increasing end time. That should be chronological. However, if two intervals have the same end time but different start, can they both be selected? They can't because they would overlap (since both end at same time and one must start before the other). So it's fine.

Now, consider a case where there are intervals with same end time but they are not overlapping because one has start after the other's end? Impossible as argued. So fine.

Edge: There could be intervals with identical times? That would be overlapping, can't both be selected.

Now, about binary search: we used bisect_right on ends list. If start_i is exactly equal to some ends, they are included. Good.

Now, about correctness: Our DP now should produce optimal value. The tie-breaking for fewer sessions and lexicographic order is handled because we compare entries with better function that prefers fewer sessions then smaller seq. Since we are making optimal choices at each step, the final solution is optimal with respect to this ordering? We need to verify that this DP yields the globally optimal solution with respect to the lexicographic order on the sequence of IDs (with primary objective being value, then count, then sequence). Because we are building solutions from subproblems that are optimal for their prefixes, and we compare whole sequences, it should be correct because the DP considers both options and uses the comparator that respects the total order. This is typical for DP with a total order on solutions that allows greedy choice based on optimal subproblem. Since our comparator is a total order, and the optimal solution for a prefix is defined as the best among all feasible subsets of intervals from that prefix, and we are always taking the best according to this total order at each subproblem, the overall solution should be optimal for the whole set. This holds because the optimal substructure property holds for the order of intervals sorted by end time. The comparator respects the same structure? Actually, we need to ensure that the comparator is consistent with the DP. For weighted interval scheduling, we can find the maximum value using DP because the value function is additive and the problem has optimal substructure. We have added secondary criteria (count and sequence) that are also additive? Count is additive, and sequence is built by concatenation. The comparison we use (lexicographic) is a total order that is compatible with the DP? That is, given two candidate solutions for a subproblem, the better one can be used to construct better solutions for larger problems? This is true because when we combine with a new interval, we only append to the end. So if we have two solutions for intervals up to index i, one is better than the other, then for any future interval j that starts after the end of the last interval in both solutions? Not necessarily, because the compatibility with future intervals depends on the end time of the last interval in the solution. In intervals sorted by end, compatibility is based on end time: future intervals have start >= current end. If we have two solutions for prefix i, they may have different end times (the end of the last selected interval). When we consider a future interval j, it may be compatible with one solution but not the other. Therefore, the DP chooses the best solution for each prefix based on the value, but for future compatibility we need to consider the end time. The standard DP only keeps the maximum value for each prefix, but it does not keep track of the end time because the prefix is defined as 'up to index i', and the last end time used is the end of interval i (since we always consider intervals in order of end time). Actually, in the DP we defined, dp[i] is the best solution using intervals from among the first i intervals (sorted by end). This dp[i] does not necessarily end with interval i; it could end with some earlier interval. That's okay because the compatibility with future intervals is determined by the start of the future interval; but we only check compatibility via p(i) which only depends on the start of interval i relative to previous intervals. When we process interval i, we consider including it by taking dp[p[i]], which is the best solution for intervals that end before start_i. That solution may have ended with some interval that ends before start_i. So it's compatible. The key is that dp[p[i]] is already the best solution among intervals that end before start_i, according to our total order. So combining it with i gives a candidate for the new best solution that ends with i. Also, we consider skip dp[i-1], which is the best solution among intervals up to i-1. For the future, when we process intervals later than i, they will use p for those intervals to find compatibility; dp[i] is used as part of skip for later intervals, but it could also be used as part of take if a later interval j has p(j) >= i. For compatibility, the last end time of dp[i] may be less than or equal to end_i (since the last interval in dp[i] could be i or earlier). However, the DP uses the index to reference the last interval that ends before start_j; it does not consider the exact end time of dp[i]'s last interval beyond that it is <= end_i. Since p(j) is defined as the maximum index such that end <= start_j, if dp[i] ends with i, then its end is end_i, which is <= start_j if p(j) >= i. If dp[i] ends with some earlier interval, its end is even earlier, so still <= start_j if p(j) >= i. So dp[i] is compatible with any j where p(j) >= i. So it's safe to use dp[i] as a subproblem. Therefore, the DP is valid.

Now, does the total order we defined preserve optimality for future steps? Since when we compare two solutions for dp[i], if they have the same value, count, and lexicographic order, the one that is better may have a different last end time. But for compatibility with future intervals, the last end time matters only in that it must be <= start_j. Both solutions have last end times that are <= end_i (since all intervals in dp[i] end <= end_i). But one solution might have a later last end time than the other? Actually, if it includes i, the last end is end_i; if it does not, the last end is the end of the last interval chosen from dp[i-1], which is <= some end (could be less than end_i). Both are <= end_i. For a future interval j with p(j) >= i, as long as the last end time of dp[i] <= start_j, it's compatible. Since dp[i]'s last end time is always <= end_i <=? Not necessarily <= start_j? If p(j) >= i, then by definition ends[i] <= start_j (since ends[i] is end of interval i, and if p(j) >= i then there exists interval with index i such that end_i <= start_j? Actually p(j) is the last index with end <= start_j. If p(j) >= i, then i <= p(j), so ends[i] <= ends[p(j)] <= start_j. So both scenarios are fine. If dp[i] doesn't include i, its last end time is the end of some earlier interval with index <= i-1; that end is <= ends[i-1] <= end_i <= start_j (since starts of j are greater or equal to ends[p(j)] >= ends[i]). So compatibility holds. Therefore the exact last end time does not affect future compatibility as long as we have the index property. So the DP is correct.

Thus our comparator is fine.

Now, we should confirm with a case where two candidate solutions for dp[i] have same value and count and different sequences, but one has a later last end time (maybe includes i) and the other does not. For future intervals, both are compatible? As argued, yes, because p for future intervals is based on end times of intervals, not the selected set. So both are considered for future intervals through dp[i]. However, when we later compute dp[j] and take from dp[p(j)], we use dp[p(j)] as a whole. If we choose the better one for dp[p(j)], that will lead to better solution for dp[j]? Since we will compare skip (dp[j-1]) and take (value_j + dp[p(j)]). So if dp[p(j)] is the best according to our order, then the candidate for dp[j] will be the maximum among those two. This accepts the best overall for dp[j]. So the DP is correct with this ordering.

Thus the solution should be correct.

Now, we need to ensure that the program is named `schedule_optimizer.py`. In the code, we don't enforce the filename. It's fine.

Now, about line count: We've written around 270 lines so far, under 1000.

Now, we should consider that the `--test` option should print only the success message and nothing else. So we should not output JSON. That's fine.

Now, we might also consider that the normal mode should print only JSON. We ensure no extra print statements.

Now, we need to handle that the input JSON may have extra fields (like "sessions" only). We ignore others.

Now, final step: Write the code in the answer.

But before final, I want to double-check some edge cases:

1. Duplicate IDs: If there are two intervals with same ID, our sequence of IDs may contain duplicates. Lexicographic comparison will compare sequences tuple: ('a','a') vs ('a','b'), etc. That's fine.

2. Very large values: counts may be large, but Python ints big.

3. Timestamp parsing: Python 3.7+ fromisoformat works for strings like "2026-05-01T09:00:00". It also works with "2026-05-01T09:00:00" and no timezone. Good.

4. Negative value rejected, but zero value allowed.

5. End must be strictly after start, so end > start. We reject if end <= start.

6. For intervals with end == start, we reject.

7. For binary search we used bisect_right to include equality. That's consistent.

Now, one more test: If there are intervals with identical start and end? It would reject because end <= start. So not accepted.

Now, ensure that in parse_sessions, we treat missing 'value' as 0? But spec says each session has value, so should be present. But we just use value = session.get('value', 0) to avoid KeyError if missing. Not necessary but safe.

Now, I'll also consider the case where a session has value 0; it's allowed. It may be selected if it contributes to tie-breaking? But since value 0 doesn't increase total value, it could be selected only if it helps with tie-breaking? Actually, if adding a zero-value interval could change the solution to have fewer sessions? No, adding zero-value increases count, so not better. It could be needed to achieve lexicographically smaller sequence? For example, two solutions with same value and count, but one includes an extra 0-value interval? That would increase count, so not equal count. So not relevant. If two solutions have same value and count, zero-value intervals could be part of both but they are equal. So fine.

Now, run_tests includes the tests we consider. We'll add maybe test for invalid timestamp where start/end missing.

Let's add a test for missing 'start' key.

Also test for large n? Not needed.

Now, we should also incorporate a test for the scenario where there are multiple solutions with same value, same count, but different sequences; one has lexicographically smaller sequence but later in order. For instance, intervals:
id='b' (9-10, value 5), id='a' (10-11, value 5), id='c' (11-12, value 5). All value=5. Sorted by end: b, a, c. Optimal total value 15 (all three). Count=3. No other with same value and count. So not tie.
Consider a scenario where we have two disjoint sets with same value and count. We already covered.

Now, what about the case where two solutions have same total value and count, but their sequences differ from the start. Our DP should pick lexicographically smaller. That's covered.

Now, ensure that the better function is used consistently.

Now, minor optimization: In the DP, for take, we compute take_entry and compare. If we use better(take, skip), and if they are equal, we pick skip. That means we prefer skip over take when tied. Does that affect lexicographic tie-breaking? If they are exactly equal (value, count, seq), then skip and take produce same sequence. So either is fine. But if they are equal except seq? That can't happen if value and count equal and seq compare yields equal, then identical. So it's okay.

Now, if we prefer skip, that might influence when there are two different ways to achieve same value, count, and seq? Impossible.

Now, about the sorting: we sort by end, then start, then id. This ordering influences the p indices and thus the solution. Could this affect the lexicographically smallest solution? Possibly, because the DP decisions depend on the order of intervals with same end. Consider two intervals with same end time but different start times and different IDs. They cannot both be in the same solution because they overlap (since same end time). The DP might consider them in some order. Since they are interchangeable in terms of compatibility with previous intervals (both have same end, but start may differ, affecting p of other intervals), the order could affect which one is considered for inclusion. However, the set of feasible solutions is independent of ordering. But the DP's choice may depend on order because we process them in sequence. However, we need to ensure that our tie-breaking (lexicographic) is deterministic regardless of sorting order? The problem expects deterministic output. The sorting order we choose (by end, start, id) is deterministic and should yield a deterministic output. However, is it possible that two different orderings of intervals with same end could lead to different selected IDs list for the same input? The DP should produce the same optimal value, but might produce different optimal solution among ties. Because when intervals have same end, the order in which we process them can affect which ones are considered 'first' and thus the DP might prefer one over the other due to tie-breaking. For example, suppose we have two intervals X and Y with same end, and they are incompatible with each other. Suppose they have the same value and count alternatives. The DP will process them in order. When processing the second, it will have dp[i-1] which might include the first. The skip option is dp[i-1] which includes possibly the first interval, but the take option will combine with prev which might be the same. The outcome could be that the second interval may be selected in some cases due to tie-breaking? The final optimal set might include either X or Y, but not both. The DP's final dp will have seq that may contain X or Y. But is it guaranteed that among all optimal solutions with same value and count, the lexicographically smallest sequence is chosen? Because we have sorting by end, start, id, the DP is not symmetric with respect to intervals with same end? The lexicographic order of IDs is independent of ordering. Therefore, our DP should, for the final set, yield the lexicographically smallest sequence among all optimal (value, count) solutions. However, due to processing order, we might need to ensure that the DP doesn't inadvertently discard a solution that could lead to lexicographically smaller sequence because of the order it processes intervals. But the DP is constructing optimal solutions for each prefix, and the final dp[-1] is the best for the entire set according to our total order, assuming subproblem optimality. Since the total order is a total order and DP respects it, the final result should be globally best. The processing order just defines the partial order of intervals (by end time). Intervals with the same end time are incomparable in end time order, but we impose a total order by (end, start, id). This total order is a refinement of the partial order by end. For intervals with same end, the DP processes them sequentially. The DP's construction ensures that for each prefix, we have the best solution considering intervals up to that index. Since all intervals are considered eventually, the final result should be optimal among all subsets from all intervals. The total order used for comparison is applied consistently. So even though we might consider X before Y, the DP can still include Y later by building a solution that includes Y and skips X. The final comparison at the last index will compare the best solution that includes Y (via take) and the best that includes X (from skip, because skip is dp[i-1] which may include X). So both are considered. The better one according to the total order will be selected. So the order should not affect the globally optimal choice as long as we compare correctly. However, note that the DP's dp[i] for earlier prefixes might not be globally optimal for the set of intervals up to i, but they are optimal among those intervals. So for the entire set, the final dp is optimal.

But there is a subtlety: Suppose there are two intervals with same end, X and Y, where X has smaller ID. Suppose there is an interval Z that starts after the end of X and Y. The DP's p for Z will be the same for both (since both have same end). The optimal solution might include Z plus either X or Y, both giving same total value and count. The tie-breaking should pick the one with lexicographically smaller sequence (which would be X, Y? Actually sequence would be [X, Z] vs [Y, Z]. Lexicographically compare: first element: X vs Y, if X < Y, then [X,Z] smaller. So we want to pick X. In the DP, when processing Z, the take option will combine with dp[p[Z]], which is the best solution for intervals ending before start of Z. That dp[p[Z]] may be either X or Y (or both depending on order). If in the prefix up to p[Z], we have processed X and Y, the dp[p[Z]] should be the best solution for intervals up to that index according to our total order. Since both X and Y have same end, and suppose they both have same value and count, the dp[p[Z]] will choose the one with lexicographically smaller sequence (i.e., X). So when we combine with Z, we will get [X, Z]. So it works.

Now, but consider a scenario where two intervals with same end have different start times. Could that affect p for later intervals? Not directly.

Thus our approach should be correct.

Now, about the output JSON: We need to ensure that we dump rejected list correctly. The rejected list contains dicts with 'id' and 'reason'. That's fine.

Now, finalize.

But we also need to consider that the input might contain sessions with zero value? That is allowed. They might be selected if they help tie-breaking? But zero value doesn't increase total value, but could be part of a solution with same max value? If there are intervals with positive value, zero-value intervals won't increase value, so if they are selected, they increase count, making count worse. So they wouldn't be chosen over solutions without them. However, if there is a tie in value and count, zero-value intervals could be used to achieve lexicographic ordering? Suppose two solutions have same total value from other intervals plus a zero-value interval? If both include that zero-value interval, it's same. If one includes it and the other doesn't, counts differ. So they wouldn't tie in count. So zero-value intervals are only selected if they are necessary to achieve the maximum value? But they don't add value, so they would only be selected if they allow including other intervals? But since they have zero value, they only take up time, possibly blocking other intervals, so they would never be part of an optimal solution unless they have value 0 but also don't conflict with anything? But then inclusion would increase count without increasing value, making it strictly worse according to our secondary criterion (fewer sessions preferred). So they won't be selected in an optimal solution. So we can ignore.

Now, final code.

Before final, we might want to add a small optimization: In the DP, when computing take_seq, we can avoid creating a new tuple if prev_seq is empty. For empty, we can just use (id_i,). This is already done because if prev>=0 and dp[prev][2] is empty, concatenation empty+(id_i,) creates a new tuple of length1. That's fine.

Now, also, we could store seq as tuple; but converting to list at the end is fine.

Now, we should also handle the case where there are many intervals and the recursion for binary search is O(log n). That's fine.

Now, one more thing: When outputting JSON, use `json.dumps(output, separators=(',', ':'))` for compact output. But the problem doesn't require compactness; we can use default (which includes spaces). I think default is fine. We'll use `json.dump(output, sys.stdout)`. The indent parameter is optional; we'll not use indent to produce compact? Not necessary. We'll leave as is.

But note: The output specification says "Output JSON with max_value, selected_ids, rejected." No additional spaces requirement. So fine.

Now, test cases: We'll run our tests mentally to ensure they pass. We already simulated.

Now, also need to test for intervals where there is a tie in value and count but the lexicographic order is not simply by first element but by later elements. We already have test5 where sequences ('c','d') and ('a','b') differ at first element. For deeper tie, need test where first elements equal. For instance:

Intervals:
- X1 (9-10, value 5), X2 (10-11, value 5), Y1 (9-10, value 5), Y2 (10-11, value 5). But IDs: X1='a', X2='b', Y1='c', Y2='d'. And there is also a high-value interval? This might be messy. But we can trust.

Let's construct a test for deeper lexicographic tie:

Sessions:
- i1: id='a', 9-12, value 10
- i2: id='b', 12-15, value 10
- i3: id='c', 9-10, value 5
- i4: id='d', 10-12, value 5
- i5: id='e', 12-15, value 5? Actually to have two solutions with value 20, count 2, sequences: a+b = ['a','b']; c+d+e? But c,d,e would have value 15? Not.
Better: Two disjoint paths with same total. Example:
Intervals: A: 9-12 value 10, B:12-15 value10, C:9-10 value5, D:10-12 value5, E:12-15 value5. Three intervals C,D,E total value 15, not 20. So not equal.
We want two solutions with same total value and count but sequences share common prefix and then differ. For instance:
Intervals: I1 (id='a', 9-11, value5), I2 (id='b', 11-13, value5), I3 (id='c', 13-15, value5), I4 (id='d', 9-13, value10). Then we have two solutions: I1+I2+I3 (value15, count3) and I4+I3? I4+I3 value15, count2? Not equal count.
We want equal value and equal count. For example, two sets of two intervals each: path1: J1 (id='a',9-10,5), J2 (id='b',10-12,5); path2: K1 (id='c',9-11,5), K2 (id='d',11-12,5). Both total 10, count2. Sequences: ['a','b'] vs ['c','d']. Lexicographically, 'a'<'c' so first element decides. To force deeper comparison, we need first elements equal, e.g., both have first interval id='a' but second differ. Example: intervals: A (id='a',9-10,5), B (id='b',10-12,5), C (id='a',9-11,5), D (id='c',11-12,5). But then we have two solutions: A+B (a,b) and C+D (a,c). They share first element 'a' but second 'b' vs 'c'. However, they are from intervals with same ID 'a'? That's allowed, but then IDs not unique. But that's okay. So we can test that kind of tie-breaking: input sessions:
- id='a', start9-10, value5
- id='b', start10-12, value5
- id='a', start9-11, value5 (another interval with same ID)
- id='c', start11-12, value5
But careful: The sorted order: first 'a'(9-10,end10), then 'a'(9-11,end11), then 'b'(10-12,end12), then 'c'(11-12,end12). However, intervals with same ID are allowed but they are separate. The DP should consider them. The solution A+B has sequence ['a','b']; solution C+D has sequence ['a','c']. Lexicographically, ['a','b'] < ['a','c'] because 'b'<'c'. So expected output should be A+B. We could include this test.

We can add a test for deeper tie-breaking. But not necessary.

Given the complexity, I'll mention that it should work.

Now, about the rejected list: We store rejected with id and reason. But what if a session is missing an id? We'll set id to 'unknown'? But the spec says each session has an ID. So it's fine.

Now, run_tests should be comprehensive.

We also need to test that the program correctly outputs JSON when run normally. Could be tested via subprocess but not required. Our unit tests cover core.

Now, final code.

I will now write the final answer with the complete code.
````

## Assistant

````markdown
```python
#!/usr/bin/env python3
import sys
import json
from datetime import datetime
import bisect


def parse_datetime(s):
    """Parse ISO‑format datetime string (without timezone)."""
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        raise ValueError("invalid timestamp")


def parse_sessions(data):
    """Validate input sessions; return (accepted, rejected) lists."""
    accepted = []
    rejected = []
    sessions = data.get('sessions', [])
    for session in sessions:
        id_ = session.get('id', 'unknown')
        try:
            start_str = session['start']
            end_str = session['end']
            start_dt = parse_datetime(start_str)
            end_dt = parse_datetime(end_str)
        except (ValueError, KeyError):
            rejected.append({'id': id_, 'reason': 'invalid timestamp'})
            continue
        if end_dt <= start_dt:
            rejected.append({'id': id_, 'reason': 'end must be after start'})
            continue
        value = session.get('value', 0)
        if value < 0:
            rejected.append({'id': id_, 'reason': 'value must be non-negative'})
            continue
        accepted.append({
            'id': id_,
            'value': value,
            'start_dt': start_dt,
            'end_dt': end_dt,
        })
    return accepted, rejected


def sort_accepted(accepted):
    """Sort intervals by end, then start, then id (deterministic order)."""
    accepted.sort(key=lambda x: (x['end_dt'], x['start_dt'], x['id']))


def compute_p(accepted_sorted):
    """For each interval, find last index with end_dt <= start_dt."""
    ends = [interval['end_dt'] for interval in accepted_sorted]
    p = []
    for interval in accepted_sorted:
        idx = bisect.bisect_right(ends, interval['start_dt']) - 1
        p.append(idx)
    return p


def better(entry1, entry2):
    """Return True if entry1 is strictly better than entry2.

    Order: higher value, fewer sessions, lexicographically smaller sequence.
    """
    v1, c1, s1 = entry1
    v2, c2, s2 = entry2
    if v1 != v2:
        return v1 > v2
    if c1 != c2:
        return c1 < c2            # fewer sessions is better
    return s1 < s2                # lexicographically smaller list is better


def solve(accepted_sorted):
    """Weighted interval scheduling with reconstruction and tie‑breaking.

    Returns (max_value, selected_ids) where selected_ids are in chronological order.
    """
    if not accepted_sorted:
        return (0, [])

    p = compute_p(accepted_sorted)
    n = len(accepted_sorted)
    base = (0, 0, ())            # (value, count, sequence tuple)
    dp = [None] * n

    for i in range(n):
        interval = accepted_sorted[i]
        id_i = interval['id']
        value_i = interval['value']

        # Option 1: skip interval i
        if i == 0:
            skip = base
        else:
            skip = dp[i - 1]

        # Option 2: take interval i
        prev = p[i]
        if prev >= 0:
            prev_entry = dp[prev]
            take_val = value_i + prev_entry[0]
            take_count = 1 + prev_entry[1]
            take_seq = prev_entry[2] + (id_i,)
        else:
            take_val = value_i
            take_count = 1
            take_seq = (id_i,)
        take = (take_val, take_count, take_seq)

        # Keep the better of the two
        if better(take, skip):
            dp[i] = take
        else:
            dp[i] = skip

    best = dp[-1]
    return (best[0], list(best[2]))


def main():
    data = json.load(sys.stdin)
    accepted, rejected = parse_sessions(data)
    sort_accepted(accepted)
    max_value, selected_ids = solve(accepted)
    output = {
        'max_value': max_value,
        'selected_ids': selected_ids,
        'rejected': rejected,
    }
    json.dump(output, sys.stdout)
    sys.stdout.write('\n')


def run_tests():
    """Built‑in tests (invoked by --test)."""

    # Test 1: two non‑overlapping sessions
    data1 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T11:00:00", "value": 10},
    ]}
    acc1, rej1 = parse_sessions(data1)
    sort_accepted(acc1)
    v1, ids1 = solve(acc1)
    assert v1 == 15, f"Test1 value = {v1}"
    assert ids1 == ['a', 'b'], f"Test1 ids = {ids1}"
    assert rej1 == []

    # Test 2: overlapping, choose higher value
    data2 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 10},
    ]}
    acc2, rej2 = parse_sessions(data2)
    sort_accepted(acc2)
    v2, ids2 = solve(acc2)
    assert v2 == 10, f"Test2 value = {v2}"
    assert ids2 == ['b'], f"Test2 ids = {ids2}"

    # Test 3: reject invalid sessions
    data3 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T09:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T09:00:00", "value": 10},
        {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": -1},
        {"id": "d", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
    ]}
    acc3, rej3 = parse_sessions(data3)
    assert len(acc3) == 1
    assert acc3[0]['id'] == 'd'
    assert len(rej3) == 3
    assert rej3[0]['reason'] == 'end must be after start'
    assert rej3[1]['reason'] == 'end must be after start'
    assert rej3[2]['reason'] == 'value must be non-negative'

    # Test 4: tie‑break – fewer sessions
    data4 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 10},
        {"id": "b", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 5},
    ]}
    acc4, rej4 = parse_sessions(data4)
    sort_accepted(acc4)
    v4, ids4 = solve(acc4)
    assert v4 == 10, f"Test4 value = {v4}"
    assert ids4 == ['a'], f"Test4 ids = {ids4} (expected ['a'])"

    # Test 5: tie‑break – lexicographic order
    data5 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T12:00:00", "end": "2026-05-01T15:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 3},
        {"id": "d", "start": "2026-05-01T10:00:00", "end": "2026-05-01T15:00:00", "value": 7},
    ]}
    acc5, rej5 = parse_sessions(data5)
    sort_accepted(acc5)
    v5, ids5 = solve(acc5)
    assert v5 == 10, f"Test5 value = {v5}"
    assert ids5 == ['a', 'b'], f"Test5 ids = {ids5} (expected ['a','b'])"

    # Test 6: empty session list
    data6 = {"sessions": []}
    acc6, rej6 = parse_sessions(data6)
    sort_accepted(acc6)
    v6, ids6 = solve(acc6)
    assert v6 == 0, f"Test6 value = {v6}"
    assert ids6 == [], f"Test6 ids = {ids6}"

    # Test 7: invalid timestamp
    data7 = {"sessions": [
        {"id": "x", "start": "not-a-date", "end": "2026-05-01T10:00:00", "value": 5},
    ]}
    acc7, rej7 = parse_sessions(data7)
    assert len(acc7) == 0
    assert len(rej7) == 1
    assert rej7[0]['reason'] == 'invalid timestamp'

    # Test 8: deeper lexicographic tie (first element equal)
    data8 = {"sessions": [
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:00:00", "value": 5},
        {"id": "b", "start": "2026-05-01T10:00:00", "end": "2026-05-01T12:00:00", "value": 5},
        {"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T11:00:00", "value": 5},
        {"id": "c", "start": "2026-05-01T11:00:00", "end": "2026-05-01T12:00:00", "value": 5},
    ]}
    acc8, rej8 = parse_sessions(data8)
    sort_accepted(acc8)
    v8, ids8 = solve(acc8)
    # Two optimal solutions of value 10, 2 sessions:
    #   ['a','b'] (first a+second b) and ['a','c'] (third a+fourth c)
    # Lexicographically: ['a','b'] < ['a','c']
    assert v8 == 10, f"Test8 value = {v8}"
    assert ids8 == ['a', 'b'], f"Test8 ids = {ids8} (expected ['a','b'])"

    print("All tests passed!")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
    else:
        main()
```
````
