# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
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
- Elapsed seconds: 11.538646
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2642, "completion_tokens": 2490, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2490
- Total tokens: 2642

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
# Designing Rate Limiting for a Multi-Tenant API: Balancing Protection with Flexibility

Rate limiting is one of those infrastructure decisions that seems simple at first but quickly unravels into a tangle of trade-offs when you support both a 5-person startup and a Fortune 500 enterprise on the same API. Getting it wrong means either frustrating your most valuable customers or letting a noisy neighbor degrade reliability for everyone. This article walks through the engineering decisions behind a rate-limiting system that serves both small teams and enterprise tenants fairly.

## 1. Foundational Distinctions: Auth, Authorization, Quotas, and Rate Limits

Before designing, we need clarity on four concepts that engineers often conflate.

**Authentication** answers “Who are you?” It validates credentials (API keys, OAuth tokens, JWT) and establishes identity. It does not control usage.

**Authorization** answers “What are you allowed to do?” It checks permissions—can this tenant call the `POST /admin/billing` endpoint? It is about access rights, not request frequency.

**Quotas** answer “How much total usage are you entitled to over a billing period?” A quota might say 1,000,000 requests per month. Quotas are enforced at the end of a period (or proactively with soft limits), typically for billing and planning.

**Rate limits** answer “How fast can you send requests right now?” They protect system stability by preventing short-term bursts from overwhelming resources. Rate limits operate on sub-second to minute windows. They are the first line of defense, whereas quotas are the accounting layer.

In a multi-tenant system, you must apply these independently. A tenant might have a high quota (enterprise contract) but still need per-second rate limits to prevent a misbehaving integration from starving other tenants.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window: Practical Trade-offs

Three common algorithms exist, and each has operational implications for multi-tenant fairness.

**Fixed Window** increments a counter per time window (e.g., 100 requests per minute, resetting at :00). It is simple to implement in Redis with `INCR` and `EXPIRE`. The critical flaw: traffic spikes at the boundary. If a tenant sends 100 requests at :59 and 100 more at :01, they effectively achieve 200 requests in two seconds. This violates the “rate” guarantee and punishes other tenants competing for the same resources.

**Sliding Window Log** tracks timestamps of each request and counts those within the window. It is accurate but memory-intensive for high-throughput tenants (requires storing potentially thousands of timestamps). For enterprise tenants with millions of requests, this becomes expensive.

**Sliding Window Counter** (e.g., using Redis sorted sets or rolling counters) keeps a few sub-windows (e.g., 6 buckets per minute) and estimates the count. It achieves near-fixed-window simplicity with much better boundary behavior. Most practical implementations use this: store two buckets (current and previous) and interpolate. The trade-off is slight approximation error (1–2%), which is acceptable for rate limiting but not for billing.

**Token Bucket** allows bursts up to a configured capacity (bucket size) while limiting the sustained rate (refill rate). A tenant with a 1,000 requests/second token bucket and a bucket size of 2,000 can burst 2,000 requests if idle, then settle to 1,000/s. This is ideal for enterprise customers with legitimate batch operations (e.g., syncing large datasets at midnight). The downside: it requires tracking token state per tenant (e.g., last refill timestamp), which adds storage cost but avoids the clock-alignment issues of window algorithms.

For a multi-tenant system, I recommend **token bucket per tenant** for the core limit, combined with a **sliding window counter** for hard global limits. Token bucket gives tenants predictable burst behavior. The sliding window counter acts as a safety net for the entire infrastructure.

## 3. Protecting Other Tenants from a Noisy Integration

The hardest problem in multi-tenant rate limiting: one enterprise tenant’s misconfigured integration (e.g., a retry loop gone wild) should not degrade another tenant’s latency or error rate. Three techniques work together.

**Isolation by enforcement point.** Rate-limit decisions must be made per tenant, not globally. Use the tenant ID (extracted from the API key or JWT claim) as the key for your token bucket. Never apply a single global rate limit that all tenants share—that protects your infrastructure but punishes quiet tenants.

**Hierarchical rate limits.** Implement tiers: a per-endpoint rate limit, a per-tenant rate limit, and a global cluster-level limit. For example, the per-tenant token bucket allows 500 req/s. A separate global sliding window of 5,000 req/s across all tenants protects the database. If one tenant sends 3,000 req/s, the per-tenant bucket rejects the excess, but the global limit ensures the remaining two-thirds of capacity stays available for others.

**Concurrency-based backpressure.** Rate limits based on request rate alone miss the problem of long-running requests. A tenant might send 10 requests, each taking 30 seconds, consuming all database connection pool slots. Add a separate “concurrent requests” limiter (a semaphore per tenant) that caps parallel in-flight requests. This prevents one tenant from occupying all worker threads.

**Delayed rejection for enterprise customers.** For small teams, dropping excess requests with `429 Too Many Requests` is fine. For enterprise customers, consider an optional “slow queue” that delays requests beyond the limit instead of dropping them, with a small buffer. This avoids catastrophic retry storms. The queue must have bounded depth and a TTL—never unbounded.

