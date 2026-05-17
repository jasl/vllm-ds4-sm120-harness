# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-v4-flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: expectation checks skipped
- Detail: `expectation checks skipped`
- Elapsed seconds: 28.191983
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "completion_tokens": 2790, "total_tokens": 2942, "prompt_tokens_details": {"cached_tokens": 128}, "completion_tokens_details": {"reasoning_tokens": 581}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 24}`
- Prompt tokens: 152
- Completion tokens: 2790
- Total tokens: 2942

## Prompt

```markdown
Write an 800–1,000 word technical article for backend engineers titled by you. Topic: designing rate limiting for a multi-tenant API used by small teams and enterprise customers.

You must cover:
1. The difference between authentication, authorization, quotas, and rate limits.
2. Token bucket vs. fixed window vs. sliding window at a practical level.
3. How to avoid punishing an entire tenant for one noisy integration.
4. What headers and error messages should be returned to API clients.
5. Observability: metrics, logs, and alerts that show whether limits are protecting reliability without blocking legitimate use.

Constraints: no code; no vendor-specific services; include a short “recommended baseline design” section at the end.
```

## Reasoning Content

```text
We need to write a technical article for backend engineers, 800-1000 words, on designing rate limiting for multi-tenant API. Must cover 5 points. No code, no vendor-specific services. Include a recommended baseline design section at the end.

Structure: Title, introduction, then sections for each point. Ensure word count. Need to be practical, technical but not too abstract.

I'll write an article with a title like "Rate Limiting for Multi-Tenant APIs: Balancing Fairness, Reliability, and Observability". Then cover each point in order.

Point 1: Difference between auth, authz, quotas, rate limits. Explain clearly: authentication (who), authorization (what they can do), quotas (total usage over period), rate limits (rate of requests per time unit). Emphasize that rate limiting is about protecting system resources, not business logic.

Point 2: Token bucket vs fixed window vs sliding window. Practical level: Token bucket allows bursts, fixed window has boundary issues, sliding window smooths. Token bucket good for absorbing spikes but requires careful sizing. Fixed window simple but can cause thundering herd at window boundaries. Sliding window more accurate but more complex to implement. Discuss trade-offs.

Point 3: Avoiding punishing entire tenant for one noisy integration. Use granularity: per-API-key or per-endpoint limits within tenant. Or distribute tenant's overall limit across its integrations via hierarchical token buckets or weighted fair queuing. Also consider debt collection or penalty boxes for specific noisy keys.

Point 4: Headers and error messages. Standard headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset. For errors: 429 Too Many Requests with Retry-After header. Body should include clear message: which limit exceeded, when it resets, maybe link to docs. Also consider including per-tenant vs per-key limits.

Point 5: Observability. Metrics: request rate per tenant, per endpoint, 429 count, latency, error rate. Logs: structured logs with tenant ID, key ID, endpoint, decision (allowed/blocked), remaining capacity. Alerts: aggregate 429 rate above threshold, individual tenant hitting limit frequently, latency spikes due to rate limiter contention. Also track capacity utilization to see if limits are too generous or too strict.

Recommended baseline design: Use token bucket per tenant, with sub-buckets per API key (or integration). Sliding window for global rate limiting to avoid sharp edges. Return standard headers. Log decision events. Alert on 5% of requests rejected for any tenant. Monitor P99 latency of rate limiter.

Keep tone professional, technical, but accessible. No code. We'll focus on concepts and design decisions.

Word count: target 900. Write concisely.

