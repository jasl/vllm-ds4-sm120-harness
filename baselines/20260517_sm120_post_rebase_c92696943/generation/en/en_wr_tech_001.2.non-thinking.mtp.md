# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 18.424362
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 3016, "completion_tokens": 2864, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2864
- Total tokens: 3016

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

## Assistant

````markdown
# You Shall Not Pass... Too Much: Designing Rate Limits for Multi-Tenant APIs

**By: The Backend Architect**

Every backend engineer eventually faces the same sobering realization: your API is a shared resource, and one noisy tenant can ruin the experience for everyone else. When your customers range from solo developers at a two-person startup to enterprise teams running thousands of automated integrations, the rate-limiting design becomes a balancing act between fairness, reliability, and usability.

This article walks through the practical decisions you must make when designing rate limits for a multi-tenant API. We'll clarify the terminology, compare algorithms, discuss tenant isolation, define proper error responses, and build an observability strategy—all without vendor-specific services or code.

---

## 1. The Four Pillars: Authentication, Authorization, Quotas, and Rate Limits

Before designing anything, ensure your team shares a precise vocabulary. These four concepts are often conflated, but they serve distinct purposes:

- **Authentication** answers *"Who is making this request?"* It verifies identity via API keys, OAuth tokens, or mTLS certificates. Authentication happens first; without it, no further checks apply.

- **Authorization** answers *"Is this requester allowed to perform this action?"* It checks permissions—read vs. write, access to specific resources, team vs. admin scopes. Authorization fails even if the request is authenticated and within rate limits.

- **Quotas** are hard, non-negotiable limits on total usage over a billing period (e.g., "10,000 API calls per month"). Exceeding a quota results in a denied request or, at minimum, a prompt to upgrade. Quotas are *accounting* boundaries.

- **Rate limits** are short-term, dynamic constraints that protect system resources from bursts. They answer *"How fast can you send requests right now?"* Rate limits reset in seconds or minutes, not months. They are *operational* boundaries.

Conflating quotas with rate limits leads to brittle designs: a quota-enforced system struggles to handle a burst of 1,000 requests in one second, even if the monthly total is fine. Conversely, a rate-limited system without quotas allows infinite requests as long as they trickle in—which is economically unsustainable for a paid API.

---

## 2. Algorithm Showdown: Token Bucket, Fixed Window, Sliding Window

### Fixed Window

The simplest approach: divide time into discrete windows (e.g., 1 minute) and count requests per tenant. If a tenant exceeds 100 requests in minute 12, they are blocked until minute 13.

**Practical problem:** The "burst at boundary" effect. A tenant sends 100 requests at 11:59:59 and another 100 at 12:00:01. The system sees 200 requests in two *consecutive* seconds, even though the per-minute limit was 100. This causes false positives for reliability while letting through traffic that stresses your backend.

**Verdict:** Easy to implement but dangerous for real-world burst control. Use only as a coarse pre-filter.

### Sliding Window Log

Maintain a timestamped log of each request per tenant. When a new request arrives, count all timestamps within the last window duration (e.g., last 60 seconds). If count exceeds the limit, reject.

**Practical problem:** Memory overhead. For high-throughput tenants, storing every request timestamp (even as a compact integer) becomes expensive. Also, the count operation can be slow if the log is long. This algorithm is precise but rarely worth the cost for high-performance APIs.

**Verdict:** Overkill for most multi-tenant APIs. Avoid unless you need perfect accuracy for compliance reasons.

### Sliding Window Counter (Approximate)

A hybrid: divide time into small sub-windows (e.g., 10-second buckets). Track counts per sub-window. For a new request, compute a weighted sum of the current sub-window and the trailing portion of the previous one. This approximates a true sliding window without storing every request.

**Practical problem:** Slight under- or over-counting due to approximation (usually within 5–10%). Acceptable for most use cases.

**Verdict:** The sweet spot for accuracy vs. resource cost. Recommended for production systems.

### Token Bucket

