# Generation Transcript

- Case: `en_code_alg_001`
- Language group: `en`
- Workload: `coding`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 628.481712
- Finish reason: `length`
- Usage: `{"prompt_tokens": 373, "total_tokens": 61813, "completion_tokens": 61440, "prompt_tokens_details": null}`
- Prompt tokens: 373
- Completion tokens: 61440
- Total tokens: 61813

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
We need to write a single-file Python 3 command-line program named `schedule_optimizer.py`. No third-party packages. Under 1000 lines.

Problem: Weighted interval scheduling with reconstruction. Input JSON from stdin. Output JSON. Also handle --test for built-in tests.

We need to parse ISO-like timestamps without time zones. Use datetime.datetime.fromisoformat or maybe datetime.strptime with format. Since Python 3.7, datetime.fromisoformat exists but it requires separators "T" and it's strict. We can use datetime.isoformat? Actually we need to parse, not format. We'll use fromisoformat but note that in Python 3.11+ it's more flexible. But for compatibility, we can use strptime with format "%Y-%m-%dT%H:%M:%S". We'll assume seconds are always provided? The example shows "2026-05-01T09:00:00". Could be also "2026-05-01T09:00" but we can handle both by trying fromisoformat first? Simpler: use datetime.strptime with "%Y-%m-%dT%H:%M:%S" and if fails, maybe try "%Y-%m-%dT%H:%M". But to keep it simple, we'll assume format with seconds. The requirement says "ISO-like timestamps", but we can handle any that Python's fromisoformat can parse? Actually we must parse using Python standard library. I'll use datetime.fromisoformat(s). In Python <3.11, it doesn't handle trailing Z or timezone offsets, but we assume no timezones. So fromisoformat works for basic ISO. But if the string is like "2026-05-01T09:00:00", fromisoformat works in Python 3.7+. I'll use that. If it fails, we can reject the session with reason "invalid start timestamp" etc.

Rejection: end not after start, value negative.

Output JSON: {"max_value": ..., "selected_ids": [...], "rejected": [{"id": ..., "reason": ...}]}

If multiple optimal solutions: choose one with fewer sessions; if still tied, lexicographically smaller list of IDs.

DP approach: O(n log n) using binary search for last non-overlapping session. Sort sessions by end time. For each session i (0-indexed after sorting), we compute dp[i] = max(value_i + dp[prev[i]], dp[i-1]) where prev[i] is the latest session j that ends before session i starts. Then reconstruct.