Let me draft.
```

## Assistant

````markdown
# Rate Limiting for Multi-Tenant APIs: Balancing Fairness, Reliability, and Observability

Backend engineers designing APIs for a mixed audience of small teams and enterprise customers quickly learn that one-size-fits-all rate limiting leads to chaos. Small teams need room to experiment; enterprise customers demand predictable throughput for dozens of integrations. The goal is not merely to cap traffic, but to allocate finite infrastructure fairly while preserving reliability. This article walks through the core distinctions, practical algorithm trade-offs, techniques to avoid tenant‑level punishment, client‑friendly response patterns, and the observability needed to tune the system without guessing.

## 1. Authentication, Authorization, Quotas, and Rate Limits – What’s What?

These four concepts are often conflated, but they serve distinct purposes.

- **Authentication** verifies *who* the client is (e.g., an API key or OAuth token). It answers “Are you whom you claim to be?”
- **Authorization** determines *what* that client is allowed to do: which endpoints it can reach, which resources it can read or write.
- **Quotas** enforce a *total usage allowance* over a long period – usually a month or a billing cycle. They are business constraints: “You may make 1,000,000 calls this month.” Exceeding a quota may result in an error or an upsell prompt.
- **Rate limits** govern the *rate* of requests over a short window (seconds or minutes). They protect the system from traffic surges, misconfigured clients, or accidental loops. A client can have a high quota and a low rate limit (e.g., 1M calls/month but only 100 requests/second).

In a multi‑tenant system, rate limits are the first line of defense. They should always be enforced before quota checks, because a burst of traffic can overwhelm shared infrastructure even if the tenant’s monthly allowance is far from exhausted.

## 2. Algorithm Choice: Token Bucket vs. Fixed Window vs. Sliding Window

All three algorithms can work, but their practical behaviors differ under bursty, multi‑tenant workloads.

### Fixed Window
Divide time into discrete windows (e.g., 1 minute). Count requests per window; if the count exceeds the limit, block until the next window starts.
**Pros:** Extremely simple to implement with a single counter per tenant.
**Cons:** Bursts at the boundary of two windows can double the allowed throughput (a “thundering herd” effect). A tenant that hits the limit exactly at the end of a window and again at the start of the next window can generate 2× the allowed rate. This unpredictability frustrates both small teams and enterprise clients.

### Sliding Window Log
Maintain a time‑ordered log of recent request timestamps per tenant. At each request, discard timestamps older than the window length and count the remaining ones.
**Pros:** Smooth, accurate rate enforcement – no boundary spikes.
**Cons:** Memory and time overhead grow with the window length and the number of active tenants. For a long window (e.g., 1 minute) and a high‑volume tenant, the log can be large. Typically acceptable if pruning is efficient.

### Sliding Window Counter
A hybrid: break the window into smaller sub‑intervals (e.g., 10‑second buckets for a 1‑minute window). Track counters per bucket. The current effective count is a weighted sum of the current bucket and the previous bucket(s).
**Pros:** Good accuracy with bounded memory and O(1) updates.
**Cons:** Slightly more complex than fixed window; still a small approximation error.

### Token Bucket
A bucket holds a fixed number of tokens. Tokens are added at a constant rate (the “refill rate”). Each request consumes a token; if the bucket is empty, the request is denied.
**Pros:** Natural burst handling – unused tokens allow short bursts up to the bucket size. Very intuitive for developers.
**Cons:** Without careful tuning, a tenant can accumulate tokens and then unleash a large burst that overwhelms downstream services. In practice, the bucket size is set to a small multiple of the sustained rate (e.g., 2× the per‑second rate).
**Recommendation for multi‑tenant:** Token bucket scales well per tenant and per API key. It is my first choice when bursts need to be allowed but bounded.

## 3. Avoiding Tenant‑Level Punishment for One Noisy Integration

Enterprise tenants often have many API keys (one per internal service, team, or integration). A single misbehaving key should not degrade the service for the rest of the tenant. This requires **hierarchical rate limiting**.

- **Per‑tenant global limit** (e.g., 5,000 requests/second) acts as a hard cap.
- **Per‑key sub‑limits** (e.g., 1,000 requests/second per key) prevent one integration from consuming the entire tenant budget.

Implementation approaches:

- **Hierarchical token buckets:** Each key has its own bucket, and a parent bucket enforces the tenant total. If the key’s bucket is empty, requests are still allowed if the tenant bucket has tokens, but this defeats the isolation goal. Instead, the key’s bucket is the primary gate, and the tenant bucket acts only as a backstop.
- **Weighted fair queuing:** Assign weights to keys based on historical usage or explicit priority. Requests are scheduled to share the tenant’s capacity fairly.
- **Debt tracking:** When a key exceeds its sub‑limit, it accrues “debt” that must be repaid before its next requests are allowed. Meanwhile, other keys enjoy full capacity.

Additionally, a noisy key should be flagged for monitoring, but automated enforcement should remain per‑key. Alerts on sustained 429 responses from a single key help operators contact the enterprise before the tenant’s support team escalates.

## 4. Headers and Error Messages

Clients need clear information to adapt their behavior. The standard set recommended by IETF (RFC 6585) is:

- `X-RateLimit-Limit` – the maximum requests allowed in the current window (e.g., `100`).
- `X-RateLimit-Remaining` – how many requests the client can still make.
- `X-RateLimit-Reset` – Unix timestamp (or seconds until reset) when the window/bucket refills.

For a multi‑tenant API, consider returning **both** the per‑key and per‑tenant limits so that clients can differentiate which cap they hit. Example:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 50
X-RateLimit-Reset: 1625097600
X-Tenant-RateLimit-Limit: 5000
X-Tenant-RateLimit-Remaining: 4500
```

