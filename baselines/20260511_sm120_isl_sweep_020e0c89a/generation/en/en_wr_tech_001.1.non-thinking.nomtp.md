# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 25.998817
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2363, "completion_tokens": 2211, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2211
- Total tokens: 2363

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
# Rate Limiting for Multi-Tenant APIs: Balancing Protection and Fairness Across Teams and Enterprises

Designing rate limiting for a multi-tenant API is fundamentally different from building a simple throttle for a single-user application. When your customers include both small teams with occasional bursts and enterprise customers running dozens of automated integrations, the wrong rate-limiting strategy can either cripple legitimate use or fail to protect shared infrastructure. This article walks through the architectural decisions that matter.

## 1. Authentication, Authorization, Quotas, and Rate Limits: Not the Same Thing

A common source of confusion is conflating these four layers. They operate at different points in the request lifecycle and serve distinct purposes.

**Authentication** answers “Who are you?” — it validates identity (e.g., API key, OAuth token). This happens first. Without it, no other checks occur.

**Authorization** answers “What are you allowed to do?” — it checks permissions (e.g., can this tenant read sensitive data?). This happens after authentication.

**Quotas** are about *capacity* — they define hard limits over a long time horizon, usually monthly or daily (e.g., 10,000 requests per month). Quotas are enforced at billing or resource allocation time. Exceeding a quota usually blocks the request permanently until the next cycle or an upgrade.

**Rate limits** are about *velocity* — they control *how fast* requests arrive (e.g., 100 requests per second). Rate limits are enforced per-second or per-minute. Exceeding a rate limit temporarily delays or rejects a request, but the counter resets after the window.

**Critical distinction:** Quotas protect your business model; rate limits protect your infrastructure. A tenant can stay within their monthly quota but still saturate your shared database with 10,000 requests in one second if rate limiting is absent.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window: Practical Trade-offs

Each algorithm has real-world implications for fairness, burst behavior, and implementation complexity.

**Fixed Window** splits time into discrete intervals (e.g., 1 minute). Counter resets at the start of each minute. *Problem:* A burst of requests at the end of minute 0 combined with another burst at the start of minute 1 can double the allowed traffic in a one-second span. This creates a “boundary problem” that punishes predictable traffic patterns.

**Sliding Window Log** tracks timestamps of recent requests within a rolling window (e.g., last 60 seconds). *Problem:* Requires O(n) storage per window and O(log n) to prune old entries. For enterprise tenants with tens of thousands of requests per second, this becomes expensive.

**Sliding Window Counter** is a practical hybrid. Divide the window into sub-intervals (e.g., 6 sub-windows of 10 seconds each for a 60-second window). The current rate is estimated as: `sum(weights of completed sub-windows) + (weight of current partial sub-window * elapsed fraction)`. This gives near-continuous smoothness with constant memory per tenant.

**Token Bucket** is the strongest choice for multi-tenant APIs. It allows bursts up to a configured capacity (bucket size), then refills at a steady rate. A team that normally sends 10 requests/second can burst to 100 requests if they’ve been idle for 10 seconds. An enterprise tenant can buy a larger bucket and refill rate. The bucket algorithm is simple to implement using a single value (tokens + last update timestamp). No per-request log.

**Recommendation:** Use token bucket as the primary algorithm. It handles bursts fairly and is constant-memory per tenant. If you need exact enforcement without burst smoothing, combine with a sliding window counter as a secondary check for premium tiers.

## 3. Avoid Punishing an Entire Tenant for One Noisy Integration

Enterprise tenants often have multiple teams or applications sharing a single API key. One rogue integration (e.g., a polling script with an infinite loop) can exhaust the tenant-wide rate limit, blocking all other integrations — including critical production services.

**Solution: Hierarchical rate limiting with per-key or per-integration buckets.**

Design your rate limit as a tree:

- **Root bucket:** Per-tenant global limit (e.g., 10,000 requests/minute).
- **Child buckets:** Per-API-key limit (e.g., 1,000 requests/minute per key), where each key represents a distinct integration.
- **Optionally, grandchild buckets:** Per-endpoint or per-IP limits for extremely noisy behavior.

When a request arrives:
1. Check the per-key bucket first. If it’s exhausted, reject with `429 Too Many Requests` — but only *that key* is blocked.
2. Decrement from the per-tenant bucket only if the per-key check passes.
3. If the per-tenant bucket is empty, block all keys — but this should be rare if per-key limits are set conservatively.