A bucket holds N tokens, replenished at a fixed rate (R tokens per second). Each request consumes one token. If the bucket is empty, the request is rejected or delayed.

**Practical analogy:** a leaky faucet filling a cup. You can save up tokens during idle periods, then spend them rapidly during bursts—up to the bucket size.

**Practical problem:** Configuration is less intuitive. You must decide burst size (bucket capacity) and steady-state rate (refill rate). A tenant that never bursts will never use its full allowance, leading to underutilization of your capacity planning.

**Verdict:** Excellent for absorbing natural bursts (e.g., a developer running a script that makes 50 rapid calls then goes silent). Prefer this when you can tolerate variable latency and want to incentivize "burst and then rest" patterns.

### Recommendation for Multi-Tenant APIs

Use **token bucket for bursty workloads** (most small teams) and **sliding window counter for steady-state traffic** (enterprise batch jobs). Implement both as middleware layers, not mutually exclusive choices. Some tenants may even negotiate which algorithm applies to their API key.

---

## 3. Avoiding the "Noisy Neighbor" Problem

A single integration—say, an enterprise's misconfigured CI/CD pipeline—can fire 10,000 requests per second. Without tenant isolation, that burst exhausts the shared rate-limit pool, blocking all other tenants.

**The cardinal rule:** Rate-limit per tenant, not per global endpoint. Use the tenant identifier (usually an API key or JWT claim) as the key for your counter or bucket.

But even per-tenant limiting isn't enough if the noisy tenant shares infrastructure with others. Consider these layers:

1. **Hard per-tenant limit:** Cap each tenant at a maximum requests-per-second based on their plan. This is non-negotiable. Enterprise plans get higher caps; small teams get lower ones.

2. **Fair queuing:** Route requests through a queue that gives each tenant a weighted fair share of processing capacity. If one tenant is overloaded, their requests wait longer, but other tenants' requests proceed without queuing behind them.

3. **Concurrency limiting:** Rate limits control *arrival rate*. Concurrency limits control *in-flight requests*. A noisy tenant might stay within rate limits but hold 500 connections open simultaneously, exhausting your connection pool. Limit each tenant to a maximum number of concurrent requests (e.g., 10 for small teams, 100 for enterprises).

4. **Priority lanes:** For enterprise tenants with SLAs, dedicate a small pool of worker threads or a separate request queue that bypasses the shared contention. This ensures that even if the shared pool is overwhelmed by a noisy tenant, premium customers still get through.

5. **Graceful degradation:** When a tenant exceeds its rate limit, do not immediately drop all its requests. Return `429 Too Many Requests` for the burst, but allow a trickle of requests to succeed (e.g., 1 request per second) so the tenant can at least poll for status updates or gracefully degrade their own logic.

---

## 4. Headers and Error Messages: The API Contract

Your clients cannot debug rate-limiting issues without clear signals. Every response (success or failure) should carry rate-limit headers. Every failure should include a machine-readable error body.

### Required Headers

| Header | Purpose | Example |
|--------|---------|---------|
| `X-RateLimit-Limit` | Maximum requests allowed per window | `100` |
| `X-RateLimit-Remaining` | Requests remaining in current window | `42` |
| `X-RateLimit-Reset` | Unix timestamp when the window resets | `1681234567` |

If using a token bucket, consider returning `X-RateLimit-BurstCapacity` and `X-RateLimit-RefillRate` so clients can model their throttling logic.

### 429 Response Body

```json
{
  "error": {
    "type": "rate_limit_exceeded",
    "message": "You have exceeded your rate limit of 100 requests per minute. Please wait 23 seconds before retrying.",
    "retry_after_seconds": 23,
    "quota": {
      "plan": "team_pro",
      "limit": 100,
      "remaining": 0,
      "reset_at": "2024-08-01T12:00:00Z"
    }
  }
}
```

- `retry_after_seconds` is critical for clients that do not parse unix timestamps.
- Include the plan name and current quota state so users understand *which* limit they hit (rate vs. quota).
- Never expose internal details like "worker pool exhausted." Keep error messages user-friendly.