When a request is rejected, return HTTP 429 Too Many Requests with a `Retry-After` header (in seconds). The response body should be a structured JSON object:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded the rate limit. Retry after 15 seconds.",
    "type": "key_level",   // or "tenant_level"
    "retry_after_seconds": 15
  }
}
```

Include a link to documentation for further help. Plain‑text error messages cause confusion in automated integration tests; structured errors are parsed reliably by clients.

## 5. Observability: Metrics, Logs, and Alerts

A rate limiter that silently blocks traffic is dangerous. Observability must answer: “Is my rate limiting protecting the system or choking legitimate use?”

### Metrics (expose to a time‑series database)
- **Requests per second (RPS) by tenant, by endpoint, by decision** (allowed / throttled / quota‑exhausted).
- **Rate‑limit latency** – the time spent in the rate‑limiting logic itself. High latency here can indicate a slow data store or an inefficient algorithm.
- **Capacity utilization** – average and peak tokens remaining per bucket. If most buckets are near empty most of the time, limits may be too tight.
- **Throttle ratio** – percentage of requests rejected per tenant. A ratio above 5% for a non‑malicious tenant is a red flag.

### Logs (structured, sampled if necessary)
Each rate‑limiting decision should emit a log line with tenant ID, API key ID, endpoint, counter values, decision (allow/deny), and remaining capacity. This helps in post‑mortems and debugging customer complaints.

### Alerts
- **Aggregate throttle rate** > 5% across all tenants – system may be under‑provisioned.
- **Single tenant throttle rate** > 10% – likely a misconfigured client or a bug.
- **Rate‑limiter latency P99** > 10ms – algorithmic or infrastructure bottleneck.
- **No rate‑limiting activity** for a previously active tenant – could indicate a client that stopped retrying or a bug in the limiter.

Tie these alerts to on‑call response protocols. A well‑instrumented rate limiter becomes a source of truth for capacity planning: if limits are constantly hit, it’s time to scale infrastructure or adjust pricing.

## Recommended Baseline Design

Start with a **per‑tenant token bucket** using a sliding window counter (to avoid boundary spikes). Each tenant gets a bucket size of 2× their sustained request rate (e.g., for 100 req/s, bucket = 200 tokens, refill = 100 tokens/s). Within the tenant, enforce **per‑API‑key sub‑limits** using the same algorithm, where each key’s bucket size is 20–30% of the tenant bucket (adjust based on number of keys).

Return the standard headers plus a `X-Tenant-RateLimit-*` set. Log every decision with tenant and key identifiers. Monitor throttle ratio per tenant; alert if it exceeds 5% for more than 5 minutes. Review utilization weekly – if any tenant’s bucket is empty for more than 10% of the time, consider raising its limit (or asking the customer to upgrade).

This design scales from a single small team with one API key to an enterprise with hundreds of internal services. It protects reliability without punishing innocent integrations, and it gives operators the visibility they need to keep the system fair.
````
