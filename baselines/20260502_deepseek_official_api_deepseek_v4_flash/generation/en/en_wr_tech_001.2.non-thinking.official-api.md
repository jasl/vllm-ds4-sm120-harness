# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-v4-flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 27.083167
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "completion_tokens": 2103, "total_tokens": 2255, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 24}`
- Prompt tokens: 152
- Completion tokens: 2103
- Total tokens: 2255

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
# Rate Limiting for Multi-Tenant APIs: Balancing Fairness and Reliability

Backend engineers who design APIs for a mix of small teams and enterprise customers quickly discover that rate limiting is not a one-size-fits-all problem. A startup with three developers and a Fortune 500 with a thousand integrations both expect the API to be responsive, but their usage patterns differ dramatically. This article walks through the key design decisions for a rate limiting system that distinguishes between auth concepts, selects the right algorithm, isolates noisy tenants, communicates clearly with clients, and surfaces meaningful observability.

## 1. Authentication, Authorization, Quotas, and Rate Limits – What’s the Difference?

These four terms are often conflated but serve distinct purposes:

- **Authentication** verifies *who* you are (e.g., API key validation, OAuth token). It answers: “Is this request from a recognized client?”
- **Authorization** determines *what* you are allowed to do (e.g., read vs. write, specific endpoints). It answers: “Does this client have permission for this action?”
- **Quotas** define a *hard cap* on usage over a long period (e.g., 10,000 requests per month). Quotas are about total consumption and often trigger billing or account upgrades.
- **Rate limits** control the *rate* of requests over a short window (e.g., 100 requests per minute). They protect system stability by preventing bursts from overwhelming infrastructure.

In multi-tenant systems, rate limits operate per-tenant (not per-user) by default, but can be layered: a global per-API-key limit, a per-endpoint limit for heavily used resources, and a per-IP limit as a last resort.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window – Practical Tradeoffs

You cannot design a rate limiter without understanding the three dominant algorithms at the implementation level.

### Fixed Window
Simplest to implement: reset a counter every N seconds. However, it suffers from the *burst-at-boundary* problem. If you allow 100 requests per minute, a client can send 99 requests at 11:59:59 and another 100 at 12:00:00—a burst of 199 requests in two seconds. This defeats the purpose of smoothing traffic.

### Sliding Window (Log or Counter)
A sliding window log stores timestamps of each request and removes those older than the window. Accurate but memory-intensive for high-throughput tenants. A sliding window counter (e.g., based on Redis sorted sets or approximations) splits the window into sub-windows and interpolates the count. It solves the boundary problem and is memory-efficient, but adds complexity.

### Token Bucket
The most practical algorithm for multi-tenant APIs. A token bucket holds a configurable number of tokens (burst capacity) and refills at a steady rate (sustained rate). A request consumes one token; if the bucket is empty, the request is denied. This naturally handles bursts up to the bucket size while enforcing a long-term average rate.

**Why it wins for mixed workloads**: Small teams may send 10 requests per minute but need a burst of 50 when deploying a script. Enterprise customers might average 500 requests per minute with occasional spikes. Token buckets allow architects to configure `burst` and `refill rate` per tenant tier, giving each predictable behavior without the fixed-window boundary problem. Sliding window counters are a close second but are harder to implement without a distributed store like Redis.

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

One of the most common failure modes in multi-tenant rate limiting is a “global tenant limit” that, when exhausted by one aggressive integration, blocks all other integrations for that tenant. If an enterprise customer has 50 separate API keys (one per internal service), a misbehaving cron job should not throttle their CRM sync.

**Solution: Per-key limits within a tenant bucket.** Each API key (or integration identifier) gets its own token bucket, and the tenant also has a *shared pool*. Requests first check the per-key bucket; if it is empty, check the shared pool. This allows fair sharing while preventing any single key from monopolizing capacity.

A more advanced approach uses **hierarchical token buckets** (HTBs): a parent bucket for the tenant with a high burst, and child buckets for each key with lower independent bursts. A request consumes from the child bucket first; if empty, it takes from the parent, but only if the parent has tokens and the child’s long-term rate is within limits. This prevents one key from draining the parent while still allowing temporary overflow.

Additionally, implement *weighted priority*: enterprise keys can have a “fairness weight” of 5, meaning they consume 5 tokens per request instead of 1, but their bucket refills faster. Noisy low-tier keys consume 1 token rapidly and get blocked sooner, protecting the tenant’s overall quota.

## 4. Headers and Error Messages for API Clients

Clients need to know *when* they are limited and *when* they can retry. Standardize on these HTTP response headers for every rate-limited endpoint:

| Header | Purpose |
|--------|---------|
| `X-RateLimit-Limit` | The maximum allowed requests per window (e.g., `100`) |
| `X-RateLimit-Remaining` | How many requests left in the current window (`42`) |
| `X-RateLimit-Reset` | Unix timestamp (or ISO 8601) when the window/bucket refills (`1651234567`) |
| `Retry-After` | Seconds until the client can retry (e.g., `30`). Use when returning 429. |
| `X-RateLimit-Scope` | Which limit was hit: `key`, `tenant`, `global` (helps debugging) |

When a limit is exceeded, return HTTP 429 Too Many Requests with a JSON body:

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "You have exceeded the rate limit for this API key. Retry after 30 seconds.",
    "scope": "key",
    "retry_after_seconds": 30
  }
}
```