### What About Headers for Concurrent Requests?

Optionally add `X-ConcurrencyLimit-Limit` and `X-ConcurrencyLimit-Remaining` to inform clients about in-flight request capacity.

---

## 5. Observability: Proving Your Limits Work

Your rate limiter is not a "set and forget" component. You must monitor it to confirm it protects reliability without blocking legitimate traffic.

### Metrics to Track (per tenant and globally)

- **Request count per interval** – baseline traffic.
- **Requests throttled (429s) per tenant** – ratio to total requests. A sudden spike indicates a misconfigured client, not just heavy usage.
- **Average and P99 latency before rate limit check** – if the check itself becomes a bottleneck, your limiter is too slow.
- **Concurrent request count per tenant** – correlates with connection pool exhaustion.
- **Rate limit check duration** – the overhead of your algorithm. If >1ms per request, consider optimizing storage (e.g., local in-memory instead of Redis for low-cardinality keys).
- **Global saturation** – e.g., "percentage of total capacity consumed across all tenants." If this exceeds 80% during peak, you need to provision more backend resources or tighten limits.

### Logs

- **Every 429 response** should log the tenant ID, endpoint, reason (rate vs. concurrency vs. quota), and the current limit state.
- **Do NOT log every accepted request** at the rate-limit layer—too noisy.
- **Log rate limit configuration changes** (e.g., "tenant A limit changed from 100 to 200 req/min") so you can correlate changes with support tickets.

### Alerts

- **Alert on per-tenant throttling rate > 10%** – means a tenant is consistently hitting limits. Either they need a higher plan, or your limits are too tight.
- **Alert on global throttling rate > 5%** – indicates systemic capacity pressure. Your rate limiter is working (blocking traffic), but you should scale horizontally.
- **Alert on rate limit check latency > 10ms P99** – your limiter is slowing down every request. Investigate storage backend contention.
- **Alert on concurrency limit near 100% for any tenant** – that tenant is holding connections. They may need a dedicated pool or a client fix.

### Dashboards

Create a single pane showing:
- Top 5 most throttled tenants (by absolute count).
- Top 5 tenants by concurrency (by active connections).
- Global request rate vs. global rate limit capacity (line chart with horizontal threshold).
- Rate limit algorithm health (storage latency, cache hit ratio).

---

## Recommended Baseline Design

For a multi-tenant API serving small teams and enterprises:

1. **Hierarchy of limits:** Rate limit (token bucket, per tenant) -> concurrency limit (per tenant) -> quota (per billing period). Check in this order: rate limit first (fastest to reject), then concurrency (protects resources), then quota (business enforcement).

2. **Algorithm:** Token bucket for flexibility. Burst capacity = 2x the per-second rate. Refill rate = per-second rate. Example: a "Pro" tenant with 100 req/min gets bucket capacity of 200 and refill of ~1.67 req/sec. This allows natural bursts while capping sustained throughput.

3. **Storage:** In-memory counters for low-cardinality tenants (≤ 100 active tenants). Use a distributed cache (like Redis) for large-scale deployments, but only if latency is acceptable. For many backends, local memory with atomic operations is sufficient because the rate limit is per tenant, not global.

4. **Isolation:** Hard per-tenant limits. Additionally, enforce concurrency limits using a semaphore-like pattern. Route enterprise tenants through a separate queue or worker pool with higher priority.

5. **Headers and errors:** Always return `X-RateLimit-*` headers on success and failure. Use a consistent error format with `retry_after_seconds` and plan context.

6. **Observability:** Expose throttle count per tenant as a Prometheus gauge; log every 429; alert when any tenant's throttle rate exceeds 10% over a 5-minute window. Review dashboards weekly for tenants that consistently bump against limits—they are candidates for plan upgrades.

Rate limiting is not about being mean to your users. It's about ensuring that the one team running a `for` loop without a sleep call does not take down the API for the startup that just raised a Series A. Design with empathy, measure with rigor, and your multi-tenant API will survive the noisy neighbor.
````
