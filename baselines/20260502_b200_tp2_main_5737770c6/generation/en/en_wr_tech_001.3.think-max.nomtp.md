# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
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
- Elapsed seconds: 19.119207
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2473, "completion_tokens": 2321, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2321
- Total tokens: 2473

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
# Granular Guardrails: Designing Rate Limits for Multi-Tenant APIs Serving Teams and Enterprises

## 1. Clarifying the Four Pillars

Before designing a rate limiter, we must distinguish four concepts that engineers often conflate:

- **Authentication** proves *who* the caller is (e.g., API key, OAuth token). It answers: “Are you a known client?”
- **Authorization** determines *what* the caller may do (e.g., read vs. write, access to specific resources). It answers: “Are you allowed to perform this action?”
- **Quotas** enforce *aggregate usage over a long period* (e.g., 10,000 requests per month, 1 TB of data transfer per billing cycle). Quotas are typically reset on a calendar month or subscription tier and are primarily a business concern.
- **Rate limits** enforce *traffic velocity over a short window* (e.g., 100 requests per second). They protect system stability by preventing any single source from overwhelming shared infrastructure.

A common anti-pattern is using rate limits to enforce quotas. If a team exhausts its daily quota at noon, they should get a 403 (Forbidden, not 429). Rate limits should tell clients *how fast* they can go, not *how much* they can use.

## 2. Algorithm Trade-offs at a Practical Level

Three algorithms dominate real-world implementations. Each has a distinct cost-benefit profile for a multi-tenant workload.

### Token Bucket
- **How it works**: A bucket holds up to N tokens. Each request consumes one token. Tokens refill at a steady rate (e.g., 10 tokens per second). If the bucket is empty, the request is rejected.
- **Strengths**: Smooths bursty traffic perfectly. A small team that pauses for 10 minutes can burst at full speed for several seconds immediately after, which feels natural.
- **Weakness**: Complexity is moderate. Requires a timer-based refill loop or a lazily evaluated algorithm. Must store the current token count per tenant, plus last refill timestamp, in a fast store (e.g., Redis).
- **Best for**: Enterprise tenants that need to absorb occasional spikes without being penalized by a rigid window boundary.

### Fixed Window
- **How it works**: A counter per tenant resets at the start of each fixed duration (e.g., 100 requests per second, resetting at :00 of each second).
- **Strength**: Extremely simple to implement and reason about. Minimal storage per tenant.
- **Weakness**: Prone to “thundering herd” at window boundaries. If ten tenants all become idle at the end of a second, they all get a fresh 100 tokens at :00 and can cause a coordinated spike. Also, a tenant doing 99 requests at :59.999 and 99 more at :00.001 effectively gets a burst of 198, which defeats the purpose of rate limiting.
- **Best for**: Internal tooling with low traffic variance, or as a first iteration before migrating to a smoother algorithm.

### Sliding Window Log
- **How it works**: Each request timestamp is logged. The rate is computed by counting timestamps within the last N seconds. If the count exceeds the limit, the request is rejected.
- **Strength**: No window-boundary effects. Accurate to the microsecond.
- **Weakness**: Storage grows with request volume. A tenant doing 10,000 req/s requires storing 10,000 timestamps per second. Memory management becomes non-trivial. Can be approximated with a sorted set or exponential time decay, but complexity rises.
- **Practical compromise**: The **sliding window counter** (a hybrid) stores two counters: the current fixed window counter and the previous window’s counter. The rate is `(previous_window_count * overlap_ratio) + current_window_count`. This gives near-exact sliding behavior with O(1) storage per tenant.

**Recommendation**: Use token bucket as the default. For tenants with extremely high traffic, fall back to sliding window counter to avoid token-bucket memory churn. Avoid fixed window entirely in production unless you explicitly intend to allow the boundary burst.

## 3. Avoiding Tenant-Wide Punishment for a Single Noisy Integration

A single misconfigured cron job or a buggy webhook integration in one sub-team should not degrade service for the rest of the tenant. There are three isolation strategies:

### Per-Integration (or Per-API-Key) Limits
Assign a rate limit to each API key, not just to the tenant. A tenant with 50 developers gets 50 separate rate-limit buckets. A noisy key that exceeds its limit receives a 429, but all other keys under the same tenant continue unimpeded.

### Shared Bucket with Fair Queuing
If you must enforce a tenant-wide cap (e.g., a “total enterprise” limit), use a hierarchical token bucket: a parent bucket per tenant (e.g., 5000 req/s) and a child bucket per integration key (e.g., 200 req/s). A request draws tokens from its child bucket first. If the child is empty, it can draw from the parent—but only if the child is not already over its limit. This ensures that no single key can starve the parent.