**Critical design rule**: Do **not** include the exact current count in the error message for security reasons—it can leak information about other tenant activity. Use only relative or remaining values.

## 5. Observability: Protecting Reliability without Blocking Legitimate Use

You need to answer three questions in production:
- Are rate limits preventing overload?
- Are legitimate users being blocked unnecessarily?
- Which tenants or integrations are on the edge?

### Key Metrics (expose via statsd, Prometheus, or similar)
- `rate_limiter_requests_total` by tenant, key, endpoint, status (`allowed`, `limited`)
- `rate_limiter_bucket_usage_ratio` (tokens_used / bucket_capacity) per tenant – shows headroom
- `rate_limiter_latency_milliseconds` (time to evaluate limits) – must be sub-millisecond
- `rate_limiter_429_percentage` – alert if above 5% for any tenant (indicates misconfiguration or attack)
- `rate_limiter_quota_exhausted_total` – counts when a tenant’s quota (not rate) is hit (distinct from rate limit)

### Logs
Log rate limit events selectively: every 10th limit event OR sample 1% of allowed requests to reduce noise. Include tenant ID, key ID, endpoint, bucket state, and whether the request was allowed or denied. Never log full request bodies for limited requests—just the metadata.

### Alerts
- **High 429 rate per tenant**: >10% of requests limited for >5 minutes. Investigate aggressively because it means the tenant’s workload is misaligned with their tier.
- **Global rate limit saturation**: If the entire system is near capacity, scaling is needed (add nodes or increase bucket sizes).
- **Bucket starvation for high-value tenants**: If an enterprise tenant consistently runs at 90%+ of their bucket, consider an upgrade conversation, not an alert.

One subtle alert: *rate_limiter_bucket_empty_duration_seconds* – if a tenant’s bucket stays empty for more than 10 minutes during business hours, their integrations are effectively blocked. This is worse than the 429 rate because it signals an unrecoverable blocking state (e.g., a bug in their retry logic).

## Recommended Baseline Design

For a multi-tenant API serving teams of 3 to enterprises with 5000 employees, here is a proven starting point:

1. **Algorithm**: Token bucket per API key with a parent bucket per tenant (hierarchical). Refill rate = 10 tokens/second for small teams, 200 tokens/second for enterprises. Burst allowance = 2x refill rate.
2. **Storage**: Use a fast, distributed key-value store with atomic increment operations (not a relational database). Keep bucket state in memory with periodic persistence.
3. **Configuration**: Tenant tier controls `refill_rate`, `burst`, and `parent_bucket_capacity`. Make these live-reloadable without redeployment.
4. **Headers**: Return all standard rate limit headers plus `X-RateLimit-Scope`. Error 429 with structured JSON and a `Retry-After` header.
5. **Observability**: Track 429 percentage per tenant, bucket utilization ratio, and bucket empty duration. Alert when any tier exceeds 5% 429 rate for 5 consecutive minutes.
6. **Fallback**: If the rate limiter storage is unavailable, default to *allow* (fail open) but log the outage and apply a conservative per-node in-memory rate limit as a last resort.

This baseline ensures small teams get predictable protection from runaway scripts, enterprise customers get fair sharing across their integration portfolio, and you sleep through the night knowing the API won’t fall over from a single noisy tenant.
````
