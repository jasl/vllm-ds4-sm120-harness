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
- Elapsed seconds: 14.960016
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 1944, "completion_tokens": 1792, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 1792
- Total tokens: 1944

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
# Designing Rate Limits That Don't Fail Your Customers

Backend engineers often conflate four distinct concepts: authentication, authorization, quotas, and rate limits. Understanding their differences is the foundation for any multi-tenant rate-limiting design.

## The Four Pillars of Access Control

**Authentication** answers "who are you?" – it's the API key, OAuth token, or mTLS certificate that identifies the caller. **Authorization** answers "what can you do?" – it's the permission model that says a free-tier user cannot call admin endpoints. **Quotas** answer "how much can you use over time?" – they are cumulative limits measured daily or monthly (e.g., 10,000 requests per month). **Rate limits** answer "how fast can you send requests?" – they protect infrastructure from sudden spikes, not total usage.

The critical insight: quotas are billing mechanisms, rate limits are reliability mechanisms. Mixing them leads to angry customers who hit a rate limit for making legitimate bursty traffic within their quota.

## Choosing Your Algorithm: Practical Trade-offs

### Token Bucket
Imagine a bucket that fills with tokens at a steady rate (e.g., 100 tokens per second) up to a maximum capacity (e.g., 200 tokens burst). Each request consumes one token. If the bucket is empty, the request is rejected.

This model handles bursty traffic naturally: a client can send 200 requests immediately, then must wait for tokens to replenish. It's the most forgiving for well-behaved clients and the least forgiving for misconfigured retry loops that drain the bucket. Implementation overhead is moderate – you need a distributed counter per tenant with per-second precision.

### Fixed Window
Divide time into discrete windows (e.g., 100 requests per 60 seconds). Reset the counter at the start of each window. Simple to implement and reason about, but suffers from the "thundering herd" problem at window boundaries: clients may queue requests right at the second 59 mark, causing a burst when the window resets. This can double the effective load.

### Sliding Window
A hybrid: maintain a counter for the current minute window plus the previous minute's counter with weighted decay. For example, a 100-req/min limit checks: `current_window_count + (previous_window_weighted_at_second_mark) < 100`. This smooths the boundary effect and prevents double-bursts. Implementation is roughly 20% more complex than fixed window but far more predictable.

### Recommendation
For multi-tenant APIs, token bucket is the pragmatic choice. It aligns with human intuition ("I sent too fast") and pairs naturally with burst control. Use sliding window only if you need strict per-second evenness and cannot tolerate any burstiness.

## Protecting Tenants from Their Own Noisy Integrations

The cardinal sin of multi-tenant rate limiting is a single "noisy" integration (a buggy webhook, an aggressive scraper, a misconfigured retry loop) degrading performance for the entire tenant. Three strategies prevent this:

**Per-API-key limits within a tenant.** Each integration (webhook callback, partner integration, mobile app) gets its own API key. Apply rate limits at the key level, then a separate, higher limit at the tenant level. This way, one misbehaving webhook can exhaust its own key limit but cannot consume the tenant's entire budget. The tenant's other integrations remain unscathed.

**Queue-based admission with priority.** Instead of rejecting requests, assign them to tenant-specific queues with configurable concurrency limits. High-priority queues (e.g., interactive user requests) bypass rate limits for bounded bursts, while low-priority queues (bulk data syncs) are strictly throttled. This adds complexity but prevents a batch job from starving real-time traffic.

**Distinct limit tiers for synchronous vs. asynchronous endpoints.** Write endpoints should have lower rate limits than read endpoints. A user-facing create-order endpoint might allow 10 req/s, while a bulk export endpoint might allow 1 req/s. This directly protects tenants from their own background jobs consuming all capacity.

## Headers and Error Messages: Engineering for Debugging

Your rate-limit response headers should answer three client questions: what's my limit, how much have I used, and when can I retry?

Required headers:
- `X-RateLimit-Limit`: The maximum requests per window (e.g., 100)
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when the window resets

For token bucket, add `X-RateLimit-Burst-Capacity`: The burst size (e.g., 200), because clients need to know the bucket depth to tune their retry intervals.

Error response body (HTTP 429 Too Many Requests):
```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit of 100 requests per second for tenant abc-123. Retry after 15 seconds.",
  "retry_after_seconds": 15,
  "limit_key": "tenant:abc-123:read-requests"
}
```

Never return "your API key is blocked" or "your account is suspended" for rate limits – that confuses clients and creates unnecessary support tickets. Use a distinct error code (429) and a clear message that differentiates rate limiting from authentication failures (401) or quota exhaustion (403).

## Observability: Knowing When Limits Work

Most teams implement rate limits and never check whether they're actually protecting reliability. You need three observability layers:

### Metrics (Prometheus/Grafana or equivalent)
- `rate_limit_decisions_total` with labels: `tenant_id`, `api_key_id`, `decision` (allow/deny), `endpoint_group` – this is your primary signal. Track deny rate per tenant: a tenant with >5% deny rate indicates either a misconfigured client or a limit that's too tight.
- `rate_limit_queue_depth` if using queue-based admission: sudden growth in a tenant's queue suggests a client ramping up unexpectedly.
- `request_latency_p99 per tenant`: if latency increases alongside deny rate, the limits are working (they're preventing overload). If latency increases but deny rate is zero, your limits are too permissive.

### Logs
Log every deny decision with the context needed for debugging: `tenant_id`, `api_key_id`, `request_path`, `current_count`, `limit_value`, `decision_reason`. Do NOT log every allow – the volume is too high. Sample 1% of allow decisions for auditing.

### Alerts
- **P0 (immediate response)**: Any tenant's error rate (server-side 5xx) increases >50% of baseline. This may mean rate limits are failing to protect the service.
- **P1 (same day)**: Any tenant's deny rate exceeds 20% for 5 minutes. This signals a noisy integration or a limit that's too low.
- **P2 (weekly review)**: A group of tenants collectively shows >10% deny rate. This often means a pricing tier's default limit is insufficient for typical usage patterns.

## Recommended Baseline Design

For a multi-tenant API serving small teams and enterprises:

1. **Algorithm**: Per-tenant token bucket with separate burst and sustained rates. Default: 50 req/s sustained, 100 req burst for small teams; 200 req/s sustained, 500 req burst for enterprises. Adjust based on tenant usage patterns.

2. **Scoping**: Rate limit at tenant level (not per API key) for simplicity, but warn noisy tenants via a secondary per-key limit that logs rather than denies. This gives you observability without breaking production traffic.

3. **Headers**: Return the three standard headers plus `Retry-After` (in seconds) for `429` responses. Never return quota usage in rate-limit headers – clients confuse them.

4. **Backpressure**: If a tenant exceeds 50% of their limit consistently for 30 seconds, apply exponential backoff to their token refill rate rather than rejecting requests. This degrades gracefully instead of cutting traffic abruptly.

5. **Observability**: Track deny rate per tenant. Alert if any enterprise tenant has >5% deny rate or any small team has >15% deny rate. Review limits quarterly against actual traffic patterns.

The goal of rate limiting is not to punish customers for using your API – it's to ensure that one customer's burst doesn't become everyone's outage. Design for forgiveness, measure for impact, and adjust limits based on real-world usage, not theoretical models.
````