**Isolate noisy tenants further:** A tenant with 100 integrations should not degrade performance for a tenant with 3 integrations. Use separate request queues or throttling pools per tenant. If one tenant’s traffic causes resource contention, apply **concurrency limiting** (max simultaneous requests) in addition to rate limiting. This prevents a single slow endpoint from occupying all worker threads.

## 4. Headers and Error Messages That Build Trust

Clients need enough information to handle rate limits gracefully. Return these HTTP response headers:

- `X-RateLimit-Limit`: The maximum number of requests allowed in the current window (e.g., `100`).
- `X-RateLimit-Remaining`: How many requests remain in the current window (e.g., `42`).
- `X-RateLimit-Reset`: Unix timestamp when the window resets or when the bucket refills enough for a new request (e.g., `1735689600`).

For the `429 Too Many Requests` response, include a human-readable body:

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit for API key 'abc123'. This key is limited to 1,000 requests per minute. Retry after 45 seconds.",
  "retry_after_seconds": 45,
  "limit_scope": "api_key",
  "limit_tenant": "acme-corp"
}
```

**Why include `limit_scope`?** The client needs to know whether the block is at the key level or tenant level. If it’s per-key, they can switch to a different key. If it’s per-tenant, they need to reduce global traffic.

**Also include a `Retry-After` header** (HTTP standard, in seconds). Some client libraries respect this natively.

## 5. Observability: Are Limits Protecting Reliability Without Blocking Legitimate Use?

Without telemetry, you’re flying blind. Instrument every rate limit decision.

**Metrics to collect (per tenant, per key, per endpoint):**

- `rate_limit_requests_total`: Total requests attempted.
- `rate_limit_allowed_total`: Requests that passed.
- `rate_limit_denied_total`: Requests rejected, broken down by `reason` (per-key exceeded, per-tenant exceeded, concurrency exceeded).
- `rate_limit_bucket_usage`: Current fill level of the token bucket (as a ratio: 0.0–1.0). This tells you how close tenants are to being throttled.
- `rate_limit_latency_seconds`: Time spent in the rate limiter itself (should be < 1ms). Spikes indicate a bottleneck.

**Logs:** Log every denied request with tenant ID, API key ID, current bucket state, and the algorithm decision. Also log near-misses (when usage exceeds 80% of the limit). Near-miss logs help you identify patterns before they cause outages.

**Alerts:**

- **P0:** `rate_limit_denied_total` spikes > 5x baseline for any single tenant. This could indicate a misconfigured integration or a DDoS.
- **P1:** `rate_limit_latency` exceeds 10ms for the 99th percentile. The rate limiter becomes a bottleneck; consider moving from log-based to in-memory or distributed (e.g., Redis) for high-traffic tenants.
- **P2:** A tenant consistently uses > 90% of their limit for 10+ minutes. Proactive outreach to the customer can prevent accidental rate limiting during their normal peak.

**Correlation with reliability:** Track downstream error rates (e.g., database query latency, 5xx responses) against `rate_limit_denied_total`. If rejection rates are high but downstream errors remain low, you are over-limiting. If rejection rates are low but downstream errors are high, you are under-limiting.

## Recommended Baseline Design

For a multi-tenant API serving teams of 5 to enterprises with 200+ integrations:

1. **Algorithm:** Token bucket per API key (bucket size = 2x normal burst, refill rate = per-key limit / 60 per second). Global per-tenant token bucket with bucket size = 1.5x the aggregate of all keys, refill rate = sum of all key refill rates.

2. **Hierarchy:** Three-level tree: Tenant → API Key → Endpoint. Only the Tenant and Key levels actively enforce limits. The endpoint level is optional for observability.

3. **Storage:** In-memory for single-instance APIs; for distributed systems, use a shared cache with TTL-based keys and atomic decrement operations. Avoid storing full request logs.

4. **Headers:** Always return `X-RateLimit-Limit`, `Remaining`, `Reset`. On 429, return `Retry-After` and a JSON body with `limit_scope` and `retry_after_seconds`.

5. **Observability:** Track `rate_limit_allowed`, `denied`, `bucket_usage` as Prometheus-style counters and gauges per tenant and per key. Alert on denial spikes above 3x baseline or downstream error correlation.

6. **Initial defaults:** Small teams: 100 req/min per key, 500 req/min per tenant. Enterprise: 1,000 req/min per key, 10,000 req/min per tenant. Adjust based on historical traffic analysis.

Rate limiting is not a “set and forget” component. It requires continual tuning based on traffic patterns, customer feedback, and infrastructure scaling. Start simple with token buckets and hierarchical keys; iterate based on real-world behavior. Your API will thank you.
````