## 4. Headers and Error Messages Clients Need

Clients cannot react to rate limits without clear feedback. The API must return these headers on every response (not just on 429):

- `X-RateLimit-Limit`: The maximum rate allowed for this tenant (e.g., “500” for requests/second)
- `X-RateLimit-Remaining`: How many requests remain in the current window/bucket before hitting the limit (e.g., “423”)
- `X-RateLimit-Reset`: Unix timestamp when the limit resets (or when the token bucket will refill to at least one request). This lets clients compute backoff.

On 429 responses, additionally return:

- `Retry-After`: Seconds the client should wait before retrying (integer). This is the most actionable header for simple retry logic.
- A JSON body:

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded your API rate limit. Retry after 12 seconds.",
  "retry_after_seconds": 12,
  "limit": 500,
  "remaining": 0,
  "reset_at": 1712345678
}
```

The error code (`rate_limit_exceeded`) must be distinct from `quota_exceeded` (billing limit) and `insufficient_permissions` (authorization). Clients must never confuse these.

For multi-tenant notability: log the tenant ID and the violating integration’s IP or API key identifier in the error response (but never expose other tenants’ info). This helps clients debug and helps you identify noisy integrations in support tickets.

## 5. Observability: Are Limits Protecting Without Blocking?

Rate limiting can become a silent villain—blocking legitimate use while letting abuse through. Observability must answer both directions.

**Metrics to collect** (per tenant tag, per endpoint tag, per status code tag):

- `rate_limit.throttled_requests_total`: Count of requests that received 429. Split by tenant and endpoint.
- `rate_limit.requests_before_throttle`: Distribution (histogram) of how many requests tenants made before hitting the limit in a window. Spikes here indicate limits are too tight or tenants are misconfiguring.
- `rate_limit.token_bucket.remaining`: Track the current bucket level per tenant. If it stays near zero for long periods, the limit is too low. If it never drops below 90%, the limit is too generous.
- `api.latency_p99`: Grouped by tenant. If throttling prevents overload, latency should remain stable even as total request volume increases. If latency climbs despite low throttle counts, the limit is not protecting the bottleneck.
- `api.error_rate` (non-429): If error rates (5xx) drop after introducing rate limits, the system is working. If they rise, something is wrong (e.g., rate limiting causing thundering herd elsewhere).

**Logs**: Log every 429 with tenant ID, endpoint, HTTP method, and the client’s user-agent or integration identifier. Also log when a tenant crosses 80% of their limit (warning) and 100% (critical). This creates a trail for post-mortems when a customer complains about their requests being dropped.

**Alerts**: The most critical alert is not “high throttle rate” but **“throttle rate increasing while error rate (5xx) remains flat”** —that indicates limits are protecting resources. Conversely, **“throttle rate increasing AND error rate increasing”** means the limits are too late or too permissive. Additionally, alert on **“no throttling for any tenant for >24 hours”** —this likely means limits are set too high to ever trigger, providing no protection.

Set a P1 alert if global infrastructure metrics (CPU, connection pool utilization, DB query latency) exceed thresholds, even if throttle rates are low. That indicates you’ve misconfigured the limits to not activate early enough.

## 6. Recommended Baseline Design

For a team building a new multi-tenant API, start with this minimal but sound design:

- **Algorithm**: Token bucket per tenant (one bucket per tenant plus one per endpoint if needed). Store `last_refill_timestamp` and `tokens` in Redis with a TTL equal to the refill period (so idle tenants don’t waste memory).
- **Tiers**: Per-tenant limit (e.g., 200 req/s), per-tenant burst limit (e.g., 400), global sliding window counter (e.g., 5,000 req/s across all tenants). Apply the global limit after the per-tenant limit to catch aggregate abuse.
- **Concurrency**: Add a per-tenant semaphore with max_in_flight = 10. Implement in middleware, not in application code.
- **Headers**: Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After` (on 429).
- **Error responses**: Use a consistent JSON schema with `error`, `message`, `retry_after_seconds`, `limit`, `remaining`, `reset_at`.
- **Observability**: Export the four metrics listed above (throttled requests, requests before throttle, bucket remaining, latency P99) with tenant and endpoint dimensions. Log every 429 and warning-level near-limit events.
- **Configuration**: Store rate limits in a dynamic config store (not hardcoded). Let enterprise support adjust per-tenant limits without a deploy.

Expand from this baseline: add per-endpoint limits for expensive endpoints (e.g., `/reports/generate`), add cost-weighted limits where one request may weigh more than one (e.g., 1 point for GET, 5 points for POST with large payload), and consider a “retry budget” for paying customers to auto-escalate limits during high-priority integrations.

Rate limiting done right feels invisible. Users should never think about it—but when a misconfiguration happens, your system should survive unscathed, and your logs should tell the story of exactly which tenant caused the pressure and how the limits held the line.
````