We need to schedule non-overlapping subset maximizing total value. The DP picks sessions for optimal total value. If tie, we want fewer sessions, and if still tie, lexicographically smaller list of IDs. Lexicographic comparison of lists of IDs (strings). For tie-breaking, we need to incorporate in DP. Typical weighted interval scheduling DP chooses max over including or excluding. For tie (same total value), we need to prioritize fewer sessions and then lexicographically smaller IDs. That means for equal total value, we prefer the option with smaller number of sessions. If still equal, we prefer the list of IDs that is lexicographically smaller when sorted chronologically (by start time or by end time? Not exactly: selected_ids should be in chronological order. So during reconstruction, we need to consider that the order is deterministic based on start times? But IDs are arbitrary. For lexicographic comparison, we need to compare the lists of IDs in chronological order. The DP decision should favor smaller lists and smaller lexicographic IDs.

One approach: modify DP to store for each state the best solution in terms of (total_value, -count, ids_lexicographic?) Actually we want to minimize count, then lexicographically smaller IDs. Since we are maximizing total value first, then for equal value we minimize count, then minimize lexicographic order of IDs (i.e., compare lists of IDs element-wise). Because we want lexicographically smaller list of IDs. Note that if two solutions have same total value and same count, the one with lexicographically smaller list of IDs is chosen. Since IDs are strings, we can compare them as lists.

We must be careful: When we reconstruct, the selected IDs will be in chronological order (by start time? The output says "in chronological order". Typically it means by start time, but could be by end time. I think it's by start time. Since we sort sessions by end time for DP, but the chronological order of selected sessions should be by start time (or by timeline). We'll sort selected sessions by start time before outputting IDs. However, for lexicographic comparison of ID lists, we need a consistent order. It's logical to order the selected sessions by start time (or by end time) when comparing. I'll decide to order by start time (ascending). If there is a tie start time? Then maybe by end time or by ID? But we need to be deterministic. We'll sort by start time, then end time, then ID? But output is "in chronological order", so we need to decide what that means. Usually it means by start time. So I'll sort selected sessions by start time. For tie-breaking during DP, we need to compare potential solutions' final ID lists (after sorting by start time). However, the DP reconstruction may produce a list of IDs in the order they are selected (which is not chronological if we just follow DP). So we need to store for each dp state the best solution (or store the path and then reconstruct and then compare). It might be simpler to do DP with standard total value, then for ties (equal dp value), we choose the one with fewer sessions, and then with lexicographically smaller list. But we can incorporate both into the DP by storing a tuple (total_value, -num_sessions, ids) for comparing? For each i we need to compare including vs excluding. But including session i gives value_i + dp[prev[i]], and excluding gives dp[i-1]. So we can compare these two options on three criteria: 1) total value, 2) number of sessions (negative of count because higher is better? Actually we want fewer sessions, so for same value we want larger negative count? Better to have a comparator that returns the better of two solutions. We'll define a function better(a, b) that returns True if a is better than b. a and b are tuples (value, count, ids). Where ids is a list of IDs sorted chronologically (by start time) for that solution. Then we can decide.

But storing full ids for each DP state could be memory heavy (O(n^2) if we store lists). However n might be large but we can instead store back pointers and only reconstruct final answer. To break ties, we need to compare the full list lexicographically. But we could incorporate tie-breaking by constructing the chosen set at the end using DP that includes count? Another technique: modify DP to store not just maximum value but also minimum count for that value, and for ties on value and count, store the lexicographically smallest list. However storing the list for each state can lead to O(n^2) memory and time if we copy lists. We can store only the decision (include or exclude) and for ties we make decisions based on comparing the resulting lists without copying? But that's complex.

Alternative: Instead of storing full lists, we can store for each state the best "signature" in a way that can be compared without full lists, like a hash? But lexicographic order cannot be encoded simply. Since n could be up to 10^4 or 10^5, storing lists for each state may be okay if we use tuples and sharing? But we cannot copy lists for each state. However we can store the decision pointer and then at the end we reconstruct the selected list and then we need to compare multiple optimal solutions? But DP only yields one optimal value. If there are multiple optimal solutions with same value, the DP as implemented may arbitrarily pick one based on implementation details (e.g., if value equal, it may prefer include or exclude). To ensure we get the one with fewer sessions and lexicographically smaller list, we need to encode the tie-breaking in the comparison of options.

One common way for weighted interval scheduling with tie-breaking: For each i, we compute dp_val[i], and we also compute dp_count[i] (minimum number of sessions to achieve dp_val[i]) or maybe we want to minimize count after maximizing value. So we can have a tuple (dp_val[i], -dp_count[i]) and maximize lexicographically. But then still the ID list ordering may break ties on count. So we need one more level: (dp_val[i], -dp_count[i], some representation of the ID list). Since lexicographic ordering of ID lists is not easily compressed, we could fallback to comparing lists only when dp_val and count are equal. But if we want to avoid storing lists, we could define a deterministic ordering of sessions (e.g., by ID) and then during DP, for ties, we choose the option that leads to a lexicographically smaller list. But we don't need to store the whole list, we can compare the lists recursively using back pointers. For example, for a given state i, we have two candidates: include_i or exclude_i. Both lead to a solution (set of sessions). We can compare them by comparing (dp_val, neg_count, ids) without materializing the whole list if we have a method to compare two lists lazily. Since we only compare two options at decision points, we could traverse the reconstructed lists in order and compare element by element. But that would be O(n) per comparison, leading to O(n^2) worst-case. But maybe n is small enough? The requirement says efficient O(n log n) algorithm. If we add O(n^2) tie-breaking, it might be okay as n might be up to 10^5? Not sure. But we can aim for O(n log n) with tie-breaking using counts and lexicographic ordering without storing full lists.

There is a known technique: For weighted interval scheduling with tie-breaking on number of intervals, you can store the number of intervals in the DP. For lexicographic ordering on IDs (once sorted by start time), you can treat IDs as strings and use a deterministic rule during reconstruction: when there is a tie between include and exclude, you choose the one that gives a smaller ID at the first point of difference. Since IDs are comparable, you could compare the two potential selected lists without constructing them fully by walking the decision graph. But that would require following pointers. However we can incorporate the tie-breaking in the DP by storing for each node the best "path" in a deterministic way: When choosing between include and exclude, if both yield same total value and same session count, then we need to compare the final sorted ID list. But the final list is sorted by start time, which must be consistent. Since we sort sessions by end time for DP, the chronological order (by start) may not correspond to the DP order. So the list of IDs from including session i and excluding will be concatenations. We need to ensure the final list is sorted by start time. That means when we combine, we need to maintain sorted order. We can always store the selected list sorted by start time for each DP state. But that leads to copying.

Given the constraints are not specified, but they said "include an efficient O(n log n) dynamic programming solution." So the DP must be O(n log n) for the main algorithm. Tie-breaking can be done in O(n) after DP if we compare options? But multiple optimal solutions might be many. To choose the one with fewest sessions, we could after computing dp_val, we also compute dp_minCount for each i by considering tie on value. This is O(n). Then for lexicographically smallest list among those with same value and count, we need to compare lists. We could reconstruct all optimal solutions? That could be exponential.

Alternative: Use a DP that stores for each state the best solution as a tuple (value, count, start_id_list) but we can store the list as a tuple of IDs (immutable) and we can reuse by concatenating? That would still be O(n^2) memory if we store a list at each state. But we can store only the decision (include/exclude) and when tie, we need to compare the resulting lists. We can write a function that given a state i, returns the list of IDs for the optimal solution up to i (sorted by start time). That would be O(n) to compute each list from scratch, yielding O(n^2) overall. Not good.

Perhaps we can avoid the lexicographic requirement by stating that if multiple optimal solutions exist, any is acceptable? But the problem statement explicitly says "choose the one with fewer sessions; if still tied, choose lexicographically smaller list of IDs." So we must implement that.

We need to think of a way to break ties without O(n^2). One approach: Use the DP to compute the maximum value, then do a second pass to compute, for each session i, the maximum number of sessions that can be achieved for that value? Actually we want to minimize count after maximum value. So we can compute dp_val[i] as maximum value, and then we can compute dp_count[i] as the minimum number of sessions achieving dp_val[i]. This can be done by comparing include and exclude: if value[i] + dp_val[p] > dp_val[i-1], then include gives value and count = 1 + dp_count[p]; if <, then exclude gives count = dp_count[i-1]; if equal, we choose the option that yields smaller count. That gives us dp_count[i] as well. This is O(n) after binary search.

Now for lexicographically smallest IDs among those with same value and count, we need a method to break ties. Since we already have dp_count (minimum sessions), we can then compare the ID lists when both options yield same value and same count. Now, we need to decide which list is lexicographically smaller when sorted by start time. We can define a total order among ID lists. However, we can also incorporate the tie-breaking into the DP by storing for each state a representation of the best list that can be compared. But this is tricky.

Observation: The sorting by start time of selected sessions is deterministic and monotonic: if we sort sessions by start time, the selected sessions will be in that order. Since we sort input by end time for DP, the start times might not be monotonic with DP index. But the selected list in chronological order will be sorted primarily by start time. So if we have two potential sets S and T, we can compare them by iterating through sessions sorted by start time. The lexicographic order of IDs in that sorted order. So to compare S and T, we need to walk through the sorted union of their sessions and compare IDs at first difference. This is like comparing the sorted lists.

Can we define a canonical representation of the optimal solution that minimizes lexicographic order? Maybe we can apply a greedy tie-breaking: When considering include vs exclude (both with same value and count), we can decide based on the first ID in the resulting lists when sorted by start time. Since we are building solutions from small end times to larger, maybe we can compute for each state a "fingerprint" string that is the sorted IDs concatenated? That's just the list.

Given the code size limit is under 1000 lines, we can implement a straightforward DP with storing the list of IDs for each state as a tuple, but that could be heavy. However, if we assume that the number of sessions is not huge (maybe up to a few thousand), copying tuples is okay. The problem doesn't specify input size. But it says efficient O(n log n) DP, so it implies that we should handle large n efficiently. Copying lists would break O(n log n) time because each state might involve copying lists O(n) per operation. But many implementations of weighted interval scheduling with reconstruction store only back pointers and then reconstruct at the end, yielding O(n) reconstruction. For tie-breaking, we can incorporate it into reconstruction by careful decisions.

Let's think: After we compute dp_val and p(i) vectors, we can reconstruct the optimal set by backtracking through decisions. But if there are multiple optimal choices (ties), we need to choose the one that yields fewer sessions, then smaller lexicographic list. We can incorporate this into backtracking by at each step, if both include and exclude options yield the same dp_val, we need to choose the one that leads to a better solution as per criteria. However, during backtracking, we don't have direct access to the full list that would result from each option. But we could simulate both paths and compare the resulting sets? That would be exponential again.

We can instead during DP computation store for each i the best decision (include or exclude) based on the criteria. But when values are equal, we need to compare the resulting full solutions. So we need to compute something that allows comparison without full list. Note that if we include i, the solution set includes session i and the optimal solution from p(i). If we exclude i, the solution set is the optimal solution from i-1. Both are optimal for prefix i. To decide which one is better (with same dp_val), we need to compare the two resulting sets. But we can compare them by looking at the sorted list of IDs. Crucially, the sets are composed of sessions from two different intervals. The set from include i includes sessions all ending before start_i? Actually p(i) is the last session non-overlapping with i, so all sessions in solution from p(i) end before start_i, thus they have end time less than start_i. Also session i starts after p(i) ends. So in chronological order, the solution from p(i) comes first, then session i. The solution from exclude i is from i-1, which may contain sessions that are overlapping with i? They could be sessions that end later than start_i but are within prefix i-1. However dp_val[i-1] is optimal for first i-1 sessions (which are sorted by end time). It may include sessions that overlap with i but we are excluding i. So the chronological order of the exclude set might interleave differently? But since we are only considering non-overlapping subsets, the exclude set from i-1 is a set of non-overlapping sessions all of which end before or at the end time of session i-1 (which is ≤ end_i because i is sorted by end). However, some sessions may start after start_i? Possibly, but they will still be in chronological order. However, comparing the two sets lexicographically is not simply comparing the smallest ID etc. But maybe we can compare the two sets by first comparing the first few IDs in sorted order. But we don't have lists.

We can think of this as a partial order: For tie-breaking, we want the set that is lexicographically smallest when sorted by start time. We can model each set as a sequence of IDs in start time order. This is like comparing two sequences. To decide which one is smaller, we can try to simulate the sorted order comparison by iterating through all sessions in start time order and picking the first difference. This can be done by a function that takes two decision pointers and walks through the two possible solutions in order, comparing IDs as they appear. However, the solutions are defined recursively. We can implement a lazy comparison function that given a state i and a decision (include or exclude) returns the list of IDs as a generator? But we need to compare two such generators element by element. That can be done by lazily generating the next ID until a difference. But each next ID might require recursive generation, which could be O(n) per comparison. In the worst case, we may compare at many decision points, leading to O(n^2) again.

Given that the code limit is 1000 lines and practical input sizes maybe moderate, we can consider a simpler approach: Use the DP with storing the selected list (as tuple) for each i, but only when needed for tie-breaking. Since we only need to store the best solution for each i (including count and list), we can store the full list as a tuple of IDs sorted chronologically. For each i, we compute candidate_include = (value_i + dp[p(i)].value, 1 + dp[p(i)].count, dp[p(i)].ids + (id_i,))? But note that dp[p(i)].ids is already sorted chronologically (since it's from earlier sessions, all ending before start_i, so adding session i at the end maintains chronological order because i's start is after p(i)'s end and thus after all starts in dp[p(i)].ids? Actually np: Since dp[p(i)].ids are sessions that end before start_i, they all have end time < start_i, thus also start < start_i (because start < end). So chronologically they all come before session i. So appending i at the end yields correct chronological order. For exclude case, candidate_exclude = dp[i-1].value, dp[i-1].count, dp[i-1].ids. So we just need to compare these tuples: first compare value (higher better), then count (lower better), then ids (lexicographic smaller better). Since we are maximizing value, then minimizing count, then minimizing ids. So we can define a key: (value, -count, ids) but note that for comparison we want higher value better, so we can use (value, -count, some negative for ids?). But Python's sort uses lexicographic order, and we can define a custom comparator using `functools.cmp_to_key` or we can store a tuple (value, -count, ids) because we want value high, count low, ids low. However, the tuple will compare ids in lexicographic order as desired. For two options, we can pick the one where (value, -count, ids) is larger (since value we want max). So we can store for each state the best as this tuple, but for ids we need the tuple of IDs (sorted). This means for each i we are copying the ids tuple from the previous solution (p(i) or i-1) and possibly appending one id. In the worst case, the size of the ids tuple is O(n), so copying leads to O(n^2) total time and memory. That's not O(n log n).

But maybe we can do better: we can store the decision and the count, and then after DP we reconstruct the ids list for the optimal solution. However, to break ties on the ids list at decision points, we need to compare the two potential ids lists. We could reconstruct both candidate lists for each tie point? But ties might occur at many points. However, note that ties only happen when dp_val values are equal. In that case, we need to decide between include and exclude based on count and then ids. If we already have dp_count[i] stored, and we have dp_val[i], we can incorporate the count. For ids, we could at each i where include and exclude have same value and same count, we need to choose the one with smaller lexicographic list. To compare the two lists without storing them, we could do a recursive comparison: define a function less_than(option1, option2) that returns True if the list from option1 is lexicographically smaller. This function can lazily compare by walking the decision trees. But we can memoize? Or we can precompute for each i the "best" decision according to the criteria, but to decide we need to compare the two lists. However, if we simply compare the lists by constructing them on the fly, that might be O(n) per comparison, but comparisons might be O(n) in total? Because each i we only compare once, and constructing list on the fly for option include and exclude would be O(n) each, leading to O(n^2). But maybe we can cache the list for each i once we decide, like we can store the optimal ids list for each i (like the DP with copying) - that's the same as copying. So O(n^2) is the same.

Given the requirement "efficient O(n log n) dynamic programming solution", O(n^2) may be considered inefficient. But perhaps we can achieve O(n log n) with tie-breaking using a trick: Since lexicographically smallest list of IDs corresponds to a specific ordering, we can maybe define a canonical ordering of sessions by ID (or by start time) and use a deterministic rule in DP: when there is a tie, choose the include option if the ID of session i is less than the first ID of the exclude option? Not exactly.

Let's explore the nature of lexicographic order on sorted-by-start-time IDs. If we have two solutions with same value and count, which one is lexicographically smaller? It depends on the earliest start time where they differ. Suppose we compare two sets A and B. The sorted-by-start-time list is like S_A and S_B. Compare the first element (ID of earliest session). Because start times are unique? Not necessarily. Start times could be same. But we can sort by start time, then end time, then ID to make it deterministic. We'll need to define chronological order: probably by start time asc, then end time asc, then ID asc to break ties. For that ordering, the list is a sequence. So lexicographic comparison of IDs in that order.

Now, note that the DP decision between include and exclude at a certain i involves solutions that share some prefix? Not necessarily. But we can observe that the optimal solution for a given i is built from two parts: either includes i or not. If we can decide which one is better based on comparing the resulting sorted lists. The sorted list of include solution is: (optimal list from p(i)) + [id_i]. The sorted list of exclude solution is: optimal list from i-1. Since i is after all in p(i) chronologically, and sessions in i-1 may be before or after start_i? Actually, some sessions in i-1 could have end > start_i (overlapping), so they might have start times before start_i? Possibly, but if they overlap with i, they cannot be in the include solution but could be in exclude solution. So the chronological order may mix.

Idea: We can pre-sort sessions by start time (and end time, ID) to define a global ordering index. Then we can enforce that the DP uses this order for reconstruction? Typically DP uses end time ordering. But we could also sort by end time and use it.

Another perspective: Since we want lexicographically smallest list of IDs when sorted by start time, we could define an augmented value that incorporates the ID as a tie-breaker. But lexicographic order is not a simple scalar.

Perhaps we can sort sessions by (start, end, ID) and then treat sessions as items in a sequence where non-overlap is determined by end <= next start? But that's not the typical interval scheduling.

Maybe we can use a two-phase approach: First compute maximum value and minimum count using DP with (value, -count). Then, among all solutions achieving that (value, count), we need the one with lexicographically smallest list. This is like finding the "lexicographically smallest" optimum. This can be done by a second DP that chooses between options based on the list, but we can incorporate a tie-breaker by constructing the list from the end? For many scheduling problems, the lexicographically smallest set can be found by a greedy algorithm after we have the DP values: At each step, we decide whether to include the current session or not based on whether there exists an optimal solution that includes it and gives the best (value,count). If both include and exclude are possible, we need to decide based on lexicographic order of the final list. That could be resolved by comparing the resulting IDs if we include vs exclude, by looking at the earliest session? Not straightforward.

Consider this: Suppose we have DP states that tell us the maximum value and minimum count for each prefix. For a given session i, we want to decide if we include it in the global optimal solution. We can check: Is there an optimal solution (with global max value and minimum count) that includes i? This can be answered by checking if dp_val[i] (with include) equals global max? Actually, global solution corresponds to dp_last. We can do backtracking with choices. For tie-breaking among different optimal solutions, we want the one with smallest list count, then smallest lexicographic list. So during backtracking, when both include and exclude give the same dp_val and dp_count, we need to choose the one that gives smaller lexicographic list. So we need to compare the two full lists. But if we prepopulate for each state the best list (only for the chosen decision) then we have O(n^2) but maybe we can store only the chosen best list for each state (with tie-breaking) and that's O(n^2) overall.

Maybe we can reduce storage by using linked lists and only storing the decision and count. For lexicographic comparison, we could compare two solutions by recursively walking the linked lists. To avoid O(n) per decision, we can precompute a "fingerprint" like a hash of the list? But lexicographic order requires exact comparison; we could use a rolling hash and binary search for the first difference? That could be O(log n) per comparison, but we need to compare potentially many pairs. That adds complexity.

Given the code-writing exam context, perhaps they expect a neat solution that uses DP with counts and then for final tie-breaking on IDs, they might not store full lists if they assume IDs are unique and they can compare the list of IDs by simply comparing the current ID in the include branch against the first ID in the exclude branch? That doesn't work because the entire list must be compared.

Maybe the problem constraints are small? The requirement says "include an efficient O(n log n) dynamic programming solution." Possibly they mean the core algorithm is O(n log n) ignoring tie-breaking on IDs, but we can still implement tie-breaking in O(n log n) using some cleverness.

Let's search for known techniques: For weighted interval scheduling with lexicographically smallest set (by some order), typically you can break ties by iterating over sessions in chronological order and deciding inclusion based on whether it doesn't prevent achieving optimal value with minimal count? But that would produce some set, not necessarily lexicographically smallest.

A standard approach to get the lexicographically smallest optimal solution for knapsack-like problems is to sort items in reverse order and do DP that prefers taking the item if it leads to an optimal solution. For interval scheduling, we can consider sessions sorted by start time (chronological). Then for each session in order, we decide to include it or not, using DP values that tell us the best value achievable from a given point. This is similar to a "forward" DP. If we define DP[i] as optimal value from sessions starting at or after some time, we can make decisions in chronological order. Lexicographically smallest set of IDs (where set is sorted by start time) can be obtained by, for each session in chronological order, if including it doesn't prevent achieving the overall optimal value (and count), we include it; else we skip. But we also need to consider minimal count. So we need to compute optimal value and minimal count. Then we can greedily decide inclusion based on whether there exists an optimal solution (with global optimal value and minimal count) that includes this session. This greedy works for lexicographically smallest set if we iterate in the order of the sorted list (here, chronological). Because the list order is exactly the order we process. This is analogous to reconstructing the lexicographically smallest optimal solution in LIS problem.

So we can: 1) Sort sessions by start time (and then end, ID) to define chronological order. Let this order be indexed 0..n-1. We'll keep the original ordering but we'll work with this sorted list for reconstruction. 2) But we need non-overlapping: the DP must respect intervals overlapping. So we cannot simply treat as sequential selection in chronological order because consecutive sessions in chronological order may overlap. However, we can define a DP that processes sessions in chronological order and uses binary search to compute the previous non-overlapping session. This is analogous to the classic DP but sorted by end time. For lexicographic reconstruction, if we want to process sessions in start time order, we might also need a DP sorted by start time.

The classic DP works with intervals sorted by end time. To get lexicographically smallest set when sorted by start time, we could do the DP sorted by end time, but then during reconstruction, we can decide between include and exclude options by checking if including the current session is consistent with achieving the best value and count. But the "current session" in backtracking is in reverse order of indices (from last to first). That may not correspond to chronological order for easy greedy.

I think a simpler method (which may be acceptable for the coding challenge) is to store the list of IDs as a tuple for each DP state, accepting O(n^2) memory/time. Given that we are to write a single-file script, and the problem likely from a coding interview, they may not stress large n. The requirement "efficient O(n log n)" might refer to the overall algorithm, but tie-breaking might be considered negligible or they assume we break ties arbitrarily? But the spec explicitly states tie-breaking rules. Maybe they expect us to implement the DP and then for tie-breaking, we can do a second pass that compares solutions on the fly using the stored dp values and counts.

Let's read the problem again: "If multiple optimal solutions exist, choose the one with fewer sessions; if still tied, choose lexicographically smaller list of IDs." This is part of the requirements, so we must implement it. It doesn't say the tie-breaking must be O(n log n). So perhaps we can implement it in a way that is still efficient for moderate n.

I think I can implement the DP with storing for each i a tuple (value, count, ids) where ids is a tuple of IDs. Since we only store the best solution for each i, and we copy the previous best solution for the option (include or exclude), but we never compare both options if one is strictly better on value or count. Only when value and count are equal do we compare ids. So the copying of ids only occurs when value and count are equal, which may not happen often? In worst case, all intervals could have same value and all solutions have same count? But not likely. However worst-case could be designed. But even then, copying ids could be O(n^2). However, we can mitigate by using immutable tuples and appending: include solution's ids = dp[p(i)].ids + (id_i,). That creates a new tuple of length len(dp[p(i)].ids)+1, which is O(k) copy where k is current length. So across all i, the total copying time sums to O(n^2) in worst case. That's not O(n log n). So we need to avoid that.

We can store the decision as a pointer to the previous state plus a flag, and then for reconstruction we can walk back to build the list. But to compare two options at decision time, we would need to compare the full lists without rebuilding. Could we compare two lists by comparing the decisions in reverse order? Suppose we have two paths: path_include = include i, then follow dp from p(i). path_exclude = follow dp from i-1. Both yield optimal for prefix i. We want to compare their sorted-by-start-time ID lists. Since the lists are sorted by start time, and because of the way intervals are sorted by end time, the order in the list is not necessarily the same as the DP index order. So we can't easily compare by just comparing the latest IDs.

But maybe we can enforce a consistent chronological order for all solutions: they all will be sorted by start time. So the list is naturally the sequence of sessions sorted by start time. If we can compute the list for a solution recursively, we could compare two such lists element by element. We can write a function that takes a state i and a flag (include or exclude) and returns the ID at a given position? Not efficient.

Alternative: Instead of storing full list, we can store a hash of the list that allows lexicographic comparison? Not possible.

We could use a persistent data structure like a rope, but that's overkill.

Given the constraints (single file, 1000 lines, no third-party), maybe it's acceptable to use an O(n^2) algorithm for tie-breaking as long as we note that the main DP is O(n log n). We can separate the algorithm: first compute dp_val and dp_count and p(i) using O(n log n). Then we need to choose the lexicographically smallest IDs among optimal solutions with maximal value and minimal count. This is a separate problem: given the set of optimal solutions (with given (val, count)), pick one with lexicographically smallest IDs sorted by start time. We can solve this by considering sessions in start time order and using the DP information to decide inclusion greedily.

Let's explore that greedy approach in detail.

We have all sessions. We want to pick a subset S that is non-overlapping, maximizes total value (global max V*), and among those, minimizes count (global min count C*), and among those, minimizes the list of IDs when sorted by start time (lexicographically). To find such S, we can process sessions in increasing start time (then end time, then ID to break ties). For each session in order, we decide whether to include it or not based on whether we can still achieve the global optimal with the remaining sessions. This is similar to constructing the lexicographically smallest optimal solution for many combinatorial problems using the concept of "feasibility" with future DP.

We need to precompute DP that gives the best value and count for any suffix or prefix. Typically, if we process sessions in chronological order (start time), we need a DP that tells us the optimal value from a given start time onward. That is a classic "weighted interval scheduling" from the right side. We could compute dp_right[i] = maximum value achievable from sessions starting at or after some time. More precisely, sort sessions by start time. For each session i (in start time order), let f(i) = maximum value achievable using sessions from i to n-1, with non-overlap. This can be computed with binary search on the first session that starts after session i's end. Then dp_right[i] = max(value_i + dp_right[next], dp_right[i+1]). Similarly we can compute count_min[i] for minimal number of sessions for that max value.

But we want both value and count. So we can compute for each state (i) the best (value, count) from that prefix. Then, when constructing lexicographically smallest list, we process sessions in start time order. At step i, we consider including session i if it's feasible with the rest (i.e., does not overlap with already selected sessions). But we can maintain a pointer current_time. Actually, we can do: start with selected = [], last_end = -inf. For each session i in chronological order (start time sorted), if session i's start < last_end, skip (overlap). Else, decide whether to include i in the final set. The criteria: There exists an optimal solution (global (V*,C*)) that includes session i and also respects previous choices (i.e., is consistent with selected so far). If yes, we include it and update last_end = session.end; else, we skip. This greedy approach will yield the lexicographically smallest list because we process sessions in chronological order and we include the earliest possible session that can be part of some optimal solution. This works if the feasibility check "exists an optimal solution that includes i given previous choices" can be done efficiently.

To implement this, we need to compute, for any position i and given that we have already selected some sessions, the best possible value and count from the remaining sessions (that start after the last_end) that can be achieved, and compare with the global optimum minus value of selected sessions. Precisely, we need to know the maximum (value, count) achievable from the future. This suggests a DP that, for each index in start-sorted order, gives the optimal value and count from that point onward, assuming no overlapping constraints with outside? Since we process chronologically, the non-overlap condition is that we cannot select any session that overlaps with already selected ones. If we decide to include a session i, then we move the last_end to its end, and the remaining sessions must start >= end_i. So we need DP info for the suffix starting with the first session that doesn't overlap with end_i.

So we can precompute, for each session i (sorted by start), the index next[i] = first session j such that start_j >= end_i (or n if none). Then we can compute DP suffix arrays: opt_value[i] and opt_min_count[i] represent the best (value, count) achievable from sessions i..n-1 (inclusive) with the condition that they are non-overlapping among themselves and can start from any time (no external constraint). Because the DP for suffix will naturally ensure non-overlap by the recurrence dp[i] = max(value_i + dp[next[i]], dp[i+1]), where dp[i] is the maximum value; for count, we can also store min count for that max value.

Then, when constructing the lexicographically smallest list, we start at i = 0 (first session chronologically), with last_end = -inf (or start_min). We want to decide whether to include session i. We can if start_i >= last_end. Then we need to check if there exists an optimal solution that includes session i, given that we have already selected some sessions (selected set so far has total value_sel and count_sel). But we are at the beginning, so selected set empty. The feasibility condition: There exists a suffix solution from next[i] (or later) that when combined with session i achieves the global optimum (V*, C*). That is: value_i + opt_value[next[i]] = V* and 1 + opt_min_count[next[i]] = C*? Not exactly because opt_value[next[i]] is the max value from that suffix, but it might be part of some optimal solution, but what if the optimal from suffix uses sessions that overlap with something? Since next[i] is defined as first session starting after end_i, it won't overlap, so it's fine. However, the global optimal might not use session i even if that equation holds, because there could be other optimal solutions that skip i but still achieve V* and C*. We need to see if there exists an optimal solution that includes i. That is true if and only if value_i + opt_value[next[i]] == V* and (1 + opt_min_count[next[i]] == C* for some minimal count? Actually for minimizing count, we need that there exists an optimal solution with count = C* that includes i. So we need that there exists a suffix solution with value = V* - value_i and count = C* - 1. But the suffix DP gives the maximum value from that suffix; but there could be multiple ways with same max value but different counts. We need to know the minimal count achievable for the max value from suffix. If that minimal count is exactly C* - 1, then we can achieve the global optimum by including i. However, there might be other optimal solutions with the same V* but higher count? But we want C* minimal, so we only count solutions achieving V* with minimal count C*.

Thus, we can compute for each suffix the best (value, count) pair, where best is defined as maximizing value, and among those minimizing count. Let's denote dp_val[i] and dp_cnt[i] as the maximum value and minimum count from sessions i..n-1 (sorted by start). Then global optimum is dp_val[0] and dp_cnt[0].

Now, to decide if we should include session i in the lexicographically smallest optimal solution, we check if:

- start_i >= last_end (overlap condition)
- value_i + dp_val[next[i]] == dp_val[0] (the global max value, but careful: dp_val[0] is from entire set; but after we have selected some sessions, we should compare with remaining optimum relative to current time? For the first decision, yes.)
- 1 + dp_cnt[next[i]] == dp_cnt[0] (since we want minimal count)

But after we include session i, the remaining problem becomes from next[i] onward, and we expect to achieve dp_val[next[i]] and dp_cnt[next[i]] to complete the global optimum. So if these equations hold, then including i can lead to a global optimal solution (with minimal count). If we skip i, we can still get global optimum if dp_val[i+1] == dp_val[0] and dp_cnt[i+1] == dp_cnt[0]. So both may be possible. Which one should we choose? For lexicographically smallest list, we want to minimize the first element. So we should include i if it is possible to include i in some optimal solution (with the required value and count). Because then the first ID will be earlier (or the same) compared to skipping, but the ID may be different. Since we process chronologically, the first session in the list will be the first included session. If we can include session i (the earliest session) in an optimal solution, then the first ID will be i's ID. If we skip i, the first ID might be later, which could be lexicographically larger (since i is earlier sort order, its ID could be smaller or larger; but if we skip the earliest possible session, the first element of the list will be some later session, which could have a later start time and possibly a larger ID? Not necessarily: ID is a string, not necessarily correlated with time. Lexicographic comparison is on IDs, not times. So the absolute start times do not matter for ID ordering. So the greedy approach based on chronological order may not directly give lexicographically smallest IDs. For example, consider two optimal solutions: one includes session A (start time earlier, ID "z"), another includes session B (start time later, ID "a"). The sorted-by-start list for A-solution: ["z",...]; for B-solution: ["a",...]. Since "a" < "z", the B-solution is lexicographically smaller even though it skips the earliest start session. So we cannot just include the earliest session that can be part of an optimal solution; we need to consider IDs. So the greedy process must consider IDs, not start times.

Thus, the sorting order for the final list is by start time, but the IDs are independent. Lexicographic comparison of lists is based on the first elements (IDs) regardless of start time? But the list order is sorted by start time, so the first element is the ID of the session with the earliest start time. So the start time determines the ordering of the list, but the IDs are the actual elements. So to minimize the list lexicographically, we want the first element's ID as small as possible, but that first element must be some session with the earliest start time among selected sessions. So we can consider all sessions that could be the first selected session (i.e., the earliest start in the solution). We want to choose the one with smallest ID among those? But we also need to ensure that the rest of the solution can be completed to global optimum. Then after choosing first session, we consider the next earliest start time that can be second, etc. This is similar to constructing lexicographically smallest sequence in order of start time, but we have flexibility in which sessions we pick. So we can indeed iterate over sessions in increasing start time (chronological order) and decide to include or skip based on whether including that session can lead to an optimal solution, but the decision must prefer including if it leads to a lexicographically smaller list? Not exactly: If we include a session with a small ID early, that might make the first element small, which is good. But if we skip a session with a large ID, that could allow us to include a later session with an even smaller ID as the first element? That's impossible because the first element's start time is the minimum start among selected sessions. If we skip session i (earliest start time), the first element will have a start time > start_i. That session's ID could be smaller than session i's ID. So we cannot simply include every session that can be part of an optimal solution; we need to compare the full list. So the greedy need to make decisions based on IDs. Essentially, we want to construct the lexicographically smallest list of IDs (when sorted by start time) among optimal solutions. That is similar to finding the smallest sequence under constraints. This can be solved by iterating over positions in the sorted list (by start time) and at each position, considering sessions that can be placed at that position (i.e., sessions that start after the previous session's end) and among those that can lead to an optimal solution, we pick the smallest ID. This is like a standard approach for lexicographically smallest optimal schedule: process in the order of interest (here, start time order), and for the current position, try all possible candidates (sessions) in increasing ID order, check if picking that session can be extended to an optimal solution (with the rest). We pick the first that works. This works because we are constructing the list element by element.

So algorithm:

- Let all sessions. Compute global optimal value V* and minimal count C* using DP on intervals sorted by end time or start time. (Will need also DP for suffix/prefix to compute feasibility of future after choosing a session.)
- Sort sessions by start time (and then end time, then ID) to define the chronological order for list output? Actually, the output list of IDs is in chronological order. That is exactly sorted by start time (with tie-breakers). So we can consider sessions in that order as the position slots. But note that the list we output will have selected sessions sorted by this order. So the construction will be: we need to choose a subset that is non-overlapping and achieves V* and C*, and we want its sorted-by-start list of IDs to be lexicographically smallest. This is equivalent to saying that when we list the sessions in chronological order, the sequence of IDs should be lexicographically smallest among all subsets achieving V*, C* (non-overlapping). So we can treat this as constructing a sequence from a set of items where order is forced by start times. Since start times determine order, we can consider sessions in increasing start time as candidate elements of the sequence. But we cannot just pick any session at each position because they may overlap. The standard way: We will construct the sequence by iterating over possible positions (chronological order) and at each step choose among the sessions that are still available (not overlapping with previously chosen) and have a chance to be part of an optimal solution (given remaining capacity). Usually, for problems like "smallest sequence of items to achieve max value" we can use DP to compute for each state the best value and count from that state, and then for reconstruction we do greedy: at each step, sort possible choices (by ID) and try them in order; after picking one, we check if the remaining can achieve the needed remainder. This yields lexicographically smallest.

Thus, steps:
1. Read sessions, validate, separate into list of valid sessions. Invalid ones go to rejected with reason.
2. For valid sessions, we need to compute global optimal (V*, C*). We'll use DP on sessions sorted by end time (classic). But for ease of suffix DP needed for reconstruction (to answer "given current time (last end) and remaining sessions, can we achieve a certain value and count?"), we might prefer to sort sessions by start time and compute suffix DP. Actually both are possible. Let's choose to sort sessions by start time (and then end, ID) to get a list L of length n. For each session i (0-indexed in this order), we can compute next[i] = first index j such that L[j].start >= L[i].end. This can be found with binary search (since start times sorted). Then we compute dp_val[i] and dp_cnt[i] from right to left: dp_val[i] = max(value_i + dp_val[next[i]], dp_val[i+1]). dp_cnt[i] = corresponding minimum count (if tie). This is O(n log n) due to binary search. This yields the best from suffix starting at i (i inclusive). The global optimum is dp_val[0] and dp_cnt[0].

Now, we want to reconstruct the list of sessions that achieves (dp_val[0], dp_cnt[0]) and yields lexicographically smallest IDs when sorted by start time. Since we need the list in start-time order, and we have sorted sessions by start time, the list will be a subsequence of L (but not necessarily contiguous) that respects non-overlap (which is enforced by next indices). To reconstruct lexicographically smallest, we can iterate over i from 0 to n-1, but we need to decide whether to include L[i] or not, but decisions affect future because if we include L[i], we must skip all sessions that overlap (those with start < end_i) and jump to next[i]. So we can do this: starting at index i=0, and with a global target value V = V*, target count C = C*. At current index i (which can move forward), we consider the possibility of including L[i] if we have not already passed its start time? Actually we will maintain a variable `pos` that is the current index in the sorted list (the earliest session we are considering). Initially pos = 0. We also have `last_end` = -inf (or earliest time). But because L is sorted by start, we know that at pos, L[pos] is the earliest remaining session. We want to decide to include it or skip it. The greedy for lexicographically smallest: we should try to include L[pos] if there exists an optimal solution (achieving global optimum) that includes L[pos] given that we have not selected anything yet. But is it always optimal to include L[pos] if possible? No, because excluding could lead to a smaller ID later. However, since L[pos] is the earliest start time, if we include it, it becomes the first element of the list. That element's ID might be large; if we exclude it, the first element will be some later session (with a later start time) which could have a smaller ID. Since we compare lists lexicographically, it's the first element that matters most. So if we include L[pos], the first ID is L[pos].id; if we exclude, the first ID will be the ID of the first selected later session (say L[j].id). So if L[pos].id > L[j].id, excluding yields smaller lexicographic list, even if inclusion is possible. So we cannot just include based on feasibility; we need to compare the resulting lists.

Thus, the standard technique: We need to determine the smallest possible ID for the first element among all optimal solutions. That is, find the session with the smallest ID that can be the first session of an optimal solution (i.e., can be selected and there exists a completion achieving V* - value, C* - 1 from sessions that start after its end). Among all such sessions, choose the one with smallest ID. That becomes the first element. Then we remove that session and all sessions that overlap with it (those with start < its end have to be skipped because they overlap? Actually any session that starts before its end cannot be selected after it, and cannot be before because we are going in chronological order; so we can discard all sessions with start < its end as they are either overlapping (and cannot be selected) or before (but they are not selected because we chose this as first). Then we set new target value = V* - value, target count = C* - 1, and set last_end = its end. Then we repeat on remaining sessions (starting from the first session with start >= last_end). This yields a greedy algorithm that produces lexicographically smallest list because we always pick the smallest possible first element, then second, etc. This is correct if the optimization problem has the property that once we fix the first element, the rest is independent and we can again apply the same greedy for the remainder (optimal substructure). Indeed, after picking the first session, the remaining problem is to find an optimal solution (with target value and count) from sessions that start after its end. Since the overall optimal solution is composed of first session and an optimal solution from the suffix (with endpoints after first's end), and the list comparison is lexicographic, choosing the smallest possible first element (by ID) yields the globally lexicographically smallest list, because the first element is compared first. So we can do:

- Compute for each suffix i the best (value, count) from i onward (using start-sorted array). Also we need to be able to answer: For a given start index i and a given target value and count? Actually we need to know if there exists a solution from index i achieving a certain value and count. But we only need to check if a particular session can be the first element leading to an optimal overall (value, count). Specifically, for a session at index i, we need to verify that value_i + dp_val[next[i]] == V* and 1 + dp_cnt[next[i]] == C* (since we need exactly minimal count). If that holds, then session i can be first in some optimal solution. But there could be multiple sessions satisfying that. Among them, we pick the one with the smallest ID. However, note that the first session must have the earliest start time among selected sessions. So it must be that there is no selected session with start < start_i. Since we are considering sessions in order of increasing start time, the first session will be the one with the smallest start time among selected sessions. If we pick a session i that has a later start, but there exists another session j with earlier start that satisfies the condition, then j's start is earlier, so any solution that includes j as first would have earlier start time, so the list order would have j's ID before i's ID. So we must consider only sessions that are the earliest in the solution; but if we consider all i in increasing start order, the first session we pick must be the first selected session; thus it must be that no earlier session is included. So we need to consider sessions that can be the first selected, meaning no earlier session is selected in the optimal solution. However, if there is an earlier session that also can be part of an optimal solution (as first), then we would prefer the one with smallest ID, but that earlier session's start is earlier, so its ID would appear first in the list, which is correct. So we should consider sessions in increasing start order, but we cannot simply look at each session in isolation; we must consider that if we skip an earlier session, it cannot be selected later because it overlaps with our first? Actually, if an earlier session j (start smaller) is not selected, it can't be in the solution because it would then have earlier start. So if there exists an optimal solution that includes session j as first, then that solution's first element is j.id. If there also exists an optimal solution that includes session i (later start) as first (i.e., no earlier sessions selected), then the lexicographic comparison between these two solutions would compare j.id vs i.id. If j.id < i.id, solution with j as first is better. If j.id > i.id, solution with i as first is better. So we need to consider all sessions that can be the first selected (i.e., there is an optimal solution where that session is the earliest). So we need to identify the set of sessions that can be the first in some optimal solution. Then pick the one with smallest ID. Then after picking, we repeat on the suffix.

But note: If we pick session i as first, we must ensure that no earlier session (with start < start_i) is selected. That means we must also consider whether there exists any optimal solution where an earlier session (j with start < start_i) is not selected but j could be part of the solution at a later position? No, if j has start < start_i, it cannot be selected after i because it would have earlier start, breaking chronological order. So if we are considering i as first, we must assume that all sessions with start < start_i are excluded entirely. So we need to ensure that there exists an optimal solution that excludes all sessions before i. That is equivalent to saying that we can achieve V* and C* from sessions starting from i (including i) without using any earlier sessions. This is captured by dp_val[i] == V* and dp_cnt[i] == C*? Not exactly, because dp_val[i] is the maximum value from sessions i..end, which includes i but also could exclude i and use later sessions. But if dp_val[i] == V* and dp_cnt[i] == C*, does that mean there exists an optimal solution using only sessions from i onward? Yes, because the maximum value from i..end equals global optimum, and the minimum count for that value from i..end equals global min count. So that means that the global optimum can be achieved without using any sessions before i. So session i can be the first selected only if there exists an optimal solution that uses sessions only from index i onward. Moreover, we also need that session i itself is included in that optimal solution? Not necessarily. For session i to be the first selected, it must be included. So we need to check that there exists an optimal solution starting from i that includes i. That requires: value_i + dp_val[next[i]] == dp_val[i] (since dp_val[i] = max(value_i + dp_val[next[i]], dp_val[i+1])) and also the count condition. Actually if value_i + dp_val[next[i]] == dp_val[i] and 1 + dp_cnt[next[i]] == dp_cnt[i] (where dp_cnt[i] is the minimum count for dp_val[i]), then there is an optimal solution that includes i (and this solution achieves dp_val[i] and dp_cnt[i]). But we also need dp_val[i] == V* and dp_cnt[i] == C* for it to be globally optimal. So for a session i to be a candidate for first selected (earliest in the final set), we need:
- dp_val[i] == V* and dp_cnt[i] == C* (global optimum achievable from i without earlier sessions)
- There exists an optimal solution from i that includes i, i.e., value_i + dp_val[next[i]] == V* and 1 + dp_cnt[next[i]] == C* (since global optimum value and count from i).

Note: If both conditions hold, then session i can be first. However, there might be multiple i satisfying this. Among them, we pick the one with smallest ID. But we also need to ensure that no earlier session is selected; but condition dp_val[i] == V* ensures that we can achieve global optimum without earlier sessions. So it's fine.

But we must also check that after picking i, we can complete from next[i] with target value V* - value_i and count C* - 1. This is satisfied if dp_val[next[i]] >= V* - value_i and dp_cnt[next[i]] <= C* - 1? Actually we need exactly value_i + dp_val[next[i]] == V* and 1 + dp_cnt[next[i]] == C* to match the optimal solution we are constructing. But after we pick i, we want to achieve exactly the global optimum; we don't want to overachieve. So we need that there exists a solution from next[i] that yields value = V* - value_i and count = C* - 1. Since dp_val[next[i]] is the maximum value from next[i], and dp_cnt[next[i]] is the minimum count for that max value, if value_i + dp_val[next[i]] == V* and 1 + dp_cnt[next[i]] == C*, then there exists such a solution. If dp_val[next[i]] > V* - value_i, then value_i + dp_val[next[i]] > V*, which cannot happen because V* is global max. So equality must hold for the max. So condition is correct.

Thus, we can find first session: among all i (0 <= i < n) such that dp_val[i] == V* and dp_cnt[i] == C* and value_i + dp_val[next[i]] == V* and 1 + dp_cnt[next[i]] == C*, choose the one with smallest id (if ties in id? But ids are unique? Possibly not; the problem doesn't say IDs are unique. We should assume IDs might not be unique? Usually they are unique identifiers; we can assume they are unique? Not explicitly. But for lexicographic comparison, if two sessions have same ID, then lists could be identical? But if they have same ID and both can be first, we need to break ties by maybe the next element. We'll treat as unique, but if not, we can handle by comparing the rest. But simpler: we can assume IDs are unique per session; the problem examples show unique ids. We'll assume unique. Then we can pick smallest id.

After picking first session i*, we then consider the next session index = next[i*] (the first session with start >= end_i*). But also we must skip all sessions with start < end_i* because they overlap and cannot be included. So we set new start index = next[i*]. The new global target value becomes V* - value_i* and new target count becomes C* - 1. Now we repeat: among sessions j from new_start_index onward, find candidates that can be the next selected (i.e., first in the remaining suffix) with the new target. We need to know, for a given suffix start index s, what is the best value and count achievable from s? But we can precompute dp_val_suffix and dp_cnt_suffix for each index. So after picking i*, the new target is not the global optimum of the suffix (i.e., dp_val[next[i*]]), but we want to achieve exactly that? Actually, since we are continuing to build the solution that yields global optimum, we know that after including i*, the remaining should achieve value = V* - value_i* and count = C* - 1. And we know that there exists at least one solution from next[i*] achieving that (by condition). But there might be multiple solutions from next[i*] that achieve that; we want the one that makes the overall list lexicographically smallest. So we now need to find the lexicographically smallest list of IDs (in start order) from suffix starting at next[i*] that achieves value = target_value, count = target_count, with non-overlap. This is the same problem but with a target value and target count that may not be the maximum from that suffix (since the suffix might have max value > target_value). However, we need to achieve exactly target_value; we cannot exceed because we already have the global optimum. So we need to find among solutions from suffix that give exactly the target value and count (and are non-overlapping) the one with lexicographically smallest IDs. To solve this, we can use a similar approach but with DP that gives, for each state i and for a given target value, whether it's achievable? That seems more complex.

But note: Since we always aim for the global optimum, and after picking i*, we know that dp_val[next[i*]] >= target_value (in fact it's exactly target_value because dp_val[next[i*]] is the maximum value from next[i*]; and we required value_i + dp_val[next[i*]] == V*, so dp_val[next[i*]] = V* - value_i = target_value. So target_value is exactly the maximum value achievable from next[i*]. So we are again in the same situation: we need to find the optimal (max value) from the suffix, but we also require the count to be minimal (target_count = C* - 1). And we also require that the resulting list IDs are lexicographically smallest among those achieving that max value and minimal count. So it's the same problem on the suffix. So we can recursively apply the same greedy: at each step, we want the first session in the remainder (the earliest start) that can be part of an optimal solution for the remainder (max value, min count). The condition for a session j in the suffix (starting at index s) to be the first in the optimal solution for that suffix is similar but uses dp_val_suffix and dp_cnt_suffix relative to that suffix. That is, for the suffix starting at index s (we consider indices j >= s), we have dp_val[j] and dp_cnt[j] defined as the maximum value and minimum count from j onward (global). And we have global optimum for the suffix starting at s is dp_val[s] and dp_cnt[s] (which equal target_value and target_count). Then a session j >= s can be first in the optimal solution for the suffix if:
- dp_val[j] == dp_val[s] and dp_cnt[j] == dp_cnt[s] (i.e., the overall optimum for the suffix can be achieved from j without using any sessions before j)
- value_j + dp_val[next[j]] == dp_val[j] and 1 + dp_cnt[next[j]] == dp_cnt[j] (i.e., there is an optimal solution from j that includes j)
Or equivalently, since we already know dp_val[s] and dp_cnt[s] are the optimum for suffix starting at s, and we want the first element, we can iterate j from s onward and check if it satisfies the conditions relative to the global suffix optimum? But careful: The suffix optimum we are targeting is dp_val[s]. For a candidate j (>= s), if dp_val[j] < dp_val[s], then it cannot achieve the target value because max from j is lower. So we need j such that dp_val[j] == dp_val[s] and dp_cnt[j] == dp_cnt[s]. Then we also need that j can be included in an optimal solution for that prefix, i.e., the include branch gives the optimum. So we can find the smallest id_j among j in [s, n-1] satisfying these conditions, and set that as the next selected. Then set new s = next[j].

But we must also ensure that j does not overlap with previously selected sessions. Since we advance s to next[j], this automatically ensures no overlap. Also, we need to ensure that there is no earlier session (i.e., sessions between s and j-1) that we skip; but if dp_val[s] == dp_val[j] and dp_cnt[s] == dp_cnt[j], then there exists an optimal solution that skips all those earlier sessions (since max from j equals max from s). So it's fine.

Thus, the reconstruction algorithm for lexicographically smallest IDs (by start order) is as follows:

1. Sort sessions by start time (and then end time, then ID) to produce array `sessions_sorted`.
2. Compute `next` array: for each index i, next[i] = first index j > i such that sessions_sorted[j].start >= sessions_sorted[i].end, or n if none. This can be done with binary search on start times array.
3. Compute suffix DP: dp_val[i] = maximum value from sessions i..n-1; dp_cnt[i] = minimum count for dp_val[i]. Recurrence:
   - include = value_i + dp_val[next[i]]; include_cnt = 1 + dp_cnt[next[i]]
   - exclude = dp_val[i+1] (with i+1 <= n? define dp_val[n] = (0,0), dp_cnt[n]=0)
   - If include > exclude: choose include; dp_cnt = include_cnt.
   - If include < exclude: choose exclude; dp_cnt = dp_cnt[i+1].
   - If equal: choose the one with smaller count; if still equal, we need to tie-break for lexicographic IDs later? At this stage, we only care about max value and min count; we don't need to break further because we'll reconstruct using the greedy method that will break ties lexicographically. So when values equal, we pick the minimum count. If counts also equal, we can pick either (say exclude) because the greedy reconstruction will later select the lexicographically smallest from all optimal solutions anyway. However, if we fix one arbitrary choice in the DP, it might restrict the set of optimal solutions considered by the greedy reconstruction? No, the greedy reconstruction will use dp_val and dp_cnt arrays to check conditions, but if we arbitrarily pick exclude when include and exclude have same value and count, then the dp_val[i] remains correct (since both give same value), and dp_cnt[i] (min count) is correct. However, we must be careful: The condition for a session to be first includes checking include branch yields optimum. If due to arbitrary tie-breaking, the dp_val[i] may be associated with exclude branch even if include also yields same value and count. But we still need to consider that include branch exists. Our condition "value_i + dp_val[next[i]] == dp_val[i] and 1 + dp_cnt[next[i]] == dp_cnt[i]" checks if the include branch gives the same value as dp_val[i] and the same minimal count. Since dp_val[i] is the maximum value, if include gives the same value and count, then concatenation should hold regardless of which branch we stored. So dp_val[i] and dp_cnt[i] are correct (max value, min count). We just need to verify equality. So it's fine.

But what if include and exclude have same value and same count, but we later need to know that both are valid for the greedy? The condition above for candidate j uses include branch: it checks if value_j + dp_val[next[j]] == dp_val[j] and 1 + dp_cnt[next[j]] == dp_cnt[j]. If both include and exclude give same value and count, then this condition would be true for include branch (since include branch can achieve dp_val[j] and dp_cnt[j]). So it's fine. If we stored exclude as the basic solution but include also works, the condition still holds because dp_val[j] equals that value. The DP arrays don't store which branch; they just store the value and count. So the condition we use for candidate j (include branch) is an independent check; it doesn't rely on stored decision. So the tie-breaking in DP for value and count is fine.

4. After we have dp_val and dp_cnt for all i, compute global V* = dp_val[0], C* = dp_cnt[0].

5. Now reconstruct lexicographically smallest list:
   - Initialize current index s = 0.
   - Initialize target_val = V*, target_cnt = C*.
   - Initialize selected_ids = [].
   - While s < n and target_cnt > 0: (we can stop when target_cnt == 0, but also if target_val == 0)
       - We need to find the smallest ID among sessions in [s, n-1] that can be the next selected session in the optimal solution for the suffix starting at s (with target value and count). That is: find index j in [s, n-1] such that:
           * dp_val[j] == target_val   (since the optimum from j must equal the required target value)
           * dp_cnt[j] == target_cnt   (min count)
           * value_j + dp_val[next[j]] == target_val   (include branch yields exactly the target value)
           * 1 + dp_cnt[next[j]] == target_cnt   (include branch yields exactly the target count)
         If multiple satisfy, pick the one with smallest id (string comparison). If still tie (same id? should be unique), pick the one with smallest start time? But since we are scanning in increasing j, and start time increases, the first encountered might have smaller start but not necessarily smaller ID. So we need to compare IDs. We'll loop over j from s to n-1, keep track of best j according to ID.
       - Then add selected_ids.append(sessions_sorted[j].id)
       - Update s = next[j]
       - Update target_val -= value_j
       - Update target_cnt -= 1
   - At the end, we have selected_ids in chronological order (since we always pick the first in start order each step). That yields the lexicographically smallest list.

But we need to confirm that this greedy indeed gives the lexicographically smallest list of IDs (sorted by start). Let's reason: The list is built by adding sessions in increasing start order. At each step, we choose the smallest possible ID that can be the next element (given that we must achieve the required remaining value and count from the suffix). Because the list is ordered by start, the choice of the first element determines the first ID; among all optimal solutions, the smallest possible first ID (by ID) leads to the lexicographically smallest list (since any list with a smaller first ID is lexicographically smaller regardless of the rest). So we choose the smallest ID among all sessions that can be the first element (i.e., there exists an optimal solution starting with that session). After fixing the first element, the remaining list (from the second element onward) must be the lexicographically smallest among all completions that achieve the remaining target (value, count) and that start after the first element's end. Again, by the same reasoning, we should pick the smallest possible second ID among those that can be the second element in some optimal completion. So the greedy works. Since the decision at each step is independent (the future doesn't affect the ID ordering of previous elements), it's optimal.

We must ensure that when we compute dp_val and dp_cnt, we do it on the start-sorted array. The recurrence we used (dp_val[i] = max(value_i + dp_val[next[i]], dp_val[i+1])) works correctly if the sessions are sorted by start time? Actually, classic weighted interval scheduling uses sorting by end time to ensure that when we consider i, all intervals that end before start_i (i.e., p(i)) are before i. But if we sort by start time, the intervals that end before start_i might be after i in the start-order? Because start order is not end order. For example, a session with early start but late end could be before an interval that starts later but ends earlier. The recurrence dp_val[i] = max(value_i + dp_val[next[i]], dp_val[i+1]) where next[i] is the first session with start >= end_i is valid only if we consider that all non-overlapping intervals before i can be independently chosen from intervals after i. But it's not sufficient because optimal solution from i might include intervals that start before i but end before start_i? However if we process from right to left and we consider i as the earliest start among remaining intervals, then all intervals that start before i are excluded because we are at i (they are earlier in start order). The classic DP for forward (starting from earliest) works if we consider intervals sorted by start time and define next as the first interval that starts after current ends. The recurrence dp[i] = max(value_i + dp[next[i]], dp[i+1]) yields the maximum value achievable from intervals from i to end (with i sorted by start). This is correct because if we take interval i, we cannot take any overlapping intervals (those that start before end_i); the earliest interval that can be taken after i is next[i]. And if we skip i, we consider dp[i+1] which considers the next interval (i+1) as potential start. This is standard forward DP (like from left to right in terms of start). It works as long as the intervals are sorted by start time. Let's test: Example: intervals: A(start=0,end=10,value=10), B(start=1,end=2,value=20), C(start=3,end=4,value=20). Sorted by start: A (0-10), B (1-2), C (3-4). DP from index 0: i=0. next[0] = first start >= 10? none, so 3 (n). include = 10; exclude = dp[1]. Now dp[1] will consider B and C. For i=1, next[1] = index of start >= 2 => C (index 2) so include=20+dp[2]=20+20=40, exclude=dp[2]=dp of C = max(value_C+dp[3],dp[3])=20; so dp[1]=40. Then dp[0] = max(10,40)=40. This yields optimal value 40 (B+C), which is correct. So forward DP with sort by start works. However, there is nuance: When we skip interval i, we go to i+1, but i+1 may start after end_i? Not necessarily; i+1 may still start before end_i (overlapping). In the example, after A (0-10), B (1-2) overlaps and start < end_A. But we can still skip A and take B and C. dp[i+1] considers starting from B, which is fine. So the recurrence works. Also note that next[i] is defined by start >= end_i, so for A, next would be the first with start >= end_A (10), which is none. So include A gives only A. The dp correctly captures that including A prevents taking any later intervals (since all later intervals have start < end_A? Actually B and C have start <10, so they overlap, so they are skipped. So including A gives 10, exclude gives 40. So works.

Thus, we can use start-sorted list for both DP and reconstruction, aligning with chronological order. This is convenient. Then the reconstructed list will naturally be in chronological order as we pick in increasing start order.

Now we need to compute next array using binary search on start times. Since we have list of starts array, for each end_i, we need first index where start >= end_i. We can use bisect_left from bisect module. That's O(log n) per i.

Now compute dp_val and dp_cnt from right to left.
Pseudo:
n = len(sessions_sorted)
dp_val = [0]*n + [0]  # dp_val[n] = 0
dp_cnt = [0]*n + [0]  # dp_cnt[n] = 0
next_arr = [n]*n  # next[i] computed before
for i in range(n-1, -1, -1):
    incl_val = sessions_sorted[i].value + dp_val[next_arr[i]]
    incl_cnt = 1 + dp_cnt[next_arr[i]]
    excl_val = dp_val[i+1]
    excl_cnt = dp_cnt[i+1]
    if incl_val > excl_val:
        dp_val[i] = incl_val; dp_cnt[i] = incl_cnt
    elif incl_val < excl_val:
        dp_val[i] = excl_val; dp_cnt[i] = excl_cnt
    else:
        # equal value
        if incl_cnt < excl_cnt:
            dp_val[i] = incl_val; dp_cnt[i] = incl_cnt
        elif incl_cnt > excl_cnt:
            dp_val[i] = excl_val; dp_cnt[i] = excl_cnt
        else:
            # equal value and count, for now we can pick either, but we need to ensure that the condition for include branch is still valid if we later rely on it. Since both have same value and count, whether we set dp_val[i] and dp_cnt[i] to include or exclude doesn't matter; both are true. However, we should be consistent with the conditions for candidate selection, which rely on comparing include branch to dp_val[i]. But if we set dp_val[i] to exclude branch value, then include may still equal that value and count, so condition still holds. So it's fine. But for tie-breaking on ID later, the DP which branch we store doesn't affect the existence of include branch. So we can arbitrarily choose, say exclude for determinism.
            dp_val[i] = excl_val; dp_cnt[i] = excl_cnt

Now we have V* = dp_val[0], C* = dp_cnt[0].

Now reconstruction:
s = 0
selected_ids = []
target_val = V*
target_cnt = C*
while s < n and target_cnt > 0:  # or target_val >0
    best_idx = None
    best_id = None
    for j in range(s, n):
        # Quick check: If dp_val[j] != target_val or dp_cnt[j] != target_cnt: continue
        if dp_val[j] != target_val or dp_cnt[j] != target_cnt:
            continue
        # Check include condition
        if sessions_sorted[j].value + dp_val[next_arr[j]] == target_val and 1 + dp_cnt[next_arr[j]] == target_cnt:
            if best_idx is None or sessions_sorted[j].id < best_id:
                best_idx = j
                best_id = sessions_sorted[j].id
                # Note: since IDs are unique, we could break after finding first? but we need smallest ID, so we must scan all.
                # However, we can break early if we find ID that is smallest possible? Not without scanning.
    if best_idx is None:
        # This should not happen if target is achievable
        break
    selected_ids.append(best_id)
    s = next_arr[best_idx]
    target_val -= sessions_sorted[best_idx].value
    target_cnt -= 1

This will produce the lexicographically smallest IDs list in chronological order.

Note: What about sessions with equal start time but different end? When sorting, we need a stable order that respects chronological order for list generation. We should sort by start, then end, then ID (maybe) to define total order. But the chronological order outputting IDs: The problem says "selected_ids in chronological order". It probably means the order in which sessions occur in time, i.e., by start time (and if start equal, by end). So sorting by start then end then ID is appropriate. Also, when constructing the list, we always add sessions in increasing start order. This yields chronological order.

Now, we must consider the case where there are no selected sessions (max value 0). In that case, we output empty selected_ids.

Now, regarding rejected sessions: We need to reject sessions where end <= start or value < 0. We'll parse and validate each session.

Edge Cases:
- Timestamp parsing: Use datetime.fromisoformat. But ensure it works for Python 3.7+. fromisoformat is available since 3.7. It can parse strings like "2026-05-01T09:00:00" without timezone. We'll use try/except; if fails, we reject with reason "invalid start" or "invalid end".

- We need to output JSON with exact format: {"max_value": V*, "selected_ids": [...], "rejected": [{"id":..., "reason":...}]}.

- Input may be a JSON object with "sessions" array.

- We'll parse JSON using json module.

Now, we must also implement built-in tests when run with `--test`. The test should execute some test cases and print a short success message. We can create test functions inside the program. Since we are to output only the code, we need to include tests.

Implementation Plan:

1. Import necessary modules: json, sys, datetime, bisect.
2. Define functions:
   - parse_timestamp(s): returns datetime or None.
   - validate_session(session): returns (valid, reason) tuple.
   - solve(sessions): main function that takes list of valid session dicts (or objects) and returns output dict (max_value, selected_ids, rejected). But we also need handle invalid inside solve? Better to separate: read input, for each session, validate, collect valid ones and rejected ones with reasons. Then run algorithm on valid ones.
3. Classes: Could define a namedtuple or simple class for session with id, start, end, value. But we can also use dicts. For performance, we can use simple objects with attributes.

Because we need to sort sessions and access attributes, a class or namedtuple is convenient. We'll use a simple class Session with __slots__ maybe.

4. Sorting: sessions_sorted = sorted(valid_sessions, key=lambda s: (s.start, s.end, s.id))   # s.start and s.end are datetime objects.

5. Compute next array: have a list of start times (list of datetime). Use bisect_left to find first index where start >= end_i.

6. DP suffix.

7. Reconstruction.

8. Output JSON.

9. If sys.argv[1] == '--test', run tests; else read stdin.

Testing: We'll include a few test cases within a function `run_tests()`. We'll use assert or raise to check outputs. Print success message if all pass.

Now, we must ensure code under 1000 lines. We'll write cleanly.

Potential pitfalls:
- The DP suffix uses dp_val[i+1]; need dp_val[n]=0.
- For next[i], we need to find first index with start >= end_i. Since end_i may be equal to some start, we should use >= to avoid overlap? If end_i equals start_j, they don't overlap (assuming closed intervals? The problem: start and end times, "non-overlapping" likely means that sessions cannot overlap in time; if one ends exactly when another starts, that's not overlapping. So we use >= for start_j >= end_i. So it's correct to use start >= end.
- When sessions have same start time, we need to ensure that if we include one, we cannot include another with same start because they overlap (start equals start? They overlap at least at start). So they are overlapping. Our next[i] for a session will include those with start >= end_i, so if start_j = start_i and end_j > start_i, they will not be in next[i] because start_j < end_i typically if end_i > start_i, so they overlap. So okay.
- If two sessions have same start and same end? Then they completely overlap, can't both be selected. Our next[i] would skip them if end_i <= start_j? Since start_j = start_i and end_i >= start_j? Actually start_j >= end_i would require start_i >= end_i, which is false because end_i > start_i. So they are overlapping. Okay.

- For sorting by start, then end, then ID, we need to define a key. But we can just use a tuple (start, end, id) because datetime objects are comparable. IDs are strings, comparable.

- The condition for candidate j: we check dp_val[j] == target_val and dp_cnt[j] == target_cnt. But note that dp_val[j] is the max value from j onward. For the suffix after we have selected some sessions, the new target_val and target_cnt are exactly dp_val[next[prev]] and dp_cnt[next[prev]] from the step. Since dp_val[next[prev]] is the max from that suffix, and we subtracted the same from global, target_val and target_cnt match the max of the suffix. So it's fine.

- But consider scenario where there are multiple ways to achieve same max value with different counts (but we always have min count). So dp_cnt[j] should be the minimal count achieving the max value. Our condition also checks 1+dp_cnt[next[j]] == target_cnt. That ensures that the include branch gives minimal count as well. So fine.

- What if there are sessions that have value=0? They should be considered in DP (they might increase count, but if we want minimize count, we might avoid zero-value sessions because they don't increase value but increase count. However, if all sessions have zero value, the max value is 0, and we would want the solution with fewest sessions? Actually, if value = 0, the max value is 0. The minimal count would be 0 (empty set). So we should not select any sessions with zero value, as they would just increase count without increasing value. Our DP will value them positively? No, value=0 gives no increase, so include branch: value_i+dp_val[next[i]] could be equal to exclude value (if dp_val[next[i]] also 0). For count, include count = 1+dp_cnt[next[i]], dp_cnt[i+1] (maybe 0). So include would have higher count, so exclude preferred. So zero-value sessions will not be selected. That's fine.

- If a session has negative value, we already reject.

Now, we must consider that the input may have sessions with value=0 and valid times; they may be selected if we need to fill? But we minimize count, so they won't be selected. However, if all sessions have value=0, the optimal solution is to select none. So our building loop with target_val == 0 and target_cnt > 0? But target_cnt will be 0 because dp_cnt[0] will be 0 (since we can achieve 0 with empty set). The reconstruction loop condition target_cnt > 0 will not run. So selected_ids empty. That's correct.

But careful: In DP, dp_cnt[i] includes the case where we achieve value 0 with 0 sessions (by taking dp[i+1] which may have 0). But what if there is a session with value 0? The include branch yields value 0 but count 1, which is not minimal; exclude yields 0 count. So dp_cnt stays 0. So global optimum has count 0. So reconstruction will not pick any session. So good.

Now, we need to handle large n efficiently: building replacement scan for each step could be O(n^2) if we linearly scan from s each step. In worst case, we might select O(n) sessions and each scan O(n) gives O(n^2). But we can improve by noticing that we only need to find the smallest ID among a suffix that satisfies the condition. The condition uses dp_val[j] == target_val and dp_cnt[j] == target_cnt. But these values change as we progress. However, note that as we move s forward, the target_val and target_cnt decrease. We could precompute for each possible value? Not easy.

We can optimize by scanning j from s to n-1, but we can break early if we know that no later j can have a smaller ID? Since IDs are arbitrary, we cannot break. But we can store a mapping from (dp_val, dp_cnt) to a list of indices sorted by ID? But target_val changes, and we need only current (target_val, target_cnt). We can precompute, for each index i, the best candidate (smallest ID) among j >= i that satisfies the two conditions (including the include condition) for each (target_val,target_cnt)? That would be many.

Given that n could be large, but the reconstruction loop would be O(n) if we do linear scan per step, leading to O(n^2) in worst case. But we can do a smarter scan by iterating j from s onwards and only break when we have a candidate and further j cannot have a smaller ID? Without ordering of IDs, we can't. However, we can precompute for each index i the information needed to quickly find the smallest ID candidate for given target_val and target_cnt? Not obviously.

Alternative: Instead of reconstructing with scanning, we can do a recursive greedy that determines the next element by examining candidates in order of ID? But we need to verify feasibility for each candidate in increasing ID order. Since IDs are strings, we could sort indices (valid sessions) by ID and try them in that order, but we must ensure they are in the eligible range (j >= s) and also satisfy conditions. So we could pre-sort all sessions (with their indices) by ID. Then for each step, we iterate over sessions in increasing ID order and check if its index >= s and conditions hold. If yes, we pick it. This avoids scanning from s each time. But we need to quickly check if a given index is >= s and conditions hold. We can maintain a pointer for ID-sorted list. But each step we may need to scan ID-sorted list from beginning until we find an eligible candidate with index >= s and conditions. That could also be O(n^2) in worst case if many candidates fail. However, we can combine: Since s moves forward (increasing), and conditions (dp_val[j] == target_val, etc.) become more restrictive; we could precompute for each possible (value, count) a list of indices satisfying the condition, sorted by ID. The target_val and target_cnt are decreasing, but there are at most n distinct values? Actually values are integers (could be large). But we can still precompute maps: For each index j, we can compute the state (val_contrib, cnt_contrib) = (value_j + dp_val[next[j]], 1+dp_cnt[next[j]]) and we want these to equal (dp_val[j], dp_cnt[j]) (as in include condition). Together with requirement dp_val[j] == target_val and dp_cnt[j] == target_cnt, we need indices where dp_val[j] = target_val and dp_cnt[j] = target_cnt and (value_j + dp_val[next[j]], 1+dp_cnt[next[j]]) = (dp_val[j], dp_cnt[j]). So for each (val, cnt), we can have a list of indices that satisfy the full condition (i.e., j is an eligible first element for the suffix where target is (val,cnt)). But note that the condition for being an eligible first element for a suffix with target (val,cnt) is exactly: dp_val[j] == val, dp_cnt[j] == cnt, and the include condition. So we can precompute, for each index j, whether it is "eligible as first" for its own dp_val[j], dp_cnt[j]. Then during reconstruction, after we have target_val = val, target_cnt = cnt, we need to find among indices j >= s that have dp_val[j]==val and dp_cnt[j]==cnt and eligible flag true, the one with smallest ID. Since s increases, we can, for each (val, cnt), pre-sort the eligible indices by ID, and then maintain a pointer to the first index >= s with ID smallest? But we need to consider both condition (index >= s). If we have a list sorted by ID, we can't filter by index >= s efficiently without scanning. But we can also pre-store the indices in increasing order of index (which is also start order). We can then, for a given s, find the first eligible index j >= s with the required val,cnt. Since we want the smallest ID, we need to consider all eligible j >= s and pick min ID. If we have a list of eligible indices for each (val,cnt) sorted by index, we can binary search for first j >= s, and then we need to find among all from that point the smallest ID. That's not directly sorted by ID. We could instead store for each (val,cnt) a list of eligible indices sorted by ID. Then we need to ensure that the chosen index is >= s. We can iterate the ID-sorted list until we find one with index >= s. Since we process steps, s increases, so we can skip previous ones. But still linear scanning per step could be O(n^2) if many ineligible by index.

But note: the number of steps (selected sessions) is at most n. In worst case, if we have linear scan per step over all n sessions, it's O(n^2). For n=10^5, it might be too slow. But we can optimize: In the scanning from s to n-1, we could break early if we can determine that no later session can have a smaller ID than the current best we have found? Since IDs are not ordered by index, we can't break. But we can use a data structure that returns the minimum ID among sessions in a range that satisfy condition. For a fixed (val,cnt) (which changes each step), we can precompute an array of booleans indicating eligible for that (val,cnt)? That's too many.

Given the code should be under 1000 lines and likely for a smaller dataset, we could accept O(n^2) reconstruction. But the prompt says "include an efficient O(n log n) dynamic programming solution." That specifically refers to the DP. Reconstruction tie-breaking might be considered separate. However, we can attempt to make reconstruction also O(n log n) by using a segment tree or something but that would be complex. Let's consider typical solutions to weighted interval scheduling with lexicographic tie-breaking: often they just do the DP and then reconstruct with tie-breaking on IDs using a custom comparator that compares the list of IDs by walking pointers, but that is still O(n^2) in worst-case. But many online solutions for similar problems (e.g., maximizing value, then minimizing number of intervals, then lexicographically smallest set) use a similar greedy on sorted intervals and check DP values, and scanning each step linearly from start index is typical. If n is up to 10^4, it's okay. I'll keep the linear scan for simplicity.

But we can make it O(n log n) by precomputing for each index i the "next eligible" for each dp_val? Not necessary. Let's stick with linear scan, but note that the loop for each step might be O(n^2) worst-case. However, we can try to reduce the scanning: since we are scanning from j = s to n-1 each time, and s increases monotonically, the total loops across all steps could be O(n^2) if in each step we scan many candidates before finding one. In the worst-case, suppose only one session is selected, and we scan all n to find it. That's O(n) per step, but steps are few. If many sessions selected, each step may scan a small portion because s jumps to next[j] which is often significantly greater. In worst-case, if all sessions are very short and can all be selected, then s increases by 1 each step, and we will scan from s to n each step, resulting in O(n^2). For example, intervals of length zero? But intervals cannot have end <= start. So they must have positive length. However, if intervals are non-overlapping and sorted by start, next[i] = i+1 if each ends before next starts. In that case, we would select many sessions, and each step we scan from current s to find the smallest ID eligible. Since conditions might be such that all sessions in the suffix are eligible for the current target? Not necessarily. But worst-case could still be O(n^2). But we can optimize by precomputation: For each index i, we can compute the smallest ID among eligible j >= i (with include condition and dp_val == target_val?) But target changes. Not easy.

Given the constraints of the problem (likely not huge), I'll go with linear scan per step. But we can still make it more efficient by avoiding scanning from s each time if we can break early when we find a candidate and we know that all later indices have larger ID? Not guaranteed. But we can pre-sort indices by ID and then for each step iterate over all indices in ID order, checking index >= s and conditions. That would scan all n each step again.

Maybe we can compute the lexicographically smallest list directly from DP decisions with tie-breaking by count and ID. Could we incorporate ID comparison into the DP in O(1) per comparison using something like "lexicographic ordering can be reduced to comparing the smallest ID that can be selected"? Not straightforward.

I think it's acceptable to use the greedy method with linear scan. We'll note that we need O(n log n) for sorting and DP, reconstruction could be O(n^2) but we'll try to keep it efficient.

Alternatively, we can implement reconstruction by iterating j from s to n and selecting the first that satisfies the condition, but that would not guarantee smallest ID; we need smallest ID, not first in start order. So we need to scan all.

But we can do: For each step, we can precompute, for each possible target (val, cnt), the list of eligible indices (those satisfying include condition and dp_val==val and dp_cnt==cnt) sorted by ID. Then we can, for the current s, find the first element in that sorted ID list whose index >= s. Since the list is sorted by ID, we can binary search for the smallest ID that also has index >= s? But we need the smallest ID, so we want the first element in the list that also has index >= s. Since the list is sorted by ID, we can iterate from start until we find one with index >= s, and that will be the smallest ID. Because if we skip elements because index < s, they are invalid now, but later they may become valid? No, s increases, so indices less than s are permanently excluded. So we can maintain for each (val,cnt) a pointer into the ID-sorted list that we advance as s increases. Then per step, we just look at the current pointer's element (which has the smallest ID among the list) and check if its index >= s; if not, we advance pointer until we find one with index >= s (or exhaust list). This yields O(n) total across all steps because each pointer advances at most n times. Perfect. Since there can be many (val,cnt) pairs, but we can note that only a few pairs will be encountered as target (val,cnt) in the reconstruction. The target (val,cnt) passes through a decreasing sequence of at most n steps. So we could compute on the fly.

Implement:

- For each index j, we compute its "eligible" status: `eligible_include[j] = (sessions_sorted[j].value + dp_val[next_arr[j]] == dp_val[j] and 1 + dp_cnt[next_arr[j]] == dp_cnt[j])`. This means that including session j is a way to achieve dp_val[j] and dp_cnt[j] (optimal from j). Also note that for a session to be candidate for the first element of a suffix with target (val,cnt) = (dp_val[j], dp_cnt[j]), it must satisfy `eligible_include[j]`. Also, we require that dp_val[j] == target_val and dp_cnt[j] == target_cnt. So the set of eligible indices for a particular (val,cnt) is: {j | dp_val[j]==val and dp_cnt[j]==cnt and eligible_include[j]}. So we can group indices by (val,cnt) pairs. Since val and cnt can be many but at most n distinct pairs (each index has its own dp_val, dp_cnt). In worst case, each index could have different (val,cnt). So groups size small.

- During reconstruction, we will have a current target (target_val, target_cnt) which is exactly dp_val[s] and dp_cnt[s] at the beginning? Actually after each step, target_val and target_cnt become the dp_val[next[prev]] and dp_cnt[next[prev]] which are the optimum for the suffix. That suffix optimum matches dp_val[s] for some s. So we can use s as a pointer. But we need to find the smallest ID among indices j >= s with dp_val[j] == target_val and dp_cnt[j] == target_cnt and eligible_include[j]. And note that target_val and target_cnt are exactly dp_val[s] and dp_cnt[s] initially. So we can start with s=0, target_val=dp_val[0], target_cnt=dp_cnt[0]. Then at each step, we need to find the smallest ID j in the set {j >= s | dp_val[j]==target_val and dp_cnt[j]==target_cnt and eligible_include[j]}. Since we know that s itself satisfies this? Not necessarily, because s might not be eligible_include (i.e., include branch may not be optimal for s). We need to scan.

- We can pre-group indices by (dp_val, dp_cnt) pairs. For each distinct pair (V,C), we have a list of indices (the j's) that have dp_val[j]==V and dp_cnt[j]==C. Among these, we also require eligible_include[j]. So we can store for each (V,C) a list of (index, id) sorted by index (or ID). We need to support query: given s, find the element with smallest ID among those with index >= s. If we have this list sorted by ID, we can do as described: maintain a pointer per (V,C) into the ID-sorted list, advancing when index < s. Since s increases, pointer advances monotonic. The total number of advances across all steps is O(n). So we can achieve O(n log n) preprocessing (sorting per group) and O(n log n) overall reconstruction (due to binary search for next). But we need to quickly get the (V,C) group for current target. We can store a dictionary mapping (V,C) pair to the sorted list (by ID) of indices that are eligible. During reconstruction, target (V,C) will be one of the pairs present (since we always have at least one index, because we know there is an optimal solution). So we can retrieve the list for that (V,C) and use a pointer that we advance as s increases. However, we need to perform this for each step, and each step we will advance the pointer as needed until we find an index >= s. The pointer might already be behind s, so we move it forward. Since each element in the list (all lists combined) is advanced at most once, total O(n). So reconstruction becomes O(n) plus binary searches for next array per step (already done). This is efficient.

But we must also ensure that the list for (V,C) is sorted by ID. For each distinct (V,C), we can collect eligible indices (those where dp_val==V, dp_cnt==C and eligible_include true). Sort them by ID (and maybe also by ID then index). Then we can create an interator pointer. Since s increases monotonically, we can pop from the front? We'll maintain an index pointer that moves forward.

Let's design:

- We'll create a dict `groups` mapping (val, cnt) to a list of tuples (id, idx) sorted by id ascending. Actually we want the smallest ID among those with idx >= s. If we have list sorted by ID, we can iterate from start and skip those with idx < s. To avoid O(scan) per query, we can for each group store two arrays: one of ids sorted, one of indices correspondingly. Then we maintain a pointer p per group that indicates the first candidate in the list that we haven't yet considered (i.e., all earlier are rejected because idx < s). But s changes each step, so we may need to re-scan from current pointer, but we can advance p until candidate's idx >= s. Since s only increases and we only go forward in the list, total pointer moves across all steps for that group is length of list. So we can do that per step. This yields O(1) amortized per step for pointer advancement (since each candidate is examined once). So overall O(n) across steps.

Implementation:

- Initialize dict: group_to_candidates = {}  # key: (val, cnt) -> list of (id, idx) sorted by id.
- For each index j in range(n):
    if not eligible_include[j]: continue
    key = (dp_val[j], dp_cnt[j])
    # note: j may have dp_val, dp_cnt unique but can share key with others.
    group_to_candidates.setdefault(key, []).append( (sessions_sorted[j].id, j) )
- After loop, for each key, sort the list by id (lexicographic).
- Also, for each key, we will maintain a pointer in the reconstruction, but since reconstruction is done per step, we can keep a dict `group_pointers` that maps key to current index in the sorted list.

Reconstruction:

- s = 0
- selected_ids = []
- target_val = dp_val[0]; target_cnt = dp_cnt[0]  # (V*, C*)
- While target_cnt > 0 (or target_val > 0 maybe):
    key = (target_val, target_cnt)
    candidates = group_to_candidates.get(key, [])
    # Get pointer for this key; initialize if not exist (pointer = 0)
    ptr = group_pointers.get(key, 0)
    # Advance ptr while ptr < len(candidates) and candidates[ptr][1] < s: ptr++
    while ptr < len(candidates) and candidates[ptr][1] < s:
        ptr += 1
    if ptr >= len(candidates):
        # No candidate? Should not happen if target is achievable.
        break
    best_id, best_idx = candidates[ptr]
    # Since list sorted by ID, the first with idx >= s is the smallest ID overall among those with idx >= s (because list sorted by ID)
    selected_ids.append(best_id)
    s = next_arr[best_idx]
    target_val -= sessions_sorted[best_idx].value
    target_cnt -= 1
    # Update pointer for this key for future use (since we may reuse same key again, but after we decrease target_val, the key changes, so this key is not used again. Actually target changes each step, so each key is used at most once. So we don't need persistent pointers per key across steps? Wait: we might have same key multiple times if target_val and target_cnt stay same after subtracting? No, because target_val and target_cnt strictly decrease (v values positive). So each (target_val, target_cnt) pair appears at most once. So we don't need to update pointers for keys across steps; we can just compute the first eligible index >= s for the given key by scanning the sorted list from beginning until we find index >= s. Since the key appears only once, the total scanning for that key will be at most the size of its list. That can still be O(n) per key, but sum over all keys may be O(n^2) if we scan from start each time. However, we can store the pointer per key and reuse across steps? But key changes, so no reuse. So if we for each step we scan the candidates list from beginning until we find index >= s, that could be O(n) per step (worst-case each list size O(n)). In the worst-case, if all indices belong to the same key, each step we would scan from start skipping many indices that are < s (which grow). That would be O(n^2). But we can maintain a pointer per key across the whole reconstruction (even though key changes, we don't revisit same key). So each key's list is scanned only once during its step, but we may scan it fully if we start from beginning and advance until we find index >= s. If the list is sorted by ID, the indices are not in order; we cannot guarantee that we can avoid scanning all previous elements because they might be < s or >= s. The condition index >= s is not monotonic with ID ordering. So to find the first (smallest ID) with index >= s, we would have to scan the entire list (sorted by ID) until we find any element with idx >= s. That could be O(m) for each key, total O(n^2) if many elements per key. However, we can sort the candidates list by index (instead of ID) for the purpose of fast retrieval of smallest ID with index >= s? That's not directly possible because we need smallest ID, not smallest index. But we could preprocess for each key: create a data structure that for a given s returns the minimum ID among indices >= s. This can be done by sorting candidates by index and then precomputing a suffix-min- ID. Since s moves forward (monotonic), we can have an array sorted by index and maintain pointer. Let's design:

For each key, we have a list of eligible indices j with their ID and index (j). We want to answer queries: given s (starting index for step), find the candidate with the smallest ID among those with index >= s. Since s is monotonic (increasing) across steps, we can sort the candidates by index (ascending) and precompute an array of suffix minimum ID (and corresponding index). Then for a given s, we can binary search (or use pointer) to find the first candidate with index >= s, and then the suffix minimum from that point gives smallest ID among all candidates with index >= s. This is O(log m) per query if binary search, or O(1) amortized if pointer moves. Since s increases, we can maintain a pointer into the index-sorted list. For each step with key K, we will:
- Get the index-sorted list for K (sorted by j).
- Initialize a pointer p for K (starting at 0) and a suffix-min array precomputed.
- Then for query with s, we advance p until candidates[p].index >= s (since s increases, p monotonic). Then the smallest ID among remaining is given by suffix_min[p]. So we get candidate in O(1) amortized.

We need to precompute for each key the list of (index, id) sorted by index. Then compute suffix_min_id[i] = min(id from i to end) (lexicographic min). We'll also store suffix_min_idx[i] to retrieve which index gives that id. But careful: If two IDs are identical? Assume unique, but if not, we need consistent tie-breaking: choose the one with smallest index? Actually we want the smallest ID; if multiple with same ID (unlikely), we need to pick the one with smallest ID; but if same ID, then we need to ensure that when we later pick it, the reconstruction still works? However, since IDs are unique (likely), we can ignore.

Thus, reconstruction algorithm per step:

- key = (target_val, target_cnt)
- Retrieve the structure for key: a list `cand_indices` sorted by index, and `suffix_min_id` and `suffix_min_idx` (or we can store the id for each entry and then track min). We also maintain a pointer `p` for this key that we advance from last position (since s increases). We'll store these structures outside the loop, and also store such pointer for each key (initialize pointer to 0). Since each key is used only once, we can just compute the answer quickly using binary search on index array and then suffix min. Since number of keys <= n, binary search per step O(log n) would be fine. But we also need to ensure that we get the correct minimum ID; binary search gives first index >= s, then we use precomputed suffix min ID from that point. This gives smallest ID among those with index >= s (since suffix min takes min over all later indices). That yields the smallest ID in O(log m) per step. Since total steps <= n, total O(n log n). That's acceptable.

Simpler: we can precompute for each key a list of (index, id) sorted by index, and also an array of suffix min id (and corresponding index). Then during reconstruction, for each step we do binary search to find leftmost index >= s, then look up suffix_min_id at that position. If no such index, break (shouldn't happen). This is O(log n) per step, total O(n log n). This is good and avoids O(n^2).

Thus, modify reconstruction:

- Preprocess eligible_include for each j.
- Build dict `groups` mapping (val, cnt) -> list of (index, id) sorted by index. (We'll only include indices where eligible_include is true.)
- Then for each key, after sorting by index, compute suffix_min_id array: suffix_min[i] = min(id from i to end) (lexicographic min). Since we need the corresponding index for later (to get next and value), we also store the index where the min id occurs. Actually we need to retrieve the index j that gives the min ID. So we can store an array `suffix_best_index[i]` = the index of the best (smallest id) candidate from i onward. Because IDs are unique, we can determine which index gives the min ID. Then for a given s, we binary search for the first i where index >= s, then use suffix_best_index[i] to get the j for candidate, and also its id. This gives the smallest ID among eligible indices with index >= s, because the suffix min takes min over all later indices (in index order, not ID order). But is it correct that the smallest ID among all eligible indices with index >= s appears as the minimum ID over a suffix of the index-sorted list? Since the list is sorted by index, not ID, the suffix of index-sorted list includes all candidates with index >= some value, but not necessarily all? All candidates with index >= s are included from the first index >= s onward because list sorted by index. So the set of candidates with index >= s corresponds exactly to a contiguous suffix of the index-sorted list (starting at first index >= s). So we can compute the minimum ID over that suffix by scanning all elements from that point. That suffix min can be precomputed. So yes, we can get the smallest ID among those with index >= s as the suffix min from that point. So that works.

Therefore, steps:

- Compute eligible_include array.
- Build groups: dict key -> list of (idx, id) sorted by idx.
- For each key, compute suffix_min_id array: e.g., for i from len(list)-1 down to 0: best_id = min(current_id, best_id_so_far) and store best_idx? Actually we need to store the index (j) of the best id. Since IDs could tie, we need tie-breaking: if same ID, pick the one with larger index? Not needed but we can just store the first (smallest index) for stability. But we'll store both.

Pseudo:
for key, lst in groups.items():
    lst.sort(key=lambda x: x[0])  # sort by index
    m = len(lst)
    suffix_min_id = [None]*m
    suffix_min_idx = [None]*m
    best_id = None
    best_idx = None
    for i in range(m-1, -1, -1):
        idx, id_ = lst[i]
        if best_id is None or id_ < best_id:
            best_id = id_
            best_idx = idx
        suffix_min_id[i] = best_id
        suffix_min_idx[i] = best_idx

Now, in reconstruction:
- s = 0
- target_val, target_cnt = dp_val[0], dp_cnt[0]
- selected_ids = []
- While target_cnt > 0: (since when target_cnt=0 we are done)
    key = (target_val, target_cnt)
    if key not in groups:
        break # should not
    lst_index = groups[key]  # list of (idx, id) sorted by idx
    # Need to find the first index where idx >= s. Use binary search on lst_index based on idx.
    # Since lst_index is sorted by index, we can use bisect_left on a list of indices.
    # We can pre-extract the list of indices: idx_list = [item[0] for item in lst_index] but we already have lst_index as list of tuples. We can create a separate list of indices for binary search if needed. But we can just use custom binary search on the tuple's first element.
    # Compute i = first position with idx >= s; using bisect_left: we need a list of indices. So we can store idx_list = [idx for idx, id_ in lst_index].
    import bisect
    idx_list = groups_idx[key]  # precompute
    i = bisect.bisect_left(idx_list, s)
    if i == len(idx_list):
        # shouldn't happen
        break
    best_id = suffix_min_id[key][i]  # precomputed array for this key
    # But we need also the corresponding index for that best_id. However, suffix_min_idx[i] gives the index (idx) of the best candidate from i onward. That's the j we want.
    best_idx = suffix_min_idx[key][i]  # note that this best_idx may not correspond to the same as i? It's the index of the candidate with smallest id among those with idx >= s.
    # Now we can add.
    selected_ids.append(best_id)
    # Update: s = next_arr[best_idx]
    s = next_arr[best_idx]
    target_val -= sessions_sorted[best_idx].value
    target_cnt -= 1

But careful: We need to ensure that the candidate we pick (best_idx) indeed satisfies eligible_include and dp_val==target_val etc. Since we built groups only for eligible_include with that dp_val,cnt, it does. Also we need to ensure that after picking best_idx, the remaining suffix (starting at next_arr[best_idx]) can still achieve the new target. By definition of eligible_include, we have value_i + dp_val[next_arr[i]] == dp_val[i] and 1+dp_cnt[next_arr[i]] == dp_cnt[i]. Since dp_val[i] == target_val, new target_val = target_val - value_i = dp_val[next_arr[i]], similarly new target_cnt = dp_cnt[next_arr[i]]. So it's consistent. However, note that we are using the smallest ID among all eligible indices with idx >= s. But we must also ensure that after picking that candidate, the remaining solution (from next_arr[best_idx]) is still achievable with target values. The eligibility condition already guarantees that there exists at least one optimal completion from next_arr[best_idx] (namely the DP solution that achieves dp_val[next_arr[best_idx]] and dp_cnt[next_arr[best_idx]]). But we also must ensure that when we later reconstruct the remainder, we use the same greedy to pick the next smallest ID; since we will continue with the same greedy method on the remainder, it should produce the lexicographically smallest completion for that suffix. However, we must be careful: The greedy choice of the first element (smallest ID among eligible for current target) is correct only if the remaining problem has an optimal solution that uses the chosen candidate as first element. Since we picked a candidate based solely on it being eligible (i.e., there exists some optimal solution starting with it), and it has the smallest ID among all such eligible candidates, then the overall list will have its first ID as small as possible. After fixing that, we recursively need the lexicographically smallest completion for the suffix. Since we will apply the same algorithm to the suffix (starting at next[best_idx]), and that suffix's optimal (value,cnt) matches target values, it will produce the smallest IDs for that suffix. This yields overall lexicographically smallest. So it works.

One nuance: What if there are multiple optimal solutions for the suffix that yield the same (target_val,target_cnt) and start with different IDs? The greedy will pick the smallest ID for the suffix as well. So it produces lexicographically smallest continuation. So the overall list is lexicographically smallest.

Thus, reconstruction using groups with precomputed suffix min IDs is efficient.

Now we need to compute eligible_include. For each i, eligible_include[i] = (sessions_sorted[i].value + dp_val[next_arr[i]] == dp_val[i]) and (1 + dp_cnt[next_arr[i]] == dp_cnt[i]). Note: This condition may be true even if dp_val[i] is achieved by include branch. If include and exclude have same value and count, then include may still be true (if value_i + dp_val[next[i]] == dp_val[i] and 1+dp_cnt[next[i]] == dp_cnt[i]), because both give same value and count. So it's fine.

Now, we must ensure we compute dp_val and dp_cnt correctly. dp_val[i] defined for i from 0 to n-1, with dp_val[n]=0. dp_cnt[n]=0. For i from n-1 to 0:
 incl_val = value_i + dp_val[next_i]
 incl_cnt = 1 + dp_cnt[next_i]
 excl_val = dp_val[i+1]
 excl_cnt = dp_cnt[i+1]
 if incl_val > excl_val: pick include
 elif incl_val < excl_val: pick exclude
 else: # equal value
   if incl_cnt < excl_cnt: pick include (smaller count)
   elif incl_cnt > excl_cnt: pick exclude
   else: # equal count, pick either (let's pick exclude for determinism)
        dp_val[i]=excl_val; dp_cnt[i]=excl_cnt

Now, dp_val[i] and dp_cnt[i] represent the best (max value, min count) from i onward.

One more check: For the DP to be correct, we need that the solution from i onward can include sessions that start before end_i but after start_i? No, because we defined next[i] as the first session with start >= end_i. So when we include i, we must exclude all sessions that start before end_i. The recurrence assumes that the optimal solution from i (if include i) is value_i + optimal solution from next[i] (the first non-overlapping). This is valid because any session with start < end_i overlaps with i, so cannot be taken if i is taken. So the optimal solution from i, if it includes i, must consist of i and an optimal solution from the set of sessions that start after end_i. Those are exactly from next[i] onward because sessions are sorted by start. Also, if we skip i, we consider solution from i+1 which may include sessions that start before end_i (overlapping i) but that's fine. So recurrence works.

Now, we also need to compute next array. Use bisect_left on list of start times (list of datetime objects). Let start_times = [s.start for s in sessions_sorted]. For each i, end_i = s.end. next_i = bisect_left(start_times, end_i)  # returns first index where start >= end_i. Could be n if no such.

Time: O(n log n) for sorting and binary searches.

Now, we should also handle the case where there are no valid sessions (all rejected). Then we output max_value=0, selected_ids=[], rejected=all. Also, dp and reconstruction would be empty. So we need to handle early.

Implementation Steps in Code:

1. Imports: json, sys, datetime, bisect, functools? Not needed.

2. Define parse_iso(s):
   try:
       dt = datetime.datetime.fromisoformat(s)
       # Ensure no timezone info? We'll accept naive. But fromisoformat returns offset-aware if timezone present; we want naive. We can check if dt.tzinfo is not None then reject? Problem says "without time zones". So we should reject strings with timezone. But fromisoformat will parse e.g., "2026-05-01T09:00:00+00:00" and return a datetime with tzinfo. We'll check and reject.
       if dt.tzinfo is not None: return None (or raise)
       return dt
   except: return None

But for datetime.fromisoformat, in Python 3.7 it doesn't support parsing "2026-05-01T09:00:00" if there is no timezone? It does. It supports only YYYY-MM-DDTHH:MM:SS and YYYY-MM-DDTHH:MM:SS.ffffff. It might not support other formats like YYYY-MM-DDTHH:MM:SS.fff? Actually it does. We'll just try. If fails, reject.

We'll also allow "T" separator only.

3. Read input: data = json.load(sys.stdin). sessions = data.get("sessions", []).

4. For each session dict, extract id, start, end, value. Validate:
   - id present (maybe not needed but assume)
   - start and end strings can be parsed to datetime.
   - end > start (strictly after)
   - value >= 0 (non-negative)
   If any violation, add to rejected list with reason. Reasons: "invalid start timestamp", "invalid end timestamp", "end must be after start", "value must be non-negative". Also if missing fields? We can assume complete or reject.

5. For valid sessions, we create list of Session objects (namedtuple or class). Use simple class with __init__ or namedtuple. I'll use a class with __slots__ for performance: id (str), start (datetime), end (datetime), value (int/float). But value is integer? Could be float? From example, 5, likely integer. We'll support int/float.

6. If no valid sessions: output max_value=0, selected_ids=[], rejected list with all.

7. Else: sort valid_sessions by (start, end, id). Use key = lambda s: (s.start, s.end, s.id).

8. Compute n = len(sessions).
   start_times = [s.start for s in sessions]
   end_times = [s.end for s in sessions] # we can compute on fly
   next_arr = [0]*n
   for i in range(n):
        next_arr[i] = bisect.bisect_left(start_times, sessions[i].end)  # returns first index with start >= end_i

9. DP arrays: dp_val = [0]*(n+1) ; dp_cnt = [0]*(n+1)  # index n is sentinel
   Loop i from n-1 down to 0:
        incl_val = sessions[i].value + dp_val[next_arr[i]]
        incl_cnt = 1 + dp_cnt[next_arr[i]]
        excl_val = dp_val[i+1]
        excl_cnt = dp_cnt[i+1]
        if incl_val > excl_val:
            dp_val[i], dp_cnt[i] = incl_val, incl_cnt
        elif incl_val < excl_val:
            dp_val[i], dp_cnt[i] = excl_val, excl_cnt
        else:
            if incl_cnt < excl_cnt:
                dp_val[i], dp_cnt[i] = incl_val, incl_cnt
            else: # incl_cnt >= excl_cnt  (if equal, we choose exclude or include? let's choose exclude for determinism)
                dp_val[i], dp_cnt[i] = excl_val, excl_cnt

10. Compute global_V, global_C = dp_val[0], dp_cnt[0]

11. Compute eligible_include array (list of bool len n):
        eligible = [False]*n
        for i in range(n):
            if dp_val[i] == sessions[i].value + dp_val[next_arr[i]] and dp_cnt[i] == 1 + dp_cnt[next_arr[i]]:
                eligible[i] = True

12. Build groups: dict groups = {} where key = (val, cnt) -> list of (idx, id) for indices where eligible[i] true.
        for i in range(n):
            if eligible[i]:
                key = (dp_val[i], dp_cnt[i])
                groups.setdefault(key, []).append( (i, sessions[i].id) )

    For each key, sort list by index (i). Also compute suffix_min_id and suffix_min_idx arrays. We'll store them in dict structures: groups_idx[key] = list of indices; groups_suffix_min_id[key] = list; groups_suffix_min_idx[key] = list.
    Alternative: store a list of tuples (idx, id) sorted by idx, then compute suffix arrays.

   Implementation:
        groups_data = {}  # key -> lst of (idx, id) sorted by idx
        for key, lst in groups.items():
            lst.sort(key=lambda x: x[0])  # sort by index
            m = len(lst)
            suffix_min_id = [None]*m
            suffix_min_idx = [None]*m
            best_id = None
            best_idx = None
            for i in range(m-1, -1, -1):
                idx, id_ = lst[i]
                if best_id is None or id_ < best_id:
                    best_id = id_
                    best_idx = idx
                suffix_min_id[i] = best_id
                suffix_min_idx[i] = best_idx
            groups_data[key] = {
                'indices': [item[0] for item in lst],  # for binary search
                'suffix_min_id': suffix_min_id,
                'suffix_min_idx': suffix_min_idx
            }

    groups_keys for direct lookup.

13. Reconstruction:

        s = 0
        target_val = global_V
        target_cnt = global_C
        selected_ids = []
        while target_cnt > 0:  # could also run while s < n and target_val > 0
            key = (target_val, target_cnt)
            if key not in groups_data:
                # should not happen
                break
            data = groups_data[key]
            idx_list = data['indices']
            # binary search for first index >= s
            i = bisect.bisect_left(idx_list, s)
            if i == len(idx_list):
                break
            best_idx = data['suffix_min_idx'][i]
            best_id = data['suffix_min_id'][i]
            selected_ids.append(best_id)
            # Update
            s = next_arr[best_idx]
            target_val -= sessions[best_idx].value
            target_cnt -= 1
        # If global_V==0 and global_cnt==0, loop doesn't run; selected_ids stays [].

14. Output JSON:
   output = {"max_value": global_V, "selected_ids": selected_ids, "rejected": rejected_list}
   print(json.dumps(output, indent=??? The problem doesn't specify formatting. We'll use compact or default? They said "Output JSON". We can use json.dumps with default separators. No need for pretty print.

But note: rejected list should be built from invalid sessions. We must store reasons.

Now, we need to ensure that global_V could be int or float; output number.

Important: The problem says "value" may be integer. We'll treat as numeric.

Now about tests: We'll include a function run_tests() that runs some test cases.

Testing approach: We'll encode test cases as input JSON, run the solve function (or the main program logic) and check output.

Test cases:

1. Basic:
   Input: {"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}]}
   Output: max_value=5, selected_ids=["a"], rejected=[]
2. Overlap two sessions with different values:
   sessions: a: 9-10 value 10; b: 9:30-11 value 20. Optimal should include b only (value 20). selected_ids=["b"].
   but check chronology: sorted by start: a (9-10), b (9:30-11). DP: next[a] = index of first start >= end_a (10:00) -> b? start_b=9:30 <10:00 so not; none. So include a=10, exclude a = max(b: 20,0)=20 -> pick b. So dp_val[0]=20, dp_cnt=1. eligible_include? For b: incl = 20 + 0 =20 = dp_val[1], count=1 matches; eligible true. For a: include = 10 !=20, eligible false. So groups: key(20,1) -> (b index, id "b"). reconstruction: s=0, target (20,1). idx_list for key: [1]; i=0; best_idx=1; add "b"; s = next[1] (none=2); target_val=0; loop ends. selected_ids=["b"].
3. Tie in value but not in count:
   a: 9-10 value 10; b: 10-11 value 10. Both non-overlap if a ends at 10, b starts at 10 (end not after start? b start=10, a end=10 => no overlap). So we can select both. Value total 20, count 2. Could also select only one? But DP will prefer two because value higher (20). So optimal value=20, count=2. In tie-breaking count same? No, but we need fewer sessions only if value equal. So not relevant.
   For tie-breaking sessions, consider:
   sessions: a: 9-10 value 5; b: 10-11 value 5; c: 9:30-10:30 value 5. All values=5. Opt total value? Options: {a,b} value=10 count=2; {c} value=5 count=1; {} value=0. So max=10 with a,b count=2 (cannot get higher). So optimal value=10, count=2. But there may be other combos that yield 10? maybe a,c? but c overlaps a, so no. So a,b is unique.
   For lexicographic, consider tie: two different sets with same value and count. Example: sessions with same start, different IDs. We'll test.
4. Test rejected: end before start, negative value, invalid timestamp.
5. Test lexicographic: Suppose we have two optimal solutions with value=10, count=2. Sessions:
   option1: sessions ["x","y"] (IDs) with times: maybe x:9-10 (value 5), y:10-11 (value 5)
   option2: sessions ["a","z"] with same thing but IDs "a","z". Since "a" < "x", option2 should be chosen.
   We'll assemble such test: sessions:
    {id:"x", start:"2026-05-01T09:00:00", end:"2026-05-01T10:00:00", value:5},
    {id:"y", start:"2026-05-01T10:00:00", end:"2026-05-01T11:00:00", value:5},
    {id:"a", start:"2026-05-01T09:00:00", end:"2026-05-01T10:00:00", value:5}, (same times as x)
    {id:"z", start:"2026-05-01T10:00:00", end:"2026-05-01T11:00:00", value:5}
   But note that there are overlapping intervals (x and a) same start/end; they cannot both be selected. So we can only pick one from first slot and one from second slot. So optimal solutions: pick (x,y) or (x,z) or (a,y) or (a,z). All have value=10,count=2. Lexicographically smallest list of IDs (sorted by start): For (a,z): list = ["a","z"]; (a,y): ["a","y"]; (x,y): ["x","y"]; (x,z): ["x","z"]. Lexicographically: "a" < "x", so one starting with "a" is better. Within those, compare second: "y" vs "z": "y"<"z". So best is ["a","y"]. So expected selected_ids = ["a","y"]. We must ensure our algorithm picks that.
   Let's simulate with our method.
   Sort sessions by start, then end, then ID. Actually they have same start (9:00) and end (10:00), so tie break by ID: a, x then next slot: y, z (start 10:00 end 11:00). So indices: 0: a, 1: x, 2: y, 3: z. Start times: [S0, S0, S1, S1] where S0=9:00, S1=10:00. Ends: E0=10:00, E1=10:00, E2=11:00, E3=11:00.
   Compute next:
   For i=0 (a): end=10:00, first start >=10:00 is index 2 (y). next=2.
   i=1 (x): end=10:00, next=2.
   i=2 (y): end=11:00, next=4 (n).
   i=3 (z): end=11:00, next=4.
   DP from right:
   i=3 (z): incl = 5 + dp_val[4]=5; excl=dp_val[4]=0; so dp_val[3]=5, dp_cnt=1 (since incl value > excl). So dp_val[3]=5, dp_cnt=1.
   i=2 (y): incl =5+0=5; excl = dp_val[3]=5; equal value. Counts: incl_cnt=1, excl_cnt=1 (since dp_cnt[3]=1). So equal count; we choose exclude (arbitrary). So dp_val[2]=5, dp_cnt=1 (from exclude). (Note: include yields same value and count, so both eligible.)
   i=1 (x): next=2, incl =5+dp_val[2]=5+5=10, incl_cnt=1+dp_cnt[2]=1+1=2; excl=dp_val[2]=5, excl_cnt=dp_cnt[2]=1; incl better -> dp_val[1]=10, dp_cnt=2.
   i=0 (a): next=2, incl=5+dp_val[2]=5+5=10, incl_cnt=2; excl=dp_val[1]=10, excl_cnt=2 (equal value and count). We pick exclude (by our rule). So dp_val[0]=10, dp_cnt=2. So global V=10, C=2.
   Eligible_include:
   i=0: incl condition: value+dp_val[next]=5+5=10 == dp_val[0]=10 and count: 1+dp_cnt[2]=1+1=2 == dp_cnt[0]=2 => eligible true.
   i=1: eligible? 5+dp_val[2]=5+5=10==dp_val[1]=10, 1+dp_cnt[2]=1+1=2==dp_cnt[1]=2 => true.
   i=2: include: 5+0=5==dp_val[2]=5, count 1+0=1==dp_cnt[2]=1 => true (even though we chose exclude, include condition holds)
   i=3: include: 5+0=5==5, count 1==1 => true.
   So all eligible_include true.
   Groups by (val, cnt):
   (10,2): indices 0,1 (a and x)
   (5,1): indices 2,3 (y and z)
   For each group, we build data sorted by index.
   (10,2): indices: 0 (id a), 1 (id x). Suffix min ID from index0: min(a, x)=a; from index1: min(x)=x.
   (5,1): indices:2 (id y),3 (id z). suffix min from2: min(y,z)=y; from3:z.
   Reconstruction:
   s=0, target (10,2). Get group data for (10,2). idx_list = [0,1]. i = bisect_left([0,1], s=0) = 0. suffix_min_idx[0]=0 (since from index0 min id a, at idx0). So best_idx=0 (session a). Add "a". Update s = next[0]=2, target_val=10-5=5, target_cnt=2-1=1.
   Now s=2, target (5,1). Get group data for (5,1). idx_list=[2,3]. i=bisect_left(..., s=2) =0. suffix_min_idx[0]=2 (since min id y at idx2). best_idx=2 (session y). Add "y". s = next[2]=4; target_val=0; target_cnt=0 -> stop. selected_ids=["a","y"] -> correct.

   So algorithm works.

Now, we must consider that in some cases eligible_include may be false for some indices even if they are part of optimal solution because the optimal might come from exclude branch? But for a session to be first element, we require both that it is in some optimal solution for its suffix. That is exactly the include branch condition. So we only consider candidates where include branch yields the optimal value for that prefix. That's correct.

Also, note that there might be a scenario where a session's include branch leads to optimal value and count, but there are multiple optimal solutions from its suffix with different IDs. Our method picks the suffix's lexicographically smallest completion via recursion. That's correct because we use the same greedy for the remainder.

Now, we should test with more complex tie-breaking cases, like same value and count but multiple candidates for first element with same ID (if IDs are unique, not issue). We'll trust.

Edge Cases:
- Sessions with value zero: They can be in optimal set only if they are necessary to achieve max value? But if they have zero value, they never increase value but increase count, so they will be avoided by count minimization. So they won't be selected. Our DP will avoid them because include branch would have same value but higher count. So eligible_include for zero-value sessions will be false because count condition fails (include count > exclude count). So they won't be in groups. So reconstruction will not pick them. Good.

- Sessions with negative value already rejected.

Now, about parsing: The problem says "Parse ISO-like timestamps without time zones using Python standard library." Use datetime.fromisoformat. But if the string is not exactly ISO format (e.g., no seconds), we might still want to accept. But to be safe, we'll attempt fromisoformat, and if that fails, we can try other formats like "%Y-%m-%dT%H:%M:%S". But for simplicity, we'll try fromisoformat first; if ValueError, reject. Since the example shows seconds, it's fine.

But we also need to ensure that the timestamp does not contain timezone info. We can check if dt.tzinfo is not None, then reject. So:

def parse_dt(s):
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is not None:
            return None
        return dt
    except:
        return None

But fromisoformat may also parse strings like "2026-05-01T09:00:00.123456" which is valid. We'll accept.

Now, formatting output: max_value could be int or float. We want to output as number without unnecessary decimals. We can use default json serialization.

Now, we should also think about large value sums: may be big integers; fine.

Now, about memory: groups_data for each key could have many entries. But overall O(n) space.

Now regarding the reconstruction loop: We used while target_cnt > 0. If global_val=0 and global_cnt=0, we skip. However, consider case where global_val>0 but global_cnt=0? Impossible because any positive value requires at least 1 session. So fine.

One more nuance: If there are sessions with value=0 but the only way to achieve global max (e.g., all sessions value=0) then global_val=0, global_cnt=0. So reconstruction will not pick any, selected_ids empty. This matches the minimal count (empty set). If there is a mix of positive and zero, the zero sessions are not needed.

Now, we must also handle the case where there are no eligible candidates for a key during reconstruction (should not happen if the problem is well-defined). But we can raise error or break.

Now, about the output: The problem expects JSON with "max_value", "selected_ids", "rejected". We'll output exactly.

We need to include built-in tests. We'll write a function `run_tests()` that tests multiple scenarios. We'll use assert or raise exception. If all pass, print "All tests passed." We'll have a simple test harness.

We'll also consider testing the tie-breaking for count: For same value, fewer sessions preferred.

Test case:
- sessions: a: value 10, b: value 10, but they overlap, cannot both. So max value=10, count=1. There could be two choices (a or b). We want the one with lexicographically smaller ID among those with same max value and count=1. So if a.id = "y", b.id = "x", we expect selected "x". Our algorithm should pick that. Let's simulate:
   Sessions: a: 9-10 value 10, b: 9:30-10:30 value 10. They overlap.
   Sorted by start: a (9-10), b (9:30-10:30). Next[a] = first start>=10 -> none? a.end=10:00, b.start=9:30 <10, so next[a]=2 (n). Next[b] = none (n).
   DP:
   i=1 (b): incl=10; excl=0 => dp_val[1]=10, dp_cnt=1.
   i=0 (a): incl=10; excl=dp_val[1]=10 (equal value). Counts: incl_cnt=1, excl_cnt=1. We pick exclude (say). So dp_val[0]=10, dp_cnt=1. Eligible_include:
       i=0: include condition: 10 + 0 =10 == dp_val[0], count 1 == 1 => true.
       i=1: true.
   Groups: (10,1): indices 0 (id a) and 1 (id b). But we will have data sorted by index: indices [0,1]; suffix min ID: from i0: min(id_a,id_b)= whichever smaller; from i1: id_b.
   Then reconstruction: s=0, target (10,1). idx_list=[0,1], i=0, suffix_min_idx[0]=0 if id_a < id_b? else min index? For example, a.id="y", b.id="x". Then suffix_min_id at i0: compare "y" and "x": min is "x" at index1? That's not necessarily contiguous in index order. Wait, our prefix min suffix from index i in the sorted-by-index list includes elements with index >= i. So in the list sorted by index (0 then 1), from i0 (first entry) we compare id at index0 ("y") and suffix min from i=1? Actually suffix_min_id[i] = min id from i to end. So at i=0, we consider all indices 0 and 1. So min is min("y","x")="x" at index1. So suffix_min_idx[0]=1 (if id_x < id_y). So we will pick best_idx=1 (session b). That yields selected_ids=["x"]. Good. So reconstruction picks the lexicographically smallest ID among all eligible candidates for that target. So correct.

But we need to ensure that after picking b, the target values decrease. In this case, after picking b (i=1), target_val becomes 0, target_cnt 0. So done. So selected= ["x"]. Good.

Now, test count minimization: Suppose there are two ways to achieve same value, one with count 2, one with count 1. We want the one with fewer sessions. For example, sessions:
  a: value 5, b: value 5, both non-overlapping, so total=10 count=2; also c: value 10 alone. So optimal value=10, but we want fewer sessions, so we should pick c (count 1) over a+b (count 2). DP with (value, count) should pick c. Let's simulate:
  Sessions:
    a: 9-10 value 5; b: 10-11 value 5; c: 9:30-10:30 value 10.
  Sorted by start: a (9-10), c (9:30-10:30), b (10-11). Start_times: a(9), c(9:30), b(10). Ends: a=10, c=10:30, b=11.
  Next:
   a: end=10 -> first start>=10: b (index2)
   c: end=10:30 -> first start>=10:30: b (start=10<10:30) no, so index 3 (n)
   b: end=11 -> n
  DP:
   i=2 (b): incl=5; excl=0 => dp=5,cnt=1.
   i=1 (c): incl=10; excl=dp[2]=5 => dp=10,cnt=1.
   i=0 (a): next=2: incl=5+dp[2]=5+5=10, cnt=2; excl=dp[1]=10,cnt=1 => excl preferred (value equal, cnt smaller). So dp[0]=10,cnt=1. So global V=10,C=1. Eligible_include:
       i=0: include gives value=10 cnt=2, does not match dp_cnt=1, so eligible false.
       i=1: include gives 10 cnt=1, matches dp[1]=10,cnt=1 => true.
       i=2: include gives 5 cnt=1, matches dp[2]=5,cnt=1 => true.
  So eligible only for c and b. Groups: (10,1): i=1 (c) only; (5,1): i=2 (b) maybe. Reconstruction: target=10,1 -> only c is eligible, picks c. So selected_ids=["c"] -> correct.

Thus count minimization works.

Now, lexicographic tie-breaking in include branch only matters when multiple eligible candidates for same (val, cnt). We have covered.

Now, we need to ensure that our grouping only includes indices with eligible_include true. For a candidate to be first element, it needs to have include branch equal to dp_val[i] and dp_cnt[i]. That's exactly eligible_include. However, what about a scenario where a session can be first element even if its include branch doesn't exactly equal dp_val[i] but there is some other solution from i that includes i and achieves dp_val[i] with same value but different count? But dp_cnt[i] is the minimal count for that value. If include branch gives the same value but larger count, it's not optimal for the suffix because we would prefer a solution with fewer sessions (if that exists). But if there is no solution with fewer sessions, the minimal count may be achieved by exclude branch. In that case, including i may still be part of an optimal solution for the entire set? For the suffix from i, the optimal (max value, min count) may be achieved by exclude branch, but there might exist a solution that includes i and achieves the same max value but with a larger count. That solution would not be optimal for the suffix from i in isolation, but could be part of a global optimal solution if the global optimal requires including i and then using a suffix that yields the same value but with higher count? No, because if the suffix can achieve the same max value with a smaller count, the global solution including i would have total count = 1 + (larger count) which would be larger than 1 + (smaller count). Since we want global minimal count, we would prefer the smaller count suffix. So the optimal global solution would not use i if it results in a higher count. So if include branch gives the same value but higher count than the best value from suffix (which may come from exclude), then including i cannot be part of a globally optimal solution (with minimal count). Because we could replace the suffix with the exclude branch solution (fewer sessions) and get same total value but fewer sessions? Wait, if we include i, we get value_i + something. The best could be that exclude gives higher value? Actually, if value_i + best value (min count) of suffix equals max value, but the best min count suffix has count C_min. If include branch uses a suffix with the same max value but larger count, then using the min count suffix would improve total count. So the optimal solution from i is defined as max value with min count; if include branch doesn't achieve the min count, it's not optimal for the suffix, and thus using i would not lead to a globally optimal with min count (since we can replace the suffix with the optimal from next[i] achieving the same value but fewer sessions, total count would be lower while value same). So indeed, for a session to be part of a globally optimal solution (with min count), we need that include branch achieves both the max value and the min count for its suffix. So eligible_include condition correctly captures that.

But what about cases where the optimal solution from i uses include branch but the minimal count from the suffix (dp_cnt[next[i]]) may be achieved by a solution that is not lexicographically smallest but we don't care? Our reconstruction will later pick lexicographically smallest for that suffix, which will be within those achieving the min count (since we enforce that condition). So it's consistent.

Thus, approach seems solid.

Now, potential pitfalls with sorting by start, end, ID: We use that for next array and for DP. The chronological order for output must be by start time (and then end, ID). Our selected list will be in that order because we always pick the earliest eligible session in start order (since s advances to next[best_idx] which is the first start >= end of selected). However, note that two selected sessions may not be consecutive in the sorted list because we skip some. But the order of selection is in increasing start order since we always start at s (the earliest remaining index) and pick a session with index >= s, then jump to next[best_idx] which is an index after the end of the selected session, thus its start >= end, which is >= start of selected session? Actually next[best_idx] is the first start >= end, which is >= end > start, so next session's start is later, so chronological order holds.

Now, about handling duplicate starts: In sorted list, multiple sessions may share the same start time. Our next[best_idx] uses end to jump, so if we pick a session with a certain start, we cannot pick any other session with same start because they overlap? If start equal, they overlap at the start time, so they cannot both be selected. Good.

Now, about the "selected_ids" order: It must be chronological. Our method yields that.

Now, we may think about the possibility that there is an optimal solution that uses no sessions (if max_value=0). Then selected_ids empty. Works.

Now, we need to ensure that if multiple candidates for first element have the same ID (if IDs not unique), we need to break ties by something else (like index)? But problem didn't require uniqueness, but it's implied. We'll assume IDs are unique; if not, our lexicographic comparison might be ambiguous. We can handle by comparing next in list; but it's easier to assume unique or treat as given. Since not specified, we'll assume IDs are unique; otherwise the lexicographic comparison based on IDs would consider equal if IDs same, then we need to compare further? But that would require comparing the rest of the list. Our approach picks the smallest ID; if two sessions have same ID, they are probably considered the same? We'll consider it's not possible, or if it happens, we break by index? But the problem says "lexicographically smaller list of IDs". If there are duplicate IDs, it's ambiguous. So we assume unique.

Now, we should also consider that the value could be non-integer? The problem says "value" (likely numeric). We'll treat as number. In DP we compare directly.

Now, we need to implement the output as JSON. We'll use json.dumps.

Now, about the `--test` flag: We check if sys.argv[1] == '--test'. We'll call run_tests() and then exit. Normal mode: read stdin.

Now, we must ensure the program reads from stdin non interactively. We'll use sys.stdin.read() for JSON.

Now, regarding large input: We read all at once.

Potential memory: storing arrays of size n.

Now, let's code.

We'll structure the code as:

- imports: json, sys, datetime, bisect

- define parse_datetime(s)
- define Session class (or namedtuple). Use simple dataclass? We'll use a class with __init__ and __slots__ to reduce overhead.
- define `solve(sessions_list, ...) -> dict` that takes list of session dicts (valid ones) and returns output dict. But we may also handle rejected list separately. Better: a main function that processes input and returns output.

We'll write:

def process_input(data):
    sessions_raw = data.get('sessions', [])
    valid_sessions = []
    rejected = []
    for sess in sessions_raw:
        # validate
        errors = validate(sess)
        if errors:
            rejected.append({"id": sess.get("id", "unknown"), "reason": errors}) # but we need specific reasons
        else:
            # parse to session object
            # store id, start, end, value
            pass
    # ... algorithm
    return output

But we need to separate validation reasons per field.

Let's define `validate_session(sess)` that returns either (session_obj, None) or (None, reason_str).

We'll do:

def parse_session(sess):
    try:
        sid = sess['id']  # assume exists
    except KeyError:
        return None, "missing id"
    try:
        start = parse_dt(sess['start'])
        if start is None:
            return None, "invalid start timestamp"
    except (KeyError, ValueError):
        return None, "invalid start timestamp"
    try:
        end = parse_dt(sess['end'])
        if end is None:
            return None, "invalid end timestamp"
    except (KeyError, ValueError):
        return None, "invalid end timestamp"
    if end <= start:
        return None, "end must be after start"
    try:
        value = float(sess['value'])  # allow int/float
    except (KeyError, ValueError):
        return None, "invalid value"
    if value < 0:
        return None, "value must be non-negative"
    # If value is integer, we might want int
    if isinstance(sess['value'], int) or (isinstance(sess['value'], float) and sess['value'].is_integer()):
        value = int(sess['value'])
    else:
        value = sess['value']  # keep as float
    session = Session(sid, start, end, value)
    return session, None

We'll parse_dt as described.

But we must note that JSON numbers: float or int. We'll convert to int if possible.

Now, define Session class:

class Session:
    __slots__ = ('id','start','end','value')
    def __init__(self, id, start, end, value):
        self.id = id
        self.start = start
        self.end = end
        self.value = value

Now, sorting: sorted(valid_sessions, key=lambda s: (s.start, s.end, s.id))

Now, compute next_arr, dp arrays.

We'll store positions of sessions in list for later retrieval.

Now about dp_val and dp_cnt: They are numeric. For value, we use int/float. For count, we use int.

Now, about dp_cnt for sentinel: dp_cnt[n]=0.

Now, we need to compute eligible_include.

Now, build groups_data.

We need to be careful with keys: dp_val may be float? But better to keep as Python numbers; (value, count) as key must be hashable. If value is float, it should be fine. But to avoid floating point issues, we assume values are ints (or maybe decimals). Usually they are integers. We'll assume int.

We can convert value to int if it is integer float.

Now, we should also handle the case where there are no valid sessions: Then we build output with max_value=0, selected_ids=[], rejected=rejected_list.

Now, about performance: Sorting sessions is O(n log n). Binary search for each next is O(n log n). DP is O(n). Building groups: O(n). Sorting each group by index: O(n log n) overall if each group sorted individually; but we can collect indices unsorted then sort; total O(n log n) because sum of sizes = n and sorting each group individually is O(k log k) per group sum <= O(n log n) worst case (if one group contains all, it's O(n log n)). So overall O(n log n).

Now, reconstruction: While loop at most n iterations, each O(log n) for binary search, so O(n log n). So overall O(n log n) with good constants.

Now, we must ensure that when we subtract values, target_val becomes zero exactly when target_cnt zero. Use while target_cnt > 0.

Alternative condition: while s < n and target_val > 0: But if target_val>0 but target_cnt=0 (impossible). We'll stick with target_cnt.

Now, the reconstruction loop should also handle case where no candidate for key (shouldn't). We'll break and perhaps set selected_ids empty.

Now, also need to consider that the DP might produce a solution that uses no sessions (global_V=0, global_C=0). In that case, groups may have key (0,0) but we would have eligible_include for sessions with value 0? Possibly not because include would increase count. So (0,0) key may not exist if no session with value 0 and included? But dp_val[0] could be 0 even if there are sessions with zero value but they are not selected because exclude yields 0 count. So dp_cnt[0]=0. Then we will not enter reconstruction loop. selected_ids empty.

Now, but what if there is a session with value 0 that is forced to be selected because there's no other way to achieve max value? If value=0, max value=0 anyway. So we don't need to select it. So fine.

Now, we also need to consider that there might be sessions with negative value already rejected.

Now, about the `max_value` output: It should be the total value of selected subset. Could be 0 if no sessions selected.

Now, we must also consider that input may have sessions with identical start and end times? They can't both be selected, but DP will pick one with higher value? Actually both may have same value, but only one can be chosen. Our DP will handle.

Now, let's write the code.

We'll include comments? Not necessary but helpful for readability. Since it's a single file, we can include minimal comments.

Now, about the test mode: We'll create test cases as Python dicts, feed to a function that runs the algorithm and checks expected output. We'll print "All tests passed." if all pass.

Test cases to include:

1. Simple: one session.
2. Overlap choose highest value.
3. Two non-overlapping with same value: selected all? Actually value total higher than single; but we also test count tie-breaking. We'll have a case with same total value but different counts.
4. Lexicographic tie-breaking: as earlier.
5. Empty sessions.
6. Reject cases: check that rejected list contains correct reasons.
7. Zero value session: should not be selected.
8. Mixed. (maybe)

We'll write them.

Now, potential edge: When there are multiple optimal solutions with same value and count, but they involve different sets; our greedy must pick the one with lexicographically smallest ID list. We'll test with e.g., two possible first sessions with different IDs, and we want the smaller ID. Also test that after picking first, the second is also lexicographically smallest.

We can simulate test where sessions: A(id="c", start=9, end=10, value=5), B(id="a", start=10, end=11, value=5), C(id="b", start=10, end=11, value=5). So first slot only A; second slot B and C. Options: A+B (list ["c","a"]), A+C (["c","b"]). Lex smallest: ["c","a"] because "a"<"b". But note that if we could skip first slot and pick B,C? But they overlap? B and C have same start and end, cannot both. So only A+B or A+C. Our algorithm should pick A+B.

But consider case where there are two different first slot candidates: e.g., sessions: A(id="c", 9-10,5), B(id="a", 9-10,5) (same time), and then C(id="d",10-11,5), D(id="b",10-11,5). We have options: A+C (["c","d"]), A+D (["c","b"]), B+C (["a","c"]? Actually order: B start 9, C start10 -> ["a","c"]), B+D (["a","b"]). Lexicographically smallest: ["a","b"]? Compare: ["a","b"] vs ["a","c"] -> "b"<"c" so ["a","b"] wins. Our algorithm should pick B then D. Let's test with data.

We'll set up:

- B: id="a", start=9:00, end=10:00, value=5
- A: id="c", same times.
- D: id="b", start=10:00, end=11:00, value=5
- C: id="d", same times.

Sorted by start then end then ID: (since same start and end, order by ID) => order: B (id a), A (id c), D (id b? wait D id b starts at 10, so after A; C id d starts at 10). So sorted indices:
0: B (a)
1: A (c)
2: D (b)   (since b < d)
3: C (d)

But careful: D and C have start 10:00; D id b, C id d, so D before C.

Now, compute next:
- For B (id a, end=10:00): first start >=10:00 -> index2 (D) because start of D=10:00.
- For A (id c, end=10:00): next also 2.
- For D (id b, end=11:00): next=4 (n)
- For C (id d, end=11:00): next=4

DP:

i=3 (C): incl=5 -> dp_val=5,cnt=1
i=2 (D): incl=5 ->5; excl=dp_val[3]=5; equal, counts equal (1 each). If we pick exclude (say), dp_val[2]=5,cnt=1.
i=1 (A): next=2, incl=5+5=10, cnt=2; excl=dp_val[2]=5, cnt=1 -> dp_val[1]=10,cnt=2.
i=0 (B): next=2, incl=5+5=10,cnt=2; excl=dp_val[1]=10,cnt=2 (equal). Choose exclude. So dp_val[0]=10,cnt=2.

Eligible_include:
- i=0: incl=10,cnt2 => matches dp_val0=10,cnt2 -> true.
- i=1: incl=10,cnt2 => matches -> true.
- i=2: incl=5,cnt1 matches dp_val2=5,cnt1 -> true (even though we exclude in DP, include condition holds)
- i=3: true.

Groups:
(10,2): indices 0 (id a) and 1 (id c)
(5,1): indices 2 (id b) and 3 (id d)

Now suffix min for (10,2): indices sorted 0,1; suffix min ID from i0: min(a,c)=a at idx0; from i1: c at idx1.
For (5,1): indices 2 (b),3(d); suffix min from i2: min(b,d)=b at idx2.

Reconstruction: s=0, target (10,2): i=0, suffix_min_idx[0]=0 (since a at idx0 is smallest ID?). Wait, at i0, min ID among indices 0,1 is "a" at idx0. So best_idx=0 (B). Add "a". Then new s=next[0]=2; target_val=10-5=5; target_cnt=1.
Now s=2, target (5,1): idx_list=[2,3], i=bisect_left([2,3],2)=0; suffix_min_idx[0]=2 (b). Add "b". selected_ids=["a","b"] -> correct. So algorithm works.

Thus, we have confidence.

Now, about building groups_data: We need to store for each key the idx_list, suffix_min_id, suffix_min_idx. We'll store these as lists. We'll encapsulate in a dict of dicts.

Implementation:

groups_info = {}
for key, lst in groups.items():
    lst.sort(key=lambda x: x[0])  # by idx
    idxs = [item[0] for item in lst]
    m = len(lst)
    suffix_min_id = [None]*m
    suffix_min_idx = [None]*m
    best_id = None
    best_idx = None
    for i in range(m-1, -1, -1):
        idx, id_ = lst[i]
        if best_id is None or id_ < best_id:
            best_id = id_
            best_idx = idx
        suffix_min_id[i] = best_id
        suffix_min_idx[i] = best_idx
    groups_info[key] = {
        'idx_list': idxs,
        'suffix_min_id': suffix_min_id,
        'suffix_min_idx': suffix_min_idx
    }

But note: suffix_min_id[i] is the smallest ID from i to end. Since IDs are strings, we compare directly. If ids are equal (unlikely), we break ties by maybe smaller idx? Not needed. But if two sessions have same ID, our min will pick the one with smaller ID (identical) so first encountered? However, picking any is fine since they have same ID.

Now, reconstruction:

for step:
    if target_cnt == 0: break
    key = (target_val, target_cnt)
    if key not in groups_info:
        # This might happen if optimal solution has no eligible sessions? But should have because we know there is at least one optimal solution. However, if target_cnt == 0, we wouldn't come here. So if we hit this, something wrong; we break.
        break
    info = groups_info[key]
    idx_list = info['idx_list']
    i = bisect.bisect_left(idx_list, s)
    if i == len(idx_list):
        break
    best_idx = info['suffix_min_idx'][i]
    best_id = info['suffix_min_id'][i]
    selected_ids.append(best_id)
    s = next_arr[best_idx]
    target_val -= sessions[best_idx].value
    target_cnt -= 1

But we should also ensure that the best_idx we picked indeed has the property that its next_arr is consistent and the new target_val, target_cnt match dp_val[next_arr], dp_cnt[next_arr]. It should by eligibility.

Now, one more nuance: The eligibility condition ensures include branch gives optimal value and count for that prefix (i). However, the greedy reconstruction relies on the fact that after picking i, the remainder's optimal (value, count) from next[i] equals dp_val[next[i]] and dp_cnt[next[i]]. That holds because we know dp_val[i] = value_i + dp_val[next[i]] and same for counts. So the new target values are correct.

Now, we must also consider that eligible_include may be true for a session i even if dp_val[i] is not the global optimum but the suffix optimum from s. That is fine.

Now, we must handle the case where there are no valid sessions (n=0). Then groups empty. Output max_value=0, selected_ids=[], rejected each rejected. We'll skip DP.

Now, let's write the code.

We'll also define a function `dp_suffix` that computes dp arrays given sorted sessions and next_arr.

Now, careful about large integers: Python int unlimited.

Now, testing: We'll write `run_tests()`. It will define a list of test cases. For each test case, we'll provide input data dict and expected output (or check parts). We'll run `solve` function that returns output dict. We'll compare using assert.

But we need to create a helper that processes the input dict and returns output without reading stdin. So we'll have a function `process(sessions_data)` that takes the list of session dicts and returns output dict. In main, we read JSON, then call process(sessions). For tests, we can call process with test sessions.

But we also need to handle the full input format: {"sessions": [...]}. So `process` will take that dict -> output.

We'll write `def solve(data):` takes the input dict (from JSON) and returns output dict with max_value, selected_ids, rejected.

Implementation steps in solve:

- Extract sessions list from data.
- Validate and separate valid/invalid.
- If no valid: output with 0 and empty.
- Else:
    - Create sorted list.
    - Compute n, start_times, next_arr.
    - DP suffix.
    - Eligible_include.
    - Build groups_info.
    - Reconstruct.
    - Output.

Now, we should also compute the total value of selected? We can compute from global_V.

But ensure that the selected_ids list is in chronological order. Our reconstruction gives that.

Now, about the output: The "max_value" should be the total value of the selected subset. Since we are using global_V, that's correct.

Now, we also need to store the rejected list with reasons. Order of rejected? Probably as encountered.

Now, about id field: The problem shows "id": "a". So we assume each session has an id. If missing, we could reject.

Now, let's code carefully.

We'll need to handle cases where `id` may be not a string? Assume string.

Now, about JSON parsing: `json.load(sys.stdin)` will deserialize numbers as int if possible (float). Our validate can convert.

Now, we should also consider that the input might have extra fields; ignore.

Now, we'll write the code with functions.

Potential Pitfalls:

- The start and end times are naive datetimes; we compare them using <.

- For binary search, we need a list of start times (datetime objects). Since datetime objects are comparable with <, bisect works.

- We'll need to import bisect.

Now, we'll need to compute `dp_cnt[next_arr[i]]` ; but next_arr[i] could be n, we have dp_cnt[n] = 0.

Now, about dp_cnt for sentinel: we set dp_cnt[n]=0.

Now, we also need to be careful that dp_val[0] and dp_cnt[0] may be 0 if no sessions or all zero.

Now, consider session value types: We treat value as number. For DP comparison, if values are floats, equal comparison might be delicate, but we assume they are integers or fine.

Now, about lexicographic comparison of IDs: strings compare normally.

Now, about potential memory: groups_info may have keys that are large numbers; but it's a dict with up to n entries.

Now, we should test with scenario where there are sessions with same value and same count but different IDs; our suffix min will pick smallest ID. Good.

Now, what about scenario where there are no eligible_include for the first few indices, but later indices are eligible? For example, suppose an optimal solution cannot include earlier sessions because they would cause higher count or lower value; our eligible_include condition will only be true for sessions that can be first in optimal solution for that suffix. So we need to ensure that when we start with s=0, the first eligible candidate in groups for target (V*,C*) may be at index > 0. That's fine; the greedy will still pick the smallest ID among those at index >= s. But does the fact that there are no eligible candidates at index 0 mean that we cannot include any session before some index? That's okay; we skip all earlier indices. In reconstruction, we will pick the first eligible index (with smallest ID) as first session. The skipped sessions will not be in the optimal solution.

Now, we also need to handle that after picking a session, we set s = next[best_idx]. This might jump over many indices. The next best_idx's include condition ensures that the remainder's optimal matches the new target. So it's consistent.

Now, we should also think about the possibility that there might be multiple optimal solutions with same value and same count but different sets; our algorithm picks the lexicographically smallest list. Good.

Now, edge case: If there is a session with start exactly equal to end of previous session? Our next uses start >= end, so they are non-overlapping; good. In chronological order, they are ordered by start: later session has later start if start > previous end? Not necessarily; if start equals end, then it's non-overlapping and chronological order places them sequentially. Our sorting by start then end: if start equal, they could be different but non-overlapping if one ends before the other starts? If start equal, they cannot be non-overlapping because they share the start time. So they conflict. So they can't both be selected.

Now, we should test a case where a session has start equal to end of previous, and both are selected; that should be allowed. Example: a: 9-10, b:10-11. Sorted by start: a then b. Next[a] = index where start>=10 -> b index (since start=10). So include a includes b's best from next. So they can both be selected. Good.

Now, consider case where session b has start=10, end=11; a ends at 10. They don't overlap. So feasible.

Now, about the JSON output: We need to serialize datetime? No, only IDs and numbers. So fine.

Now, code.

Now, we should include comments explaining the algorithm? Not required but may help. Keep code clean.

Now, let's start writing.

We'll structure as:

#!/usr/bin/env python3

import sys, json, datetime, bisect

class Session:
    __slots__ = ('id','start','end','value')
    def __init__(self, id, start, end, value): ...

def parse_datetime(s): ...

def validate_session(sess): ...

def solve(data): ...

def run_tests(): ...

def main(): ...

if __name__ == '__main__': main()

Now, parse_datetime: we handle both with fromisoformat and also maybe with strptime as fallback? Let's implement robustly: try fromisoformat, and if that fails because of microsecond or timezone, we can try manual? But we can just try fromisoformat and reject if fails. However, fromisoformat in Python 3.7 does not accept strings like "2026-05-01T09:00:00" ? It does accept. In 3.7 it's strict but accepts that. In 3.11 it's more lenient but still works. So we'll just use it.

But to also handle cases like "2026-05-01T09:00" (without seconds), we might want to add %H:%M format. But the example has seconds. I'll try fromisoformat; if it fails, we can try strptime with format "%Y-%m-%dT%H:%M:%S". And if that fails, try "%Y-%m-%dT%H:%M". This increases robustness. But must be careful with timezone again.

We'll write parse_dt that tries several formats. But ensure no timezone info.

Simpler: Use dateutil? Not allowed. So we'll implement a custom parse function that uses strptime for known formats. I'll write a function that tries to parse with format "%Y-%m-%dT%H:%M:%S". If it fails, try "%Y-%m-%dT%H:%M". We'll also check for timezone by ensuring the string does not contain '+' or '-' after T? But might be ambiguous. We'll reject strings that have timezone indicators (like Z, +, - after time). We'll check using regex? Simpler: assume no timezone. strptime will ignore timezone? Actually, strptime with those formats will fail if there is timezone info. So it's safe. But we must also handle strings with decimal seconds? The example does not have that. We'll not handle fractional seconds unless fromisoformat handles it. We can base on fromisoformat primarily, and if it returns a datetime with tzinfo, reject. But fromisoformat may raise ValueError if not ISO. So we'll do:

def parse_dt(s):
    # Try fromisoformat first
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is not None:
            return None
        return dt
    except:
        pass
    # Try strptime with seconds
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]:
        try:
            dt = datetime.datetime.strptime(s, fmt)
            # strptime returns naive datetime
            return dt
        except:
            continue
    return None

This should catch most ISO-like strings without timezone.

But Python 3.7. fromisoformat may be buggy? It should be fine. We'll go with this.

Now, validate_session:

def validate_session(sess):
    if not isinstance(sess, dict):
        return None, "session is not a dict"
    sid = sess.get('id')
    if sid is None: return None, "missing id"
    start_str = sess.get('start')
    end_str = sess.get('end')
    if not isinstance(start_str, str): return None, "invalid start timestamp"
    if not isinstance(end_str, str): return None, "invalid end timestamp"
    start = parse_dt(start_str)
    if start is None: return None, "invalid start timestamp"
    end = parse_dt(end_str)
    if end is None: return None, "invalid end timestamp"
    if end <= start: return None, "end must be after start"
    value = sess.get('value')
    if value is None or not isinstance(value, (int, float)): return None, "invalid value"
    if value < 0: return None, "value must be non-negative"
    # Optionally convert to int if whole number
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    session = Session(sid, start, end, value)
    return session, None

Now, in solve:

def solve(data):
    sessions_raw = data.get('sessions', [])
    valid_sessions = []
    rejected = []
    for sess in sessions_raw:
        session, err = validate_session(sess)
        if err:
            rejected.append({"id": sess.get('id', 'unknown'), "reason": err})
        else:
            valid_sessions.append(session)
    if not valid_sessions:
        return {"max_value": 0, "selected_ids": [], "rejected": rejected}
    # Sort
    sessions = sorted(valid_sessions, key=lambda s: (s.start, s.end, s.id))
    n = len(sessions)
    # Build start times list
    start_times = [s.start for s in sessions]
    # next array
    next_arr = [0]*n
    for i in range(n):
        next_arr[i] = bisect.bisect_left(start_times, sessions[i].end)
    # DP arrays
    dp_val = [0]*(n+1)
    dp_cnt = [0]*(n+1)
    for i in range(n-1, -1, -1):
        incl_val = sessions[i].value + dp_val[next_arr[i]]
        incl_cnt = 1 + dp_cnt[next_arr[i]]
        excl_val = dp_val[i+1]
        excl_cnt = dp_cnt[i+1]
        if incl_val > excl_val:
            dp_val[i] = incl_val
            dp_cnt[i] = incl_cnt
        elif incl_val < excl_val:
            dp_val[i] = excl_val
            dp_cnt[i] = excl_cnt
        else:
            if incl_cnt < excl_cnt:
                dp_val[i] = incl_val
                dp_cnt[i] = incl_cnt
            else:
                dp_val[i] = excl_val
                dp_cnt[i] = excl_cnt
    global_val = dp_val[0]
    global_cnt = dp_cnt[0]
    # Eligible include
    eligible = [False]*n
    for i in range(n):
        if dp_val[i] == sessions[i].value + dp_val[next_arr[i]] and dp_cnt[i] == 1 + dp_cnt[next_arr[i]]:
            eligible[i] = True
    # Build groups for eligible indices
    groups = {}
    for i in range(n):
        if eligible[i]:
            key = (dp_val[i], dp_cnt[i])
            groups.setdefault(key, []).append( (i, sessions[i].id) )
    # Build groups_info for reconstruction
    groups_info = {}
    for key, lst in groups.items():
        lst.sort(key=lambda x: x[0])  # sort by index
        indices = [item[0] for item in lst]
        m = len(lst)
        suf_min_id = [None]*m
        suf_min_idx = [None]*m
        best_id = None
        best_idx = None
        for i in range(m-1, -1, -1):
            idx, id_ = lst[i]
            if best_id is None or id_ < best_id:
                best_id = id_
                best_idx = idx
            suf_min_id[i] = best_id
            suf_min_idx[i] = best_idx
        groups_info[key] = {
            'indices': indices,
            'suf_min_id': suf_min_id,
            'suf_min_idx': suf_min_idx
        }
    # Reconstruction
    selected_ids = []
    s_idx = 0
    target_val = global_val
    target_cnt = global_cnt
    while target_cnt > 0:  # could also target_val>0
        key = (target_val, target_cnt)
        if key not in groups_info:
            # Should not happen, but break
            break
        info = groups_info[key]
        idx_list = info['indices']
        i = bisect.bisect_left(idx_list, s_idx)
        if i == len(idx_list):
            break
        best_idx = info['suf_min_idx'][i]
        best_id = info['suf_min_id'][i]
        # Double-check that best_idx >= s_idx? Should be by construction.
        selected_ids.append(best_id)
        s_idx = next_arr[best_idx]
        target_val -= sessions[best_idx].value
        target_cnt -= 1
    return {
        "max_value": global_val,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

But we need to ensure that we did not lose the total value if global_val=0 and global_cnt=0: we skip loop. selected_ids empty. Works.

Now, we should consider that the groups_info might be empty if no eligible (e.g., all value=0). Then reconstruction loop not entered.

Now, about the output JSON: We can simply print the dict using json.dumps.

Now, about the main:

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
    else:
        data = json.load(sys.stdin)
        output = solve(data)
        # Print JSON with no indent (compact)
        print(json.dumps(output, ensure_ascii=False, allow_nan=False))

But ensure that max_value could be int/float; we want output as number. Python json handles.

Now, write tests.

In run_tests(), we'll define several test cases as dicts with input (as would be given to solve) and expected output fields. We'll compare.

We need to create a function that compare outputs ignoring order of rejected? But rejected order matters? Likely order as encountered. We can check that rejected list contains expected entries (maybe order not important). We'll just check content.

Simpler: For each test, we call solve(test_input) and then assert certain conditions.

We'll write test cases:

Test 1: Empty sessions.
Input: {"sessions": []}
Expected: max_value=0, selected_ids=[], rejected=[].
Check.

Test 2: Single valid session.
Input: {"sessions": [{"id": "a", "start": "2026-05-01T09:00:00", "end": "2026-05-01T10:30:00", "value": 5}]}
Expected: max_value=5, selected_ids=["a"], rejected=[].

Test 3: Overlap sessions, choose higher value.
Input: [ {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":10}, {"id":"b","start":"2026-05-01T09:30:00","end":"2026-05-01T11:00:00","value":20} ]
Expected: max_value=20, selected_ids=["b"], rejected=[].

Test 4: Non-overlap, combine.
Input: [ {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5}, {"id":"b","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":10} ]
Expected: max_value=15, selected_ids=["a","b"], rejected=[].

Test 5: Tie value with count minimization.
Input: sessions: a (value 5, 9-10), b (value 5, 10-11), c (value 10, 9:30-10:30). Expected: max_value=10, selected_ids=["c"], rejected=[].

Test 6: Lexicographic tie-breaking.
Input: sessions:
  {"id":"x","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
  {"id":"y","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5},
  {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
  {"id":"z","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5}
But careful: overlapping? a and x have same start/end: they overlap completely, cannot both. So optimal sets: pick one from first slot and one from second slot. We expect max_value=10, count=2. Lexicographically smallest list: ["a","y"]? Let's compute: options: (a,y) -> ["a","y"]; (a,z)->["a","z"]; (x,y)->["x","y"]; (x,z)->["x","z"]. Among these, compare: "a"<"x", so those starting with a are better; compare second: "y"<"z", so best is ["a","y"]. Expected selected_ids ["a","y"].
We'll use that.

Test 7: Rejected sessions: invalid start, invalid end, end before start, negative value.
Input: sessions:
 {"id":"r1","start":"invalid","end":"2026-05-01T10:00:00","value":5},
 {"id":"r2","start":"2026-05-01T09:00:00","end":"invalid","value":5},
 {"id":"r3","start":"2026-05-01T10:00:00","end":"2026-05-01T09:00:00","value":5},
 {"id":"r4","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":-1},
 {"id":"v1","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
 Expected: max_value=5, selected_ids=["v1"], rejected length=4 with appropriate reasons.

Test 8: Zero value session not selected.
Input: sessions:
 {"id":"z1","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":0},
 {"id":"v1","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5}
Expected: max_value=5, selected_ids=["v1"], rejected=[] (v1 selected, zero value not selected because not needed). Because DP will exclude it to avoid count.

Test 9: Multiple optimal with same value, count, but different ID order; test lexicographic with first element different.
We already have test6.

Test 10: Test that if all sessions have value 0, max_value=0, selected empty.

Test 11: Test count tie-breaking: two sessions with value=10 each but overlapping, so only one selected. Then we have two candidates with same value and count (1). The one with smaller ID selected. Simpler test.

We'll code these tests.

We need to parse expected output. For simplicity, we'll check max_value and selected_ids exactly, and check rejected list length and maybe some ids.

We'll use assert.

Now, we must be careful: The `solve` function returns numbers (max_value) and list of IDs. For comparison, we need to ensure that IDs are strings. So selected_ids order is as returned.

In test6, we expect ["a","y"]. We'll check.

Now, one more test: In test5, we have c (value10) and a,b (value5 each). Expected selected_ids=["c"].

Now, test with overlapping and tie on count: sessions: a (id="b",value=5,9-10), b (id="a",value=5,9-10) -> they overlap exactly. So only one can be selected. Both have same value, count 1. Lexicographically smaller ID is "a". So expected selected_ids=["a"]. We'll test.

Now, we should also test that the reconstruction doesn't pick more sessions than needed (count minimization). Already covered.

Now, we could also test that the DP correctly rejects sessions with negative value.

Now, we have to be aware that our solution's output might not have the exact field order in JSON but it's fine.

Now, executing tests: we can call run_tests() which prints success if all pass.

Now, about `run_tests` function: We'll define a helper `check_test(name, input_data, expected_max, expected_ids, expected_rejected_len, ...)`. But we'll just do asserts.

We'll put all tests in a list of cases or sequentially.

We'll do:

def run_tests():
    # test 1
    data = {"sessions": []}
    out = solve(data)
    assert out["max_value"] == 0
    assert out["selected_ids"] == []
    assert out["rejected"] == []
    print("Test 1 passed: empty")

    # test 2
    data = {"sessions": [{"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:30:00","value":5}]}
    out = solve(data)
    assert out["max_value"] == 5
    assert out["selected_ids"] == ["a"]
    assert out["rejected"] == []
    print("Test 2 passed: single")

    # test 3 overlap
    data = {"sessions": [
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":10},
        {"id":"b","start":"2026-05-01T09:30:00","end":"2026-05-01T11:00:00","value":20}
    ]}
    out = solve(data)
    assert out["max_value"] == 20
    assert out["selected_ids"] == ["b"]
    assert out["rejected"] == []
    print("Test 3 passed: overlap")

    # test 4 non-overlap combine
    data = {"sessions": [
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"b","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":10}
    ]}
    out = solve(data)
    assert out["max_value"] == 15
    assert out["selected_ids"] == ["a","b"]
    assert out["rejected"] == []
    print("Test 4 passed: non-overlap combine")

    # test 5 count minimization
    data = {"sessions": [
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"b","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5},
        {"id":"c","start":"2026-05-01T09:30:00","end":"2026-05-01T10:30:00","value":10}
    ]}
    out = solve(data)
    assert out["max_value"] == 10
    assert out["selected_ids"] == ["c"], f"Expected [c], got {out['selected_ids']}"
    assert out["rejected"] == []
    print("Test 5 passed: count minimization")

    # test 6 lexicographic tie-breaking (four sessions as above)
    data = {"sessions": [
        {"id":"x","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"y","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5},
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"z","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5}
    ]}
    out = solve(data)
    assert out["max_value"] == 10
    assert out["selected_ids"] == ["a","y"], f"Expected [a,y], got {out['selected_ids']}"
    assert out["rejected"] == []
    print("Test 6 passed: lexicographic")

    # test 7 rejected sessions
    data = {"sessions": [
        {"id":"r1","start":"invalid","end":"2026-05-01T10:00:00","value":5},
        {"id":"r2","start":"2026-05-01T09:00:00","end":"invalid","value":5},
        {"id":"r3","start":"2026-05-01T10:00:00","end":"2026-05-01T09:00:00","value":5},
        {"id":"r4","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":-1},
        {"id":"v1","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5}
    ]}
    out = solve(data)
    assert out["max_value"] == 5
    assert out["selected_ids"] == ["v1"]
    assert len(out["rejected"]) == 4
    # Check reasons (optional)
    # IDs of rejected: r1,r2,r3,r4 (order could be as input)
    rejected_ids = [r['id'] for r in out['rejected']]
    assert 'r1' in rejected_ids
    assert 'r2' in rejected_ids
    assert 'r3' in rejected_ids
    assert 'r4' in rejected_ids
    print("Test 7 passed: rejections")

    # test 8 zero value not selected
    data = {"sessions": [
        {"id":"z1","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":0},
        {"id":"v1","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5}
    ]}
    out = solve(data)
    assert out["max_value"] == 5
    assert out["selected_ids"] == ["v1"]
    assert out["rejected"] == []
    print("Test 8 passed: zero value not selected")

    # test 9 all zero
    data = {"sessions": [
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":0}
    ]}
    out = solve(data)
    assert out["max_value"] == 0
    assert out["selected_ids"] == []
    assert out["rejected"] == []
    print("Test 9 passed: all zero")

    # test 10 tie count lexicographic (overlap same value)
    data = {"sessions": [
        {"id":"b","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5}
    ]}
    out = solve(data)
    assert out["max_value"] == 5
    # Both have same value, count 1; lexicographically smaller ID is "a"
    assert out["selected_ids"] == ["a"], f"Expected [a], got {out['selected_ids']}"
    print("Test 10 passed: tie count lexicographic")

    print("\nAll tests passed!")

We should also test case where multiple sessions with same start but different IDs, and the one with smaller ID may be later in the start order? Actually this is fine.

Now, we must ensure that the reconstruction picks the session with smallest ID among eligible for the suffix. In test10, both sessions are eligible (include branch yields optimal value 5, count 1). The groups for (5,1) will have indices 0 and 1 (sorted by index: 0 then 1). Suffix min ID from i0: min("b","a") = "a" at idx1. So picks idx1 (session a). So output ["a"]. Good.

Now, one more test: When there are three sessions, two in first slot (same times) and one in second slot, but only one valid combination. For instance:
  sessions:
    a: id="a", start=9, end=10, value=5
    b: id="b", start=9, end=10, value=5
    c: id="c", start=10, end=11, value=5
Optimal: pick one from first and c (value 10, count 2). Options: a+c or b+c. Lexicographically: ["a","c"] vs ["b","c"] => first element "a" < "b", so pick a+c. Expected: selected_ids ["a","c"].
Let's test (should be covered by test6? Not exactly, but we can add a test case.

We'll add test 11:
   data = {"sessions": [
        {"id":"b","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"c","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5}
   ]}
   Expected: max_value=10, selected_ids=["a","c"], rejected=[].

Our algorithm should produce ["a","c"] because: sorted by start then end then ID: indices: a (id a) then b (id b) then c. Next: a and b both have next=2 (c). DP: i=2 (c) =>5; i=1 (b): incl=10 cnt2, excl=5 cnt1 -> dp_val=10 cnt2; i=0 (a): incl=10 cnt2, excl=dp_val[1]=10 cnt2 -> tie; we pick exclude (say). dp_val[0]=10 cnt2. Eligible_include: a: true, b: true, c: true. Groups: (10,2): indices 0 (a) and 1 (b). Suffix min from i0: min(a,b)=a at idx0. So picks a. Then s= next[0]=2; target (5,1) selects c. So good.

Add this test.

Now, need also to test that if there are multiple sessions with same start and end and same value, but the first element picks the smallest ID, then the second picks the smallest among remaining. Already covered.

Now, about test for `--test`: We'll run run_tests() and then exit.

Now, ensure that our solve function returns the correct types. max_value should be number. selected_ids list of strings. rejected list of objects with id and reason strings.

Now, potential issue: In DP, we set dp_cnt for include include_cnt. But if include and exclude have same value and count, we prefer exclude. That's fine.

Now, also we should consider that values might be non-integer (float). Our equality for include condition uses `==`. This is fine for floats, but could have precision issues. But input likely integers.

Now, we should also consider that the value of a session could be non-negative integer; if float, it's okay.

Now, about the `max_value` output: When global_val is 0, we output 0.

Now, we should also test a case where all sessions are invalid: only rejected. Expect max_value=0, selected_ids=[], rejected filled.

Test 12:
   data = {"sessions": [{"id":"x","start":"bad","end":"bad","value":5}]}
   out = solve(data)
   assert out["max_value"] == 0
   assert out["selected_ids"] == []
   assert len(out["rejected"]) == 1
We'll include.

Now, let's code.

Now, we need to be careful about the JSON parsing: The input may have "start" and "end" as strings, "value" as number. Our validate handles.

Now, about IDs: They may be numbers? In example it's string. Our code expects string (since we call sess.get('id') and later compare strings). If IDs are numbers, the lexicographic comparison might be different? But they'd be represented as numbers in JSON; Python would load as int or float. We can convert to string? The problem statement shows "id": "a", so likely strings. But to be safe, we can convert id to str? But then lexicographic for numbers would be different. I think it's safe to assume IDs are strings. We'll treat as string. If int, our validation would still accept. But then we would compare ints lexicographically? Actually string comparison of ints would be different (e.g., "10" < "2" lexicographically). That might be incorrect. So we should keep IDs in their native type but for comparison we need to define a consistent ordering. The problem says "lexicographically smaller list of IDs". Lexicographic comparison works on sequences; if IDs are numbers, they are not lexicographic but we convert to string? The problem implicitly assumes IDs are strings. So we'll store as string. If the id field is not a string, we could convert to string using str() to maintain the ability to compare. But the problem's examples show string IDs. We'll assume string. If not, we could reject? I'll treat it as string using `str(sess.get('id',''))`. But possibly the user may provide integer IDs. To be safe, we'll convert to string for storage. Because lexicographic order on strings is defined; on numbers it's not. So we can ensure that IDs are strings by converting. However, if the input has id as integer, the output should still be that integer, not string? The example output shows "selected_ids": ["a"] (strings). So they should be strings. So we'll enforce that id is a string; if not, we can reject or convert? But the problem does not specify. We'll assume it's string. We'll check if id is not string, maybe we accept but convert to string for storage? Then the output would contain string representation of the integer, which might not match input? But better to reject? I think it's safer to accept and convert to string, but the problem might expect the id as is. Since it's not specified, we'll assume they are strings. We'll not convert; we'll keep as is. If they are numbers, then lexicographic comparison would not be defined, but Python compares numbers using numeric order. But lexicographic generally means compare elements as per their natural order; for numbers it's numerical order. But "lexicographically" in context of lists often means compare first element, if equal then second, etc., using the default ordering of the elements. For numbers, that's numeric. For strings, that's lexicographic. The problem example uses strings. We'll assume strings. We'll not force conversion.

We'll define ID as whatever type comes from JSON. But then when we compare IDs in `id_ < best_id`, if they are of different types (e.g., one str, one int), it might raise error. So we expect all IDs to be of same type. We'll validate that ID is a string. In validate_session, we can check if isinstance(sid, str) else reject. I'll add that.

We'll add:
  sid = sess.get('id')
  if not isinstance(sid, str):
      return None, "invalid id (must be string)"
This ensures type consistency.

Now, we must adjust reject reasons accordingly.

Now, integrate.

Now, let's write the code.

Potential pitfalls with timezone detection: Using fromisoformat may parse timezone correctly, but we check dt.tzinfo is not None to reject. In Python 3.7, fromisoformat does not parse timezone offsets? Actually fromisoformat in Python 3.7 does not support parsing timezone offsets; it only supports the format YYYY-MM-DDTHH:MM:SS or with microseconds but no timezone. So for string with timezone, it will raise ValueError. So we don't need check tzinfo. But we'll keep.

Now, about strptime formats: We'll try with seconds and without seconds. We'll also try with "Z" suffix? Since ISO allows "Z" for UTC. But we said no timezones, so we can reject strings with Z. But strptime doesn't handle Z. So they will fail. Good.

Now, we might also want to handle strings like "2026-05-01T09:00:00.123" (fractional seconds). fromisoformat handles it. Our strptime format with seconds won't. So fromisoformat will succeed, but if it returns a datetime with tzinfo? It won't fromisoformat doesn't parse fractional seconds in 3.7? Actually Python 3.7's fromisoformat can parse "2026-05-01T09:00:00.123456". Yes, it can. And it's naive. So good.

Thus, we'll rely on fromisoformat primarily.

Now, implement parse_dt as:

def parse_dt(s):
    if not isinstance(s, str):
        return None
    # Try fromisoformat
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is not None:
            return None
        return dt
    except:
        pass
    # Try without microseconds
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"]:
        try:
            dt = datetime.datetime.strptime(s, fmt)
            # strptime returns naive
            return dt
        except:
            continue
    return None

But note: fromisoformat in Python 3.11+ can parse strings like "2026-05-01T09:00". So it may succeed for that format. But we have fallback.

Now, think about performance: For each session we parse two dates. That's fine.

Now, we must ensure that the computation of next array works with datetime objects. bisect_left(start_times, end_i) works because start_times is a list of datetime objects, and end_i is datetime, both comparable.

Now, we need to differ between tests and normal mode. Use sys.argv[1] check.

Potential: sys.argv[1] may be absent. Use len(sys.argv) > 1.

Now, about output: Print only JSON in normal mode.

Now, we can include `if __name__ == '__main__': main()`.

Now, let's write the whole code.

We must keep code under 1000 lines. Our code with tests should be under.

Now, let's start coding in our mind.

Plan to write:

1. Imports.
2. Session class.
3. parse_dt.
4. validate_session.
5. solve(data) function.
6. run_tests function.
7. main function.

We'll also need to import bisect.

Now, code:

```python
import sys
import json
import datetime
import bisect

class Session:
    __slots__ = ('id','start','end','value')
    def __init__(self, id_, start, end, value):
        self.id = id_
        self.start = start
        self.end = end
        self.value = value

def parse_dt(s):
    if not isinstance(s, str):
        return None
    # Try fromisoformat (Python 3.7+)
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is not None:
            return None
        return dt
    except:
        pass
    # Fallback formats
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return dt
        except:
            continue
    return None

def validate_session(sess):
    if not isinstance(sess, dict):
        return None, "invalid session object"
    sid = sess.get('id')
    if not isinstance(sid, str):
        return None, "missing or invalid id"
    start_str = sess.get('start')
    end_str = sess.get('end')
    if not isinstance(start_str, str):
        return None, "invalid start timestamp"
    if not isinstance(end_str, str):
        return None, "invalid end timestamp"
    start = parse_dt(start_str)
    if start is None:
        return None, "invalid start timestamp"
    end = parse_dt(end_str)
    if end is None:
        return None, "invalid end timestamp"
    if end <= start:
        return None, "end must be after start"
    value = sess.get('value')
    if not isinstance(value, (int, float)):
        return None, "invalid value"
    if value < 0:
        return None, "value must be non-negative"
    # Convert integer floats to int
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    session = Session(sid, start, end, value)
    return session, None

def solve(data):
    sessions_raw = data.get('sessions', [])
    valid = []
    rejected = []
    for sess in sessions_raw:
        session, err = validate_session(sess)
        if err:
            rejected.append({"id": sess.get('id', 'unknown'), "reason": err})
        else:
            valid.append(session)
    if not valid:
        return {"max_value": 0, "selected_ids": [], "rejected": rejected}
    # Sort by start, then end, then id
    sessions = sorted(valid, key=lambda s: (s.start, s.end, s.id))
    n = len(sessions)
    # Build start times list and next array
    start_times = [s.start for s in sessions]
    next_arr = [0]*n
    for i in range(n):
        next_arr[i] = bisect.bisect_left(start_times, sessions[i].end)
    # DP arrays
    dp_val = [0]*(n+1)
    dp_cnt = [0]*(n+1)   # dp for number of sessions (min count for max value)
    for i in range(n-1, -1, -1):
        incl_val = sessions[i].value + dp_val[next_arr[i]]
        incl_cnt = 1 + dp_cnt[next_arr[i]]
        excl_val = dp_val[i+1]
        excl_cnt = dp_cnt[i+1]
        if incl_val > excl_val:
            dp_val[i] = incl_val
            dp_cnt[i] = incl_cnt
        elif incl_val < excl_val:
            dp_val[i] = excl_val
            dp_cnt[i] = excl_cnt
        else:  # equal value
            if incl_cnt < excl_cnt:
                dp_val[i] = incl_val
                dp_cnt[i] = incl_cnt
            else:
                dp_val[i] = excl_val
                dp_cnt[i] = excl_cnt
    global_val = dp_val[0]
    global_cnt = dp_cnt[0]
    # Determine eligible include (sessions that can be part of an optimal solution for their suffix)
    eligible = [False]*n
    for i in range(n):
        if dp_val[i] == sessions[i].value + dp_val[next_arr[i]] and dp_cnt[i] == 1 + dp_cnt[next_arr[i]]:
            eligible[i] = True
    # Build groups of (value, count) -> list of (index, id) for eligible sessions
    groups = {}
    for i in range(n):
        if eligible[i]:
            key = (dp_val[i], dp_cnt[i])
            groups.setdefault(key, []).append((i, sessions[i].id))
    # Build per-group data for fast retrieval of smallest ID by index threshold
    groups_data = {}
    for key, lst in groups.items():
        # sort by index
        lst.sort(key=lambda x: x[0])
        indices = [x[0] for x in lst]
        m = len(lst)
        suf_min_id = [None]*m
        suf_min_idx = [None]*m
        best_id = None
        best_idx = None
        for i in range(m-1, -1, -1):
            idx, id_ = lst[i]
            if best_id is None or id_ < best_id:
                best_id = id_
                best_idx = idx
            suf_min_id[i] = best_id
            suf_min_idx[i] = best_idx
        groups_data[key] = {
            'indices': indices,
            'suf_min_id': suf_min_id,
            'suf_min_idx': suf_min_idx
        }
    # Reconstruction: get lexicographically smallest list
    selected_ids = []
    s = 0
    target_val = global_val
    target_cnt = global_cnt
    while target_cnt > 0:
        key = (target_val, target_cnt)
        if key not in groups_data:
            # Should not happen, but just in case
            break
        gd = groups_data[key]
        idx_list = gd['indices']
        pos = bisect.bisect_left(idx_list, s)
        if pos == len(idx_list):
            break
        best_idx = gd['suf_min_idx'][pos]
        best_id = gd['suf_min_id'][pos]
        # In case best_idx < s? Could happen if suffix min from pos points to an index earlier than s? Since we advanced to first index >= s, and then take best from suffix, but the best might be an earlier index if there's a smaller ID among earlier indices? But those earlier indices are before s (idx < s) because we started at pos with idx >= s. However, suf_min_idx[pos] returns the index of the smallest ID among all indices in the suffix of the index-sorted list from pos. That suffix includes only indices >= the first index >= s, so all indices >= that first index, which are >= s. So best_idx >= s. So fine.
        selected_ids.append(best_id)
        s = next_arr[best_idx]
        target_val -= sessions[best_idx].value
        target_cnt -= 1
    return {
        "max_value": global_val,
        "selected_ids": selected_ids,
        "rejected": rejected
    }

def run_tests():
    # Test 1: Empty
    data1 = {"sessions": []}
    out1 = solve(data1)
    assert out1["max_value"] == 0
    assert out1["selected_ids"] == []
    assert out1["rejected"] == []
    print("Test 1 passed: empty")

    # Test 2: Single session
    data2 = {"sessions": [{"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:30:00","value":5}]}
    out2 = solve(data2)
    assert out2["max_value"] == 5
    assert out2["selected_ids"] == ["a"]
    assert out2["rejected"] == []
    print("Test 2 passed: single")

    # Test 3: Overlap, choose higher value
    data3 = {"sessions": [
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":10},
        {"id":"b","start":"2026-05-01T09:30:00","end":"2026-05-01T11:00:00","value":20}
    ]}
    out3 = solve(data3)
    assert out3["max_value"] == 20
    assert out3["selected_ids"] == ["b"]
    assert out3["rejected"] == []
    print("Test 3 passed: overlap high value")

    # Test 4: Non-overlapping combine
    data4 = {"sessions": [
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"b","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":10}
    ]}
    out4 = solve(data4)
    assert out4["max_value"] == 15
    assert out4["selected_ids"] == ["a","b"]
    assert out4["rejected"] == []
    print("Test 4 passed: non-overlap combine")

    # Test 5: Count minimization (prefer one session over two with same total value)
    data5 = {"sessions": [
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"b","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5},
        {"id":"c","start":"2026-05-01T09:30:00","end":"2026-05-01T10:30:00","value":10}
    ]}
    out5 = solve(data5)
    assert out5["max_value"] == 10
    assert out5["selected_ids"] == ["c"]
    assert out5["rejected"] == []
    print("Test 5 passed: count minimization")

    # Test 6: Lexicographic tie-breaking
    data6 = {"sessions": [
        {"id":"x","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"y","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5},
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"z","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5}
    ]}
    out6 = solve(data6)
    assert out6["max_value"] == 10
    # Expect ["a","y"] because lex smallest first element "a", then second "y" < "z"
    assert out6["selected_ids"] == ["a","y"], f"Expected [a,y], got {out6['selected_ids']}"
    assert out6["rejected"] == []
    print("Test 6 passed: lexicographic tie")

    # Test 7: Rejected sessions
    data7 = {"sessions": [
        {"id":"r1","start":"invalid","end":"2026-05-01T10:00:00","value":5},
        {"id":"r2","start":"2026-05-01T09:00:00","end":"invalid","value":5},
        {"id":"r3","start":"2026-05-01T10:00:00","end":"2026-05-01T09:00:00","value":5},
        {"id":"r4","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":-1},
        {"id":"v1","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5}
    ]}
    out7 = solve(data7)
    assert out7["max_value"] == 5
    assert out7["selected_ids"] == ["v1"]
    assert len(out7["rejected"]) == 4
    rejected_ids = [r["id"] for r in out7["rejected"]]
    for rid in ["r1","r2","r3","r4"]:
        assert rid in rejected_ids, f"Missing {rid}"
    print("Test 7 passed: rejections")

    # Test 8: Zero value session not selected
    data8 = {"sessions": [
        {"id":"z1","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":0},
        {"id":"v1","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5}
    ]}
    out8 = solve(data8)
    assert out8["max_value"] == 5
    assert out8["selected_ids"] == ["v1"]
    assert out8["rejected"] == []
    print("Test 8 passed: zero value")

    # Test 9: All zero value
    data9 = {"sessions": [{"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":0}]}
    out9 = solve(data9)
    assert out9["max_value"] == 0
    assert out9["selected_ids"] == []
    assert out9["rejected"] == []
    print("Test 9 passed: all zero")

    # Test 10: Overlap same value, lexicographic
    data10 = {"sessions": [
        {"id":"b","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5}
    ]}
    out10 = solve(data10)
    assert out10["max_value"] == 5
    assert out10["selected_ids"] == ["a"], f"Expected [a], got {out10['selected_ids']}"
    assert out10["rejected"] == []
    print("Test 10 passed: lexicographic among overlapping")

    # Test 11: Three sessions, lexicographic on both levels
    data11 = {"sessions": [
        {"id":"b","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"a","start":"2026-05-01T09:00:00","end":"2026-05-01T10:00:00","value":5},
        {"id":"c","start":"2026-05-01T10:00:00","end":"2026-05-01T11:00:00","value":5}
    ]}
    out11 = solve(data11)
    assert out11["max_value"] == 10
    assert out11["selected_ids"] == ["a","c"], f"Expected [a,c], got {out11['selected_ids']}"
    assert out11["rejected"] == []
    print("Test 11 passed: three sessions lexicographic")

    # Test 12: All invalid
    data12 = {"sessions": [{"id":"x","start":"bad","end":"bad","value":5}]}
    out12 = solve(data12)
    assert out12["max_value"] == 0
    assert out12["selected_ids"] == []
    assert len(out12["rejected"]) == 1
    print("Test 12 passed: all invalid")

    print()
    print("All tests passed!")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        run_tests()
    else:
        data = json.load(sys.stdin)
        output = solve(data)
        # Print JSON without extra whitespace
        print(json.dumps(output, allow_nan=False, ensure_ascii=False))

if __name__ == '__main__':
    main()
```

Now, we should test this code manually with a few cases to ensure no bugs.

But before finalizing, let's think about potential pitfalls.

- In DP, when incl_val == excl_val, we choose exclude if incl_cnt >= excl_cnt. This means if counts equal, we prefer exclude. This could affect eligible_include for some sessions? For a session where include and exclude have same value and count, both include and exclude are optimal. Our DP picks exclude. Then dp_val[i] and dp_cnt[i] reflect the exclude branch. However, the include branch also achieves the same value and count. As a result, for that session, the condition for eligible_include (include branch) will be true because include branch yields value_i+dp_val[next] == dp_val[i] and count_i+dp_cnt[next] == dp_cnt[i]. Even though dp_val[i] is set from exclude branch, the equality holds because include yields same values. So eligible_include is true. Good.

- What about a scenario where include and exclude offer same value but exclude has fewer count? Then include will not be eligible (since its count larger). That's correct.

- What about scenario where include and exclude have same value and count, but after picking include, the chosen suffix from next[i] might have multiple optimal with different ID lists; our eligibility check only ensures that there exists some optimal solution including i. Then in reconstruction, when we pick i as first, we will later find the smallest ID list for the suffix. However, note that we picked i based on smallest ID among eligible for the overall target. But what if there is another optimal solution that also includes i but uses a different suffix that yields a different second ID, and that suffix is not the one with smallest ID for the remainder? Since we are going to recursively pick the smallest ID for the remainder, we are effectively picking the lexicographically smallest overall. So consistent.

- What if two eligible sessions for the same target (global) have same ID? Not possible as unique.

Now, we must also consider that after we pick the first session i, the new target becomes target_val = global_val - value_i, target_cnt = global_cnt - 1. However, it might be that for the remainder, there is an optimal solution with the same value but different count? No, by construction, target_val and target_cnt are exactly dp_val[next[i]] and dp_cnt[next[i]]. So the remainder's optimal is exactly target. So the greedy will work.

Now, we should also test scenario where there is more than one optimal solution for the remainder, and the suffix might have multiple candidates for the next element. Our algorithm will choose the smallest ID among those eligible for that suffix's optimum. That yields lexicographically smallest continuation.

Now, think about a potential counterexample: Suppose the first element candidate with the smallest ID, when combined with the lexicographically smallest remainder, gives list L1. But there might be another first element with a slightly larger ID but leads to a much smaller second ID such that overall list becomes lexicographically smaller? Lexicographic order compares first element first. So a smaller first element always wins regardless of the rest. So yes, we must choose the smallest possible first ID among all optimal solutions. So our greedy picking the smallest ID eligible for the global target is correct. That is exactly what we do: among eligible indices with dp_val==global_val and dp_cnt==global_cnt (i.e., those that can be part of an optimal solution for the global problem), we pick the smallest ID. This matches.

But what if there is an eligible session i with dp_val[i] == global_val and dp_cnt[i] == global_cnt, but there exists an optimal solution that does not include i but also achieves global optimum? Then i is still eligible as first if there exists some optimal solution that includes i. That's fine; if there is an optimal solution that includes i, then using i as first can yield a solution. If there is another optimal solution that does not include i, its first element may have a smaller ID? But then that smaller ID is also eligible (since it's part of some optimal solution). Since we pick the smallest ID among all eligible, we will pick that smaller ID instead. So correct.

Thus our algorithm for first element is optimal.

Now, we should also ensure that the groups_data for key (global_val, global_cnt) includes all sessions that are first-element eligible. But what about sessions that are not eligible_include but still could be part of an optimal solution as first element? Consider a session i for which include branch gives the same value but higher count than the best count for that suffix. That cannot be part of a globally optimal solution with minimal count because it would increase the total count. So such session cannot be first in a global optimal solution with minimal count. So we exclude them. Good.

Now, what about a session i where include branch gives less value than dp_val[i] but it's still possible to be first element in some global optimal? No, because if include branch gives less value, then including i reduces total value, so it cannot lead to global optimum (max value). So not eligible.

Thus eligible_include correctly captures candidates that can be the first session in a (V*, C*) optimal solution.

Thus algorithm stands.

Now, double-check DP correctness with floating values? Not needed.

Now, think about the scenario where there are multiple eligible sessions for the same key, and we pick the smallest ID. But what if that smallest ID session, when selected, leads to a suffix where the lexicographically smallest completion is not available because that suffix cannot achieve the target with minimal count? However, by definition of eligibility (include condition), we know that there exists at least one completion from next[i] achieving target_val-value_i and target_cnt-1 (the DP optimal for that suffix). That completion may not be the lexicographically smallest for that suffix, but there exists at least one. So we can then recursively apply the greedy to get the lexical smallest for that suffix. Since we always take the smallest ID among all eligible for each step, it should produce overall lexicographic smallest.

But is it possible that picking the smallest ID first forces a later completion that is not the lexicographically smallest for the remainder compared to if we picked a different first with slightly larger ID but leads to a much smaller second ID that makes overall list lexicographically smaller? Again, first element comparison dominates. So no.

Thus fine.

Now, we should also consider that there might be multiple optimal solutions with the same V and C but different counts? Wait, C is minimal count for V. So all optimal solutions have same count C*. So no.

Now, code seems okay.

Let's run through test6 in our mind:

Earlier we got correct.

Now, test5: c has value 10, a and b each 5. DP picks c count 1. Eligible: a? For a, include gives 5+dp_val[next[a]]=5+5=10 != dp_val[0]? dp_val for index of a? We need consider sorting order. Let's simulate with code order: sessions sorted by start: a (9-10), c (9:30-10:30), b (10-11). So indices: 0 a, 1 c, 2 b.
DP: we computed earlier: global_val=10 from c. Eligible: a? include for a: value+dp_val[next[a]] where next[a]=2 (b) =5+5=10, count=2; dp_val[0] from our DP (we chose exclude for a?) Actually earlier calc: for index0, dp_val[0]=10, dp_cnt[0]=1 (since prefer exclude because exclude gives 10 cnt1). Include gives 10 cnt2, so not equal count. So eligible for a false. c: include gives 10 cnt1 matches dp_val[1]=10 cnt1 => true. b: include 5 cnt1 matches dp_val[2]? dp_val[2]=5 cnt1 => true. So groups: (10,1): index1 (c); (5,1): index2 (b). Reconstruction: s=0, target (10,1): i = bisect_left([1],0)=0, suffix_min_idx[0]=1 (c). picks c. Then s=next[1]=? next[1] for c? End=10:30, first start >=10:30? b start=10<10:30 so none-> n=3; s=3; target becomes 0; loop ends. So selected_ids=["c"]. Good.

Now, test11 (three sessions): b, a, c. Sorted: a (id a, start9), b (id b, start9), c (start10). Indices:0 a,1 b,2 c.
next: a: end10 => first start>=10? c (index2); b: also next=2; c: next=3.
DP: i=2 c: incl=5, excl=0 => dp_val=5,cnt1.
i=1 b: incl=5+5=10 cnt2; excl=5 cnt1 => dp_val=10,cnt2.
i=0 a: incl=5+5=10 cnt2; excl=dp_val[1]=10 cnt2; tie counts equal; we choose exclude (by our rule). So dp_val[0]=10 cnt2.
Eligible:
a: include 5+5=10 cnt2 matches dp_val[0] (value and count) => true.
b: include 5+5=10 cnt2 matches dp_val[1]=10 cnt2 => true.
c: include 5+0=5 cnt1 matches dp_val[2] => true.
Groups: (10,2): indices 0 (a) and 1 (b); (5,1): index2 (c)
For key (10,2), indices sorted [0,1]; suffix min ID from i0: min(a,b)=a at idx0; from i1:b.
Reconstruction: s=0, target (10,2) -> idx_list [0,1]; i=0 -> best_idx=0 (a). selected a; s = next[0]=2; target_val=5, target_cnt=1.
Now (5,1): idx_list [2]; i=0 -> best_idx=2 (c). selected c. So ["a","c"]. Good.

Now, test for test4: a and b non-overlap: a(9-10),b(10-11). sorted: a index0,b index1. next: a-> first start>=10 -> b (index1). b-> next=n=2.
DP:
i=1 b: incl=10, cnt1; excl=0 => dp_val=10,cnt1.
i=0 a: incl=5+10=15 cnt2; excl=10 cnt1 => include better. dp_val=15,cnt2.
Eligible: a: include=5+10=15 cnt2 matches dp_val[0]? dp_val[0]=15,cnt2 => true. b: include=10+0=10 cnt1 matches dp_val[1]=10,cnt1 => true.
Groups: (15,2): index0; (10,1): index1.
Reconstruction: s=0, target (15,2) -> idx_list [0]; pos=0; best_idx=0 (a). selected a; s= next[0]=1; target_val=5? Wait, target_val becomes 15-5=10, target_cnt=2-1=1. Then target (10,1): idx_list [1]; pos=0; best_idx=1 (b) => selected b. So ["a","b"]. Good.

Now, for test10: two sessions overlapping (same times) a and b. Sorted: a (id a) index0, b (id b) index1 both start9 end10. next for both: end10, first start>=10 none, so next=2.
DP:
i=1 (b): incl=5,cnt1; excl=0 => dp_val=5,cnt1.
i=0 (a): incl=5,cnt1; excl=dp_val[1]=5,cnt1 -> tie (value,count equal). Our DP chooses exclude. So dp_val[0]=5,cnt1.
Eligible: both include conditions true because incl=5,cnt1.
Groups: (5,1): indices 0 and 1.
Reconstruction: s=0, target (5,1). idx_list [0,1]; pos=0; suffix min index from 0: indices 0 (a) and1 (b); min id = "a" at idx0. So picks index0 (a). So selected ["a"]. That matches expected. Good.

Now, test3: a (9-10,10), b(9:30-11,20). sorted: a index0, b index1. next: a end10, first start>=10 -> none? b start=9:30<10, so next=2; b next=2.
DP:
i=1 b: incl=20,cnt1; excl=0 => dp_val=20,cnt1.
i=0 a: incl=10,cnt1; excl=20,cnt1 => excl better. dp_val=20,cnt1.
Eligible: a: include 10 !=20 so false; b: include 20=cnt1 true.
Groups: (20,1): index1.
Reconstruction: s=0 target (20,1) -> idx_list [1]; i=0 -> best_idx=1 -> selected b. Works.

Now, test for count minimization with overlapping: a and b overlapping with higher value c, we did.

Now, test for case where two non-overlapping sessions have value 5 each, and another session overlapping both has value 11? For instance:
  a:9-10 value5
  b:10-11 value5
  c:9:30-10:30 value11
Then optimal value max=11 from c (count 1) vs a+b=10 count2. So we pick c. Our DP would yield that because include for c gives 11, exclude for a etc. Let's test quickly: sorted: a (0), c (1), b (2). Next: a->? end10, first start>=10: b (index2). c->end10:30, first start>=10:30? b start10 so no => n=3. b-> n=3.
DP: i=2 b: incl=5,cnt1; excl=0=>5 cnt1.
i=1 c: incl=11,cnt1; excl=5 cnt1 => incl better => 11 cnt1.
i=0 a: incl=5+5=10 cnt2; excl=11 cnt1 => excl better => 11 cnt1.
Eligible: a false; c true; b true.
Groups: (11,1): index1 (c); (5,1): index2 (b).
Reconstruction: s=0, target (11,1)-> picks c. So correct.

Now, we should test scenario where value 0 sessions exist but a positive session yields max value. Should not include 0 session. Already tested.

Now, think about scenario where there are multiple optimal solutions with same value and count but the lexicographically smallest list not captured because we assumed that the smallest ID for the first element is sufficient. But what if two eligible sessions have the same ID? Not possible. So fine.

Now, ensure that our reconstruction loop target_cnt decrement works even if max_value=0 and count=0. Then we skip loop. Good.

Now, we should test with integer IDs vs string IDs. In our validate, we enforce id is string. So okay.

Now, about the parsing of timestamps: We used fromisoformat and strptime. Could there be a timezone string like "2026-05-01T09:00:00Z"? fromisoformat in Python 3.11+ can parse it with tzinfo=UTC, but in 3.7 it will raise ValueError. Our fallback strptime with "%Y-%m-%dT%H:%M:%S" will not match because of the 'Z'. So it will return None, reject with reason "invalid start/end timestamp". That's acceptable because we require no timezone. So we reject Z suffix. Good.

Now, about microseconds: fromisoformat can parse; it returns datetime with microsecond. That's fine.

Now, we should test parse_dt with "2026-05-01T09:00" (no seconds). fromisoformat in 3.7 cannot parse that? Actually Python 3.7's fromisoformat requires the full format like "YYYY-MM-DDTHH:MM:SS" (with seconds). So "2026-05-01T09:00" would raise ValueError in 3.7. Our fallback strptime with "%Y-%m-%dT%H:%M" will parse it. So we support that. Good.

Now, also "2026-05-01T09:00:00.123456" fromisoformat works.

Thus, parse_dt is robust.

Now, about JSON output: The output should be printed to stdout. We'll use print.

Now, we need to ensure that if there is an error in reading input, we handle gracefully? Not required.

Now, about code length: We are around 300 lines maybe? Let's approximate: The solution part is about 150 lines, tests about 200 lines, total under 500. So well under 1000.

Now, we should also consider that we used `bisect` module. Imported.

Now, potential bug: In binary search for next_arr, we used `bisect_left(start_times, sessions[i].end)` which returns the first index where start >= end. For sessions that have end equal to start of another session, that's allowed. So good.

Now, for sessions with same start and end times? Not possible as end > start.

Now, we should also think about the case where multiple sessions have the exact same start, end, and value but different IDs. They overlap completely. Only one can be chosen. Our DP will pick the one with smallest ID if we tie-break? Actually in DP, we don't consider IDs. We just pick one arbitrarily (based on DP tie-breaking which may favor exclude). Ultimately, during reconstruction, our greedy will pick the smallest ID among eligible for that suffix. So if two sessions are identical, both will be eligible if they can be part of optimal solution (value, count same). Then groups will contain both; the smallest ID will be chosen. Good.

Now, about the order of reconstruction: We always pick the smallest ID first. But what about the order of the remaining? After we pick a session, we jump to next[best_idx]. That may skip some sessions that also have the same start but later IDs? But those are overlapping, so cannot be selected after. So it's fine.

Now, we could also run a sanity check: We can compute total value of selected_ids by summing sessions' values and compare to global_val. But not necessary.

Now, about the possibility that the DP might produce a solution that uses sessions with zero value to fill gaps? It would be disfavored because of count minimization. So not selected.

Now, I think algorithm is sound.

Now, we should test the code with some manual runs using Python. But since we can't run now, we'll trust.

Edge Cases to consider:

- If there are sessions with very large value sums; Python ints fine.

- If there are sessions where value is float; comparisons work.

- If global_val is float, target_val may be float. Keys in dict use floats. This can cause issues due to floating point precision when checking equality (e.g., 0.1+0.2 != 0.3). But values are likely integers from problem. We can assume they are int. In validate, we convert integer floats to int; if value is float like 5.5, it remains float. Then the equality dp_val[i] == sessions[i].value + dp_val[next_arr[i]] may be precise if all values are multiples of something? Could be dangerous. But problem uses "value" as integer in example. We'll assume integer values. To be safe, we could use a small epsilon for comparison? But since the values are presumably exact multiples, we can keep as is. But to avoid floating issues, we could convert all values to `int` if they are floats? Not always possible. But the problem says value is probably integer. We'll keep as provided; if they are floats, they should be exact.

Alternatively, we could use `math.isclose` but then lexicographic ordering would be messy. Given contest problem, likely integer values.

Thus, we'll keep as is.

Now, consider that dp_val[i] and value_i + dp_val[next[i]] may be float; equality check may fail due to rounding. We could convert to int if possible. But we'll assume.

I'll add a line in validate: if isinstance(value, float): if value.is_integer(): value = int(value). Already done. If value is non-integer float, we treat as float. Could be okay as long as sums are exact.

Now, if we are concerned about floating equality, we could use a tolerance in the eligibility condition and also in DP comparison. However, to keep it simple, we'll assume integers.

Now, about the `--test` flag: we check sys.argv[1]. However, if there are additional arguments, we ignore. Good.

Now, we should ensure that in test mode, we don't read from stdin. So we exit after tests.

Now, final code.

Potential small improvements:

- Use `functools.cmp_to_key` if needed but not.

- For large n, recursion depth not used.

Now, one more thing: In the eligible_include condition, we check `dp_val[i] == sessions[i].value + dp_val[next_arr[i]]` and `dp_cnt[i] == 1 + dp_cnt[next_arr[i]]`. But note that dp_val[i] might be achieved via exclude branch, but include branch also yields the same value and count? That's fine.

But what if include branch yields the same value but not the same count (higher count)? Then condition fails, correct.

Now, we must also consider that when include branch and exclude branch have same value and same count, the eligibility condition will be true for include (since it matches). Even though we stored exclude in DP, include still yields that value and count. So condition true.

Now, but there is a nuance: Suppose include branch yields value and count that are both optimal, but there is also an alternative exclude branch that also yields same value and count. Our eligible_include includes the session. That's correct.

Now, about the reconstruction step: We use groups_data for key. When we pick the first eligible (smallest ID), we assume that there exists a completion achieving the target. However, we must ensure that after picking that session, the new target (target_val - value_i, target_cnt-1) is exactly dp_val[next[i]] and dp_cnt[next[i]]. This is true by eligibility condition. Since we have stored only the info for the optimal suffix from next[i] exists, we can continue. But could it be that the suffix we need (lexicographically smallest) is not the one that the DP solution from next[i] uses? However, the DP suffix value and count for next[i] are fixed; there may be multiple ways to achieve that value and count; we will again pick the lexicographically smallest among them. So the process continues.

One more subtlety: What if there are multiple optimal solutions for the suffix that achieve the required value and count but have different structure; the lexicographically smallest overall list may not be formed by appending the lexicographically smallest suffix? Because the suffix's list sits after the first element, and lexicographic order compares first element then the rest. So if we fix the first element, the best we can do is the lexicographically smallest suffix list that completes the target. So recursive greedy works.

Thus correct.

Now, potential flaw: Our eligible_include condition ensures that there exists at least one optimal solution from i that includes i. But when we are at step with target (val, cnt) that is exactly dp_val[i] and dp_cnt[i], we are considering i as potential first element. However, note that we skip indices before s by s argument. At the first step s=0, we consider indices >=0. But we might encounter an index i that is eligible but its actual index i may be > some other index j (j < i) that also is eligible and has smaller ID. Since we search in index order and pick smallest ID via suffix min, we are fine. But is it possible that there is an eligible session i that, when selected, yields a solution that is not globally optimal because the suffix from next[i] might not have a solution achieving the remainder? Eligibility guarantees there exists at least one solution from next[i] achieving the remainder (dp_val[next[i]], dp_cnt[next[i]]). So it's okay.

But wait: eligibility condition only checks that include branch yields same value and count as dp_val[i]. This implies that there is an optimal solution from i that includes i. But does it guarantee that the suffix from next[i] will be able to achieve the remainder when combined with i? Yes, because it says value_i + dp_val[next[i]] == dp_val[i] and count_i+dp_cnt[next[i]] == dp_cnt[i]. Since dp_val[next[i]] is the max value from suffix, if we take that max, we get optimal. There may be other solutions from suffix with same value and count but not the one that dp_val refers to? But dp_val[next[i]] is the max value; any solution achieving that max and minimal count is acceptable. So there exists at least one. So fine.

Now, what about if there are multiple sessions with same ID? Not considered.

Now, I think we are ready.

Now, consider case where there are sessions with start exactly equal to end of previous, but the DP includes both; but there could be alternative optimal solution that includes a different set for the same value and count. Our reconstruction will pick lexicographically smallest.

Now, test scenario that may break the "lexicographically smallest" assumption: Suppose we have two eligible first sessions: session A (id "a") and session B (id "b"). For A, the remainder optimal (lexicographically smallest completion) is list L_A; for B, it's L_B. If we pick A first, overall list = ["a"] + L_A. If we pick B first, = ["b"] + L_B. Since "a" < "b", we prefer A regardless of L_A vs L_B. So we need to pick A if it is eligible (i.e., there exists some optimal solution starting with A). That's what we do. So we choose smallest ID among eligible first elements.

Now, what if there is an older eligible session with ID "c" that is not the smallest ID but leads to a remainder that is empty? No.

Now, one more potential edge: In some scheduling problems, the lexicographic smallest list of IDs when sorted by start time may require that we consider not only the first element ID but also the start time order? For example, two sessions with same start time but different IDs; the one with smaller ID is better. If there is a session with a later start but smaller ID than an earlier session's ID, but if we skip the earlier session, the later session could be the first element now, and its ID may be smaller. Our algorithm will consider that later session as eligible for first (since it is earlier in start order? Actually if session j has a later start than session i but i is earlier in start order, then i has index < j. For j to be eligible for first, we need dp_val[j] == global_val and dp_cnt[j] == global_cnt, meaning that we can achieve global optimum without using any sessions before j. This may or may not be true. If it is true, then j is eligible and its ID might be smaller than i's ID. Since we scan all indices and choose smallest ID among those with index >= s, and s=0 initially, we will consider both i and j. We choose smallest ID overall. That could be j if its ID is smaller. So algorithm works.

Now, check if dp_val[j] == global_val could happen even if there is an earlier session i that is also eligible? Yes, it's possible that skipping all earlier sessions still yields global optimum. For example, earlier sessions may have value 0 or not needed. So later eligible sessions with smaller ID can be chosen. This yields lexicographically smaller list because first element ID is smaller. So correct.

Thus, algorithm is correct.

Now, time to write code.

One more nuance: In the groups_data, we store suffix min arrays. The indices list sorted by index. For the binary search, we use bisect_left on that indices list to get position. Since suffix min is computed over that list from that position onward, it gives the smallest ID among all indices >= lower bound. However, we should ensure that the suffix min_idx we get is indeed an index >= s. Since we start from first index >= s, and suffix min considers all indices thereafter, it's fine.

But what if the first index >= s (say index=5) has ID "z", and later there is index=6 with ID "a". Suffix min at position i where we include index5 will have min ID = "a" from index6, so best_idx=6. That's >=5, so fine.

Now, We must also ensure that after we pick best_idx, the new s = next_arr[best_idx] might be less than next element's index? That's fine.

Now, we should also consider the possibility that next_arr[best_idx] could be less than some indices that were skipped? No, because next_arr[best_idx] is the first start >= end, which is greater than best_idx? Not necessarily; it could be less than best_idx? Since start_times are monotonic, next_arr[i] >= i+1? Actually can be i+1 or greater. But could it be less than i if end_i <= start_i+1? No, because next_arr[i] is an index in the sorted list which is >= i because we are looking for starting after end_i, and since sessions are sorted by start, end_i > start_i, so the session i itself has start < end_i, so next_arr[i] cannot be i; must be > i because start_i < end_i and start list is increasing, so first with start >= end_i will be after i (since start_i < end_i). So next_arr[i] > i always. So s increases.

Now, after we pick best_idx, s = next_arr[best_idx] > best_idx. So we only move forward.

Now, none of the earlier indices (before s) will be considered again. So the reconstruction will process each session at most once. And the number of steps equals number of selected sessions.

Now, we also need to ensure that the target value is correct after subtraction. Since we rely on eligibility, target_val - value_i = dp_val[next[i]] exactly.

Now, we should also handle if target_val - value_i becomes negative? Impossible because value_i <= target_val since include branch achieves target.

Now, about the case where global_val=0 and global_cnt=0: we skip loop, selected_ids empty.

Now, we also need to consider that eligible_include for a session might be true but its next_arr index might point beyond n, which is fine.

Now, we need to check if there might be a situation where groups_data for a key has indices but none of them have index >= s (e.g., s passed all). Then binary search returns len(idx_list). Then we break. That shouldn't happen if target is achievable.

Now, also we should consider that after picking a session from a key, the new target may be for a different key that may not have groups_data. That would indicate inconsistency; but by eligibility it should exist.

Now, let's also test with scenario where there are multiple sessions but the optimal solution selects zero sessions (global_val=0). Then dp_cnt[0]=0. So while loop not entered. selected_ids empty. Works.

Now, another test: Suppose there are sessions with value 0 that are the only sessions, but they are not selected because we minimize count. So global_val=0, global_cnt=0. selected empty.

Now, about rejected: The rejected list contains id and reason. In case id is missing, we used "unknown". Good.

Now, we should ensure that we use `sess.get('id', 'unknown')` when creating rejected. In validate_session, we return error if id missing or not string, so sess.get('id') may still exist but invalid. In that case, we want to include the id (if any) or 'unknown'. So in the rejected list, we use `sess.get('id', 'unknown')`. But if id is not a string, we still use it; but our validation already checks isinstance(sid, str) and if not, returns error. In that case, the id might be some value. For consistency, we'll use `sess.get('id', 'unknown')` regardless. But if id is integer, it will be included as integer. That's fine. In the output, it might be integer. Problem expects ID strings? Example shows strings. Possibly fine.

But since we reject if id not string, we may have already enforced that only sessions with string id are considered valid. However, we still add rejected entries for those with non-string id. Their id may be integer. We'll keep as is. It's acceptable.

Now, we must crucially ensure that the `max_value` output is exactly the sum of values of selected sessions. Since we use global_val from DP, it's correct.

Double-check DP: It's standard.

Now, potential issue: In the DP we used dp_cnt as minimal count for max value. We counted number of sessions. Are we counting sessions correctly? For include, count = 1 + dp_cnt[next[i]]. That's the number of sessions in that branch. For exclude, count = dp_cnt[i+1]. So we pick min count for same value. That's correct.

Now, tie-breaking on count vs. value: We chose the minimal count for max value. Good.

Now, about eligible_include: if include branch produces optimal value and count (i.e., equal to dp_val[i] and dp_cnt[i]), then we mark eligible. But note: what if include branch produces same value but dp_cnt[i] is the minimum count, but that minimum count is achieved by both include and exclude? Then both have same count, so condition holds. So that's fine.

Now, what if include branch produces same value and same count as dp_val[i] but the optimal solution from next[i] might have multiple ways with different ID lists; our later greedy picks the smallest ID among those. That's fine.

Now, final step: Write code as described.

Now, we must also consider that the ordering of the selected_ids list is as per start time. Since we always pick sessions in increasing start order (since s increases to next of chosen, which is beyond its end, and start times are increasing), the list will be chronological. For sessions with equal start times, the sorting by (start,end,id) ensures a deterministic order, and since we never pick two sessions with same start time (they would overlap), it's fine.

Now, about the output: we should be careful that JSON keys are exactly "max_value", "selected_ids", "rejected". Use those.

Now, we are ready to produce final code.

But before writing, let's test parsing of dates with our parse_dt:

- "2026-05-01T09:00:00" -> fromisoformat works.
- "2026-05-01T09:00" -> fromisoformat fails (in Python 3.7), falls back to strptime "%Y-%m-%dT%H:%M" works.
- "2026-05-01T09:00:00.123456" -> fromisoformat works.
- "2026-05-01T09:00:00Z" -> fromisoformat (in 3.7 fails because 'Z' not supported) -> fallback strptime fails -> returns None -> reject.
- "2026-05-01T09:00:00+00:00" -> fromisoformat in 3.7 may raise? Actually in 3.7, it may try to parse timezone offset but it's not supported? I think it raises. So fallback fails. reject. Good.
- "2026-05-01T09:00:00.123+00:00" similarly.

Thus acceptable.

Now, final check on the test for reject: We have async.

Now, about readability: We'll keep code as is.

Potential performance issue: The loop for building groups: for i in range(n): if eligible[i]: groups.setdefault(key, []).append((i, sessions[i].id)). This is O(n). Then sorting each group by index could be O(n log n). That's fine.

Now, one more nuance: In groups_data, we computed suffix min arrays. But we used `suf_min_id` and `suf_min_idx`. These need to be stored as lists of same length as indices list. That's fine.

Now, the reconstruction loop uses `bisect_left(idx_list, s)`. idx_list is a list of ints (indices). This works.

Now, we should test a case when s is exactly equal to an index in idx_list. Then bisect_left returns that position. Good.

Now, we also should consider that after picking best_idx, we set s = next_arr[best_idx]. This may be a number that could be larger than any index in the next key's idx_list. Then bisect_left returns len(idx_list), loop breaks. That's expected when target_cnt becomes zero.

Now, we set target_cnt -= 1. After last session, target_cnt becomes 0. So loop condition fails.

Now, we should also consider that after subtracting value, target_val might become 0 but target_cnt > 0? Not possible if eligibility holds (value and count linked). But if something goes wrong, we break.

Now, to be defensive, we could also check target_val > 0 in while condition, but target_cnt is enough.

Now, we'll implement.

Now, we must ensure we imported datetime correctly.

Now, we need to think about timezone-naive comparisons; all datetimes are naive.

Now, one more thing: The problem says "Parse ISO-like timestamps without time zones using Python standard library." We did.

Now, final verification with a more complex test: Suppose sessions with IDs that are not in alphabetical order but we need lexicographically smallest list. Our algorithm seems to produce that.

Now, all seems good.

Now, compile the final answer.

One more potential bug: In the DP, for sessions where include and exclude equal value and count, we choose exclude. Later, eligible_include may still be true for include branch. But what if there is a session where include branch yields the same value and count as exclude, but the exclude branch's solution comes from later indices, while include branch's solution uses a different set of sessions that might have a different ID list? Our eligible_include includes it. That's correct because there exists an optimal solution including it.

Now, but consider that for the suffix from i, both include and exclude are optimal. We have dp_val[i] and dp_cnt[i] representing the optimal value and count (which are same for both). In reconstruction, when we are at some step with target equal to dp_val[i] and dp_cnt[i], we consider both indices i and maybe later indices? i itself is eligible if include branch yields dp_val[i]. But if exclude branch yields dp_val[i] but include branch does not yield dp_cnt[i]? No, we said both yield same value and count. So include branch eligible as well. So i is a candidate. But we also have later indices j that might be eligible for the same target. Among them, we choose smallest ID. That's fine.

Now, but is it always true that if we exclude session i, we can still achieve the global optimum using only later indices? That's precisely dp_val[i] == dp_val[i+1] and dp_cnt[i]==dp_cnt[i+1]. That would mean that i is not needed. In that case, i itself might not be eligible because include branch may not match dp_cnt? Actually if include also yields same value and count, then i is eligible. But if exclude yields same, then i may be redundant. Yet it's still eligible as a candidate for first element (since you could include i and still get optimal). But if there is later session with smaller ID, that later session might be chosen, skipping i. So algorithm still works.

Now, consider a case where the first eligible session under the global target has a certain ID, but its inclusion leads to a suffix where the lexicographically smallest completion is not the same as the overall lexicographically smallest if we had chosen a later first session? But as argued, first element dominates. So we choose smallest ID. So no issue.

Now, we also should consider the scenario where two sessions have same ID? Unlikely.

Now, we are ready to write final code.

But wait: What if there are multiple sessions with the same (start, end) but different IDs, and they both are eligible and have the same ID? Not possible.

Now, we should also test case where the optimal solution may include a session that has zero value but is needed to achieve max value? If value is zero, it doesn't increase value. So no.

Thus, final code.

I'll write the final answer accordingly.

New: I've realized that in the eligibility condition we used `dp_val[i] == sessions[i].value + dp_val[next_arr[i]]` and `dp_cnt[i] == 1 + dp_cnt[next_arr[i]]`. But what if `next_arr[i] == n`? Then dp_val[n]==0 and dp_cnt[n]==0. Works.

Now, one more nuance: In the DP, when we have equal value and equal count, and we choose exclude, it's fine. But later, for eligibility, we rely on include branch having the same count. That may be true or not. In equal value case if include count > exclude count, include not eligible. That's correct.

Now, final code.

I'll produce the final answer.
````

## Assistant

````markdown
```python
import sys
import json
import datetime
import bisect

class Session:
    __slots__ = ('id', 'start', 'end', 'value')
    def __init__(self, id_, start, end, value):
        self.id = id_
        self.start = start
        self.end = end
        self.value = value

def parse_dt(s):
    """Parse an ISO-like timestamp without timezone information."""
    if not isinstance(s, str):
        return None
    # Try fromisoformat (Python 3.7+)
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is not None:
            return None
        return dt
    except ValueError:
        pass
    # Fallback formats (without timezone)
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return dt
        except ValueError:
            continue
    return None

def validate_session(sess):
    """Validate a session dict and return a (Session, None) or (None, reason)."""
    if not isinstance(sess, dict):
        return None, "invalid session object"
    sid = sess.get('id')
    if not isinstance(sid, str):
        return None, "missing or invalid id"
    start_str = sess.get('start')
````
