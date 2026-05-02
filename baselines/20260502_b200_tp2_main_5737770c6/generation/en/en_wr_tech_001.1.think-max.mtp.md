# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.032518
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 1954, "completion_tokens": 1802, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 1802
- Total tokens: 1954

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
# Designing Rate Limiting for Multi-Tenant APIs: Balancing Small Teams and Enterprise Customers

**By: [Your Name]**

## 1. Foundational Concepts: Authentication, Authorization, Quotas, and Rate Limits

Before designing a rate-limiting system, it’s critical to distinguish four related but distinct concepts:

- **Authentication** verifies *who* you are (e.g., API key, OAuth token).
- **Authorization** determines *what* you’re allowed to do (e.g., read-only vs. admin).
- **Quotas** define a *hard ceiling* on total usage over a long period (e.g., 1 million requests per month). Quotas are enforced *after* the fact or at the point of consumption.
- **Rate limits** control the *instantaneous* rate of requests (e.g., 100 requests per second) to protect infrastructure from bursts and abuse. Rate limits are enforced *in real time*.

A common pitfall is conflating quotas with rate limits. Quotas protect your business model; rate limits protect your system’s stability. Both are needed, but they serve different purposes and require separate enforcement mechanisms.

## 2. Algorithm Comparison: Token Bucket, Fixed Window, Sliding Window

### Fixed Window
Divide time into discrete windows (e.g., 1-second intervals). Count requests per window. If the count exceeds the limit, reject until the next window.

**Pros:** Simple to implement, low memory overhead.
**Cons:** Bursts at window boundaries can double throughput. A client sending 100 requests at the last millisecond of window N and 100 at the first millisecond of window N+1 effectively achieves 200 requests in 2 milliseconds.

### Sliding Window Log
Maintain a sorted list of timestamps for each request. At each new request, remove timestamps older than the window duration. If the remaining count exceeds the limit, reject.

**Pros:** Smooth rate enforcement, no boundary spikes.
**Cons:** High memory per tenant (storing all timestamps) and O(n) cleanup per request.

### Token Bucket
A bucket holds a fixed number of tokens. Tokens are added at a constant rate (e.g., 10 tokens per second). Each request consumes one token. If the bucket is empty, the request is rejected.

**Pros:** Allows short bursts up to bucket capacity; smooth long-term rate. Stateless implementation is possible using atomic counters.
**Cons:** Slightly more complex; requires tuning bucket size vs. refill rate.

**Practical recommendation:** Token bucket is generally the best fit for multi-tenant APIs. It naturally handles bursts (important for small teams testing under load) while enforcing a sustainable long-term rate. Fixed window should be avoided for production unless you accept boundary spikes. Sliding window log is acceptable for low-volume tenants but becomes expensive at scale.

## 3. Protecting Tenants from Internal Noise

A common failure pattern: one integration (e.g., a misconfigured webhook or a polling script) within a tenant exhausts the tenant’s global rate limit, blocking all other legitimate integrations and users for that tenant.

**Solution: Multi-tier rate limiting with per-key and per-tenant buckets.**

- **Per-API-key bucket:** Each API key (or integration) gets its own token bucket. If one key goes rogue, it exhausts only its own bucket, not the tenant’s global limit.
- **Per-tenant bucket:** A separate, larger bucket limits the total traffic across all keys for the tenant. This ensures no key can monopolize the tenant’s total allowance.
- **Hierarchical enforcement:** On each request, check the per-key bucket first. If it’s okay, then check the per-tenant bucket. A request passes only if both buckets have tokens.

This protects the tenant from a single noisy integration while still allowing the tenant to have a maximum aggregate rate. Enterprise customers with many integrations benefit from this granularity.

## 4. API Client Feedback: Headers and Error Messages

Clients must receive unambiguous feedback to adjust behavior programmatically.

### Response Headers (standardized per RFC 6585)
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 234
X-RateLimit-Reset: 1685559600
```
- `X-RateLimit-Limit`: Maximum requests allowed per window.
- `X-RateLimit-Remaining`: Remaining requests in current window.
- `X-RateLimit-Reset`: Unix timestamp when the limit resets.

For multi-key tenants, include both key-level and tenant-level headers:
```
X-RateLimit-Key-Limit: 100
X-RateLimit-Key-Remaining: 17
X-RateLimit-Tenant-Limit: 5000
X-RateLimit-Tenant-Remaining: 1024
```

### Error Response (429 Too Many Requests)
Return a JSON body with retry semantics:
```json
{
  "error": "rate_limit_exceeded",
  "message": "API key rate limit exceeded. Retry after 12 seconds.",
  "retry_after_seconds": 12,
  "scope": "api_key"
}
```
The `scope` field clarifies whether the limit was hit at the key or tenant level. Enterprise teams can then adjust the offending integration without panicking about tenant-wide blocking.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting must be transparent to your operations team. Without observability, you cannot distinguish between “limits protecting the system” and “limits blocking legitimate customers.”

### Metrics (counters and histograms)
- **requests_total** by tenant, key, and status (allowed / rate_limited).
- **rate_limit_exhausted_total** by scope (key vs. tenant) and by tenant tier (small team vs. enterprise).
- **request_bucket_capacity_remaining** (gauge) for each tenant bucket—useful for detecting tenants approaching limits.
- **rate_limit_decision_latency_seconds** (histogram)—enforcements must be fast (< 1ms). High latency here indicates a scaling issue.

### Logs
- Log every rate-limited request with tenant ID, key ID, request path, and which bucket triggered the denial.
- Log when a tenant’s bucket refills (or reaches certain thresholds) to correlate with traffic patterns.
- **Avoid** logging every allowed request; that will drown your log system.

### Alerts
- **High rate limit hit rate per tenant:** If a single tenant is hitting limits > 10% of its total requests, investigate (may be a misconfigured integration).
- **Global rate limit exhaustion:** Rare, but if your internal infrastructure limits are being hit, it signals capacity planning failure.
- **Latency spike in rate limit decision:** Distributed rate limiter coordination (e.g., Redis read) can become a bottleneck. Alert if p99 latency exceeds 5ms.
- **Anomalous drop in allowed requests for an enterprise tenant:** Could indicate a bug in your rate limiting logic, not actual throttling.

## 6. Recommended Baseline Design

For a practical, scalable, multi-tenant API serving both small teams and enterprise customers, use the following:

- **Algorithm:** Token bucket with per-key and per-tenant buckets. Bucket size = 2× the refill rate per minute to allow short bursts.
- **Storage:** In-memory with a distributed cache (e.g., Redis) shared across API servers. Use atomic `INCR` with expiry for per-key counters, and `INCR` with a TTL-based window for tenant-level aggregates (simulates token bucket via sliding window counters).
- **Tiering:** Offer three tiers—Small Team (100 req/min per key, 500 req/min tenant total), Growth (500 req/min per key, 5000 req/min tenant total), Enterprise (custom).
- **Headers:** Always return key and tenant level headers and a clear `retry_after_seconds` in 429 responses.
- **Observability:** Expose Prometheus metrics from the rate limiter middleware. Set alerts for >1% rate-limited requests per tier and latency >5ms.

**Avoid** global rate limits that affect all tenants equally; multi-tenancy demands isolated limits. **Never** silently drop requests—always respond with 429 and actionable feedback.

Rate limiting, when designed with these principles, protects your infrastructure without punishing legitimate usage—whether from a startup’s weekend hackathon project or a Fortune 500’s production billing pipeline.
````
