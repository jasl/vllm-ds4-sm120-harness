# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 8.621245
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2020, "completion_tokens": 1868, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 1868
- Total tokens: 2020

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
# Beyond the Bottleneck: Designing Multi-Tenant Rate Limits for Teams and Enterprises

Backend engineers often conflate rate limiting with authentication or quotas, leading to systems that either block legitimate traffic or fail under duress. For a multi-tenant API serving both small teams and enterprise customers, the design must be nuanced: a single noisy integration inside a large tenant should not degrade service for the rest of that tenant’s users, nor for other tenants entirely. This article unpacks the distinctions, algorithms, fairness mechanisms, client communication, and observability needed to build a resilient, tenant-aware rate limiter.

## 1. Authentication, Authorization, Quotas, and Rate Limits: The Four Pillars

Before designing, clarify each term—confusing them leads to brittle architectures.

- **Authentication**: Verifies *who* the caller is (e.g., API key, OAuth token). It answers: “Is this a valid client?”
- **Authorization**: Determines *what* the caller is allowed to do (e.g., read vs. write, specific endpoints). It answers: “Does this client have permission for this action?”
- **Quotas**: Enforce *how much* a tenant can consume over a billing cycle (e.g., 1 million requests per month, 10 GB of storage). Quotas are coarse, long-term limits tied to pricing plans.
- **Rate Limits**: Control *how fast* a client can send requests over short windows (e.g., 100 requests per second). Rate limits protect system stability, not billing.

A common anti-pattern is using rate limits to enforce quotas (e.g., 1000 requests per hour = a “rate limit”). This misleads clients: once the limit is reached, they must wait—but a quota should simply reject or meter, not impose a sliding window. Keep them separate: quotas for plan enforcement, rate limits for resource protection.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window: Practical Choices

Three algorithms dominate backend rate limiting. Each has trade-offs for multi-tenant fairness.

- **Fixed Window**: Count requests in discrete intervals (e.g., per minute). Simple to implement but suffers from “edge bursts”: 100 requests at 11:59:59 and another 100 at 12:00:00 can overwhelm a system. For multi-tenant, this creates unfairness: a small tenant hitting a window boundary may be throttled while a large tenant gets a free burst.

- **Sliding Window Log**: Tracks timestamps of each request. Most accurate but memory-intensive and slow (O(n) per request). Not practical for high-throughput multi-tenant systems unless using approximate data structures.

- **Token Bucket**: A bucket holds tokens, refilled at a constant rate; each request consumes one token. Bursts are allowed up to bucket size. This is the gold standard for multi-tenant APIs because:
  - Burst capacity caps peaks without punishing historical usage.
  - Refill rate ensures long-term fairness.
  - Easy to configure per tenant (bucket size = burst, refill = sustained rate).

For enterprise tenants, you might set a bucket of 5000 tokens with a refill of 1000/second. For a small team, 200 tokens with 50/second. Token bucket handles the noisy-integration scenario naturally: one misbehaving integration within a tenant consumes its tenant’s tokens faster, but only until the bucket empties, then the entire tenant is throttled together. This leads to our next section.

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

A single overloaded endpoint or misconfigured cron job inside a large enterprise tenant should not degrade all other integrations (e.g., a dashboard user vs. a data pipeline). The solution is **hierarchical rate limiting**:

- **Tenant-level rate limit**: A token bucket for the entire tenant (e.g., 5000 tps burst). This protects the system from that tenant’s aggregate load.
- **Integration-level (or key-level) rate limit**: A nested bucket per API key or integration. If a key burns through its own smaller bucket, it gets throttled independently. The tenant’s other keys continue normally.

Implementation: when a request arrives, check the integration-level bucket first. If tokens remain, then check the tenant-level bucket. This ensures one noisy integration exhausts only its own allocation before the tenant-level bucket is affected.

Additionally, if the noisy integration is critical (e.g., a payment webhook), you can assign a higher priority queue—but that’s a rate limiting extension, not a replacement for hierarchical buckets.

## 4. Headers and Error Messages That Clients Actually Understand

Rate limit feedback must be unambiguous. Return the following headers (HTTP 429 for too many requests):

```
X-RateLimit-Limit: 5000          # total tenant bucket size
X-RateLimit-Remaining: 4231      # remaining tokens in tenant bucket
X-RateLimit-Reset: 1623456789    # Unix timestamp when bucket will refill fully (optional)
Retry-After: 5                   # seconds until at least one token is available (recommended)
```

Additionally, for integration-level throttling:
```
X-RateLimit-Integration-Limit: 200
X-RateLimit-Integration-Remaining: 0
```

Error body (JSON):
```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit. Retry after 5 seconds.",
  "retry_after_seconds": 5,
  "scope": "integration"  // or "tenant"
}
```

Important: never send the system’s internal bucket refill rate. Clients should not know your burst capacity, only their own limit and remaining tokens. This prevents reverse-engineering of your infrastructure.

## 5. Observability: Proving Limits Protect, Not Block

A rate limiter that silently drops requests is dangerous. You need metrics, logs, and alerts that distinguish legitimate blocking from system degradation.

**Metrics** (per tenant and global):
- `rate_limit_checked_total` (counter, labeled by tenant)
- `rate_limit_allowed_total` (counter)
- `rate_limit_throttled_total` (counter, labeled by scope: tenant vs. integration)
- `rate_limit_current_tokens` (gauge, per bucket) – monitors bucket drain.
- `rate_limit_requests_before_first_throttle` (histogram) – measures how many requests a tenant makes before hitting limits.

**Logs**:
- Log every throttled request with tenant ID, integration ID, endpoint, bucket refill rate, and remaining tokens. This helps debug which integrations are misbehaving.
- Log when bucket refills are consumed unusually fast (e.g., >90% of tokens in 1 second) as a warning.

**Alerts**:
- P99 latency increase across all tenants with *no* increase in throttling ratio → system may need higher limits.
- Throttling ratio per tenant exceeds threshold (e.g., >5% of requests) → noisy integration or misconfiguration.
- `rate_limit_throttled_total` drops to zero while traffic is high → rate limiter may be failing open (dangerous).
- Integration-level throttling is frequent for a specific key, but tenant-level bucket is nearly full → that integration is the source.

**Dashboards**: Show per-tenant “remaining tokens” as a heatmap. If enterprise tenants hover near zero tokens during peak hours, they may need a plan upgrade; if small teams hover near zero at all, they may have a noisy integration.

## 6. Recommended Baseline Design

For a multi-tenant API with small teams and enterprises, implement a **two-level token bucket** with the following defaults:

| Tenant Type | Bucket Size (burst) | Refill Rate | Integration Bucket Size | Integration Refill |
|-------------|---------------------|-------------|-------------------------|--------------------|
| Small team  | 200 requests        | 50/sec      | 50 requests             | 10/sec             |
| Enterprise  | 5000 requests       | 1000/sec    | 500 requests            | 100/sec            |

- Use Redis or a similar in-memory store with atomic operations per bucket (no vendor-specific, but a generic key-value store with TTL and Lua scripting works).
- Apply integration-level limits before tenant-level limits.
- Return headers and error bodies with `scope` and `retry_after_seconds`.
- Monitor with the metrics and alerts above.

This design protects the system from bursts, isolates noisy integrations inside tenants, and provides clear feedback to clients. The token bucket’s mathematical property—allowing bursts while enforcing average rate—fits real-world API usage patterns far better than fixed windows. Hierarchical limits ensure fairness across tenants and within them. And with proper observability, you’ll know whether your rate limiter is a shield or a bottleneck.
````