### Delayed Throttling for Outlier Sources
When a single integration starts consuming an outsized portion of the tenant’s budget, do not immediately 429. Instead, insert an artificial delay (e.g., 200 ms) for requests from that specific key. If the behavior continues beyond a grace period (e.g., 10 seconds), then reject. This keeps the integration alive (preventing cascading failures from retry storms) while protecting latency for well-behaved keys.

## 4. Headers and Error Messages

Returning descriptive headers is a form of “politeness” that greatly improves the developer experience. Every rate-limited response should include:

- **`X-RateLimit-Limit`**: The maximum requests per window (e.g., `100`).
- **`X-RateLimit-Remaining`**: The number of requests left in the current window (e.g., `42`).
- **`X-RateLimit-Reset`**: A Unix timestamp (seconds since epoch) indicating when the rate limit resets. This lets clients schedule their next poll precisely.

For **failed** requests (HTTP 429), add a `Retry-After` header in seconds. For example: `Retry-After: 3`. The body should be JSON with:

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit of 100 requests per second for this API key. Please retry after 3 seconds.",
  "reset_at": 1712345678
}
```

Crucially, differentiate between **tenant-level** and **key-level** limits in the headers. When the tenant-level limit is hit (a rare emergency), use a different error code like 429 with `error: "tenant_rate_limit_exceeded"`. If you merge both into a single 429, clients cannot distinguish between a self-inflicted limit and a neighbor’s noise.

## 5. Observability: Protecting Reliability Without Blocking Legitimate Use

Rate limiting is a blunt instrument. You need telemetry to verify it is not too aggressive (blocking legitimate spikes) or too permissive (failing to protect downstream services).

### Metrics (Prometheus-style)
- **`rate_limit_requests_total{key_id, tenant, action, status}`**: Count all requests broken down by whether they were accepted or rejected. Track the ratio of rejected to accepted per tenant. If a tenant has a 0.01% rejection rate for 24 hours, it is likely accidental (window boundary effects). If a tenant has 5% rejection on a key, that key is misconfigured.
- **`rate_limit_current_bucket_level{key_id}`**: Gauge showing the current token count per bucket. Sudden drops to zero indicate a request burst that may need investigation.
- **`p99_request_latency_seconds{tenant}`**: Rate limiting should not increase latency for legitimate requests. If p99 rises above a threshold (e.g., from 50 ms to 200 ms) during a spike, your rate limiter may be rejecting requests that get retried at a bad moment, causing a queue buildup.

### Logs
- Log **every rejection** at WARN level with `key_id`, `tenant`, `request_path`, `remaining`, and `reset_at`. Do not rate-limit the rate-limiting logs; you need the full picture during an outage.
- Log **tenant-level throttling events** (e.g., when a parent bucket is drained by a noisy child) at ERROR level and include the violating `key_id`. This triggers an alert.

### Alerts
- **Tenant-level rejection rate > 1%** for more than 5 minutes: Likely your rate-limit thresholds are too low, or a DDoS-like pattern (e.g., a bug in the tenant’s client). Investigate.
- **Single key rejection rate > 20%**: That key is clearly broken. Alert the tenant contact.
- **Any key hitting tenant-level limit**: This is an emergency—one misbehaving key is starving the entire tenant. Immediate intervention required.
- **`rate_limit_current_bucket_level` drops below 10% for > 10 seconds** for multiple keys simultaneously: The system may be near its total capacity, not just per-tenant limits. Investigate scaling upstream dependencies.

## Recommended Baseline Design

For a multi-tenant API that serves both small teams (50 req/s per key) and enterprise customers (500 req/s per key, 10 keys per tenant), implement a two-level hierarchical token bucket:

1. **Per-API-key child bucket**: refill rate = 50 req/s, burst size = 100.
2. **Per-tenant parent bucket**: refill rate = 500 req/s (configurable per plan), burst size = 1000.
3. A request draws from the child bucket first. If the child is empty, it may draw from the parent only if the child’s current consumption rate (rolling average over 5 seconds) is below 80% of its limit. This punishes only the noisy key, not the tenant.

Store bucket state in a fast key-value store with TTL-based eviction (hourly). Use sliding window counters rather than pure token bucket for parent buckets (to avoid storing 1000 tokens per tenant). Return `X-RateLimit-Limit`, `Remaining`, and `Reset` headers for both the key-level and tenant-level limits.

Monitor the rejection rate at both levels. If tenant-level rejection exceeds 0.1%, scale the parent bucket (or contact the customer). If key-level rejection exceeds 5%, that integration is misconfigured—block it early rather than letting it cascade.

This design gives small teams freedom to burst, protects enterprises from their own mistakes, and ensures the API remains reliable for everyone.
````
