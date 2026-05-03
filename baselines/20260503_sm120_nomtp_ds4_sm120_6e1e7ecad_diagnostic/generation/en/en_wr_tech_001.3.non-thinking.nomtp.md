# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 34.86902
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2384, "completion_tokens": 2232, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2232
- Total tokens: 2384

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
# Beyond the Blunt Hammer: Designing Rate Limits for Multi-Tenant APIs

**By: [Your Name]**

Every backend engineer eventually faces the same bitter lesson: an API without rate limiting is an API waiting to be accidentally (or maliciously) DoS’ed by its own customers. But when your API serves both a five-person startup and a Fortune 500 enterprise with dedicated integration teams, a one-size-fits-all rate limit is not just unfair—it’s dangerous. It punishes the loyal while failing to protect the infrastructure.

This article walks through the practical engineering decisions behind rate limiting for a multi-tenant API, focusing on the nuances that separate a working system from a production incident waiting to happen.

## 1. The Four Pillars: Authentication, Authorization, Quotas, and Rate Limits

Before designing anything, we must clarify the vocabulary. Confusing these four leads to implementation that feels wrong, scales poorly, or violates security.

- **Authentication** answers “Who are you?” It establishes identity via API keys, OAuth tokens, or mTLS certificates. Without it, you cannot apply any of the following.

- **Authorization** answers “What are you allowed to do?” It checks permissions: “Can this tenant write to the billing endpoint?” Rate limiting is not authorization. A tenant can be authorized to call an endpoint but still be rate-limited.

- **Quotas** are **long-term, cumulative limits** over a billing cycle: “You may make 100,000 API calls this month.” They are enforced at the end of the cycle (soft) or rejected mid-cycle (hard). Quotas are about *capacity planning and billing*.

- **Rate limits** are **short-term, sliding constraints** to protect infrastructure health: “You may make 100 requests per second.” They prevent a burst from overwhelming shared resources—databases, queues, workers.

**Key insight:** Quotas are a business contract. Rate limits are an operational safety net. A tenant that hits its quota should be told “upgrade your plan.” A tenant that hits a rate limit should be told “slow down—your burst is hurting the system.”

## 2. Algorithm Showdown: Token Bucket, Fixed Window, Sliding Window

Three algorithms dominate discussion. At a practical level, one is almost always the right choice for multi-tenant APIs.

### Fixed Window
Divide time into discrete windows (e.g., 1 second). Count requests in each window. Exceed the limit? Reject until the next window.

**Practical problem:** Burst at the boundary. A tenant sends 100 requests in the last millisecond of window N, then 100 requests in the first millisecond of window N+1. In 2 milliseconds, they made 200 requests—effectively double the intended rate. The system still sees 100 in each window. This defeats the purpose of rate limiting and creates unpredictable load.

### Sliding Window Log
Track a timestamp for each request. Count requests within the last, say, 60 seconds. This eliminates boundary bursts but requires O(n) storage per tenant. For thousands of tenants with high throughput, this becomes a memory and GC nightmare. It also introduces latency if the window is checked via a centralized store like Redis (SCAN + ZREMRANGEBYSCORE under load hurts).

### Token Bucket
Imagine a bucket that fills at a constant rate (refill rate) and holds a maximum number of tokens (burst capacity). Each request consumes one token. If the bucket is empty, the request is rejected. The bucket is *not* tied to a clock window—it’s a pure sliding mechanism.

**Why it wins for multi-tenant APIs:**
- **Allows short bursts** (the bucket can hold tokens for up to the burst capacity).
- **Smooths long-term rate** regardless of wall-clock windows.
- **Memory efficient:** One integer per tenant (current token count) + one timestamp (last refill time). You can even lazily calculate fills on access.
- **Fair under micro-bursts:** A tenant cannot exploit window edges because there are no windows.

**Trade-off:** Token bucket is not perfectly precise for “exactly N per hour” (that’s a quota). But for rate limiting, it is the gold standard. Implement it with a simple Lua script in Redis or a local in-memory structure per API instance (if you can tolerate eventual consistency across replicas).

## 3. Isolation: Don’t Punish an Entire Tenant for One Noisy Integration

Multi-tenant APIs often share a pool of workers. If you apply a single global rate limit per tenant, one misbehaving integration—say, a webhook client that loops on errors—can consume all of that tenant’s tokens, starving their legitimate users (e.g., their own customers calling your API via their app).

**Solution: Nested rate limit keys.**

Design a hierarchy:
1. **Tenant-level limit** (e.g., 1,000 req/s). This is the hard ceiling.
2. **Integration-level limit** (e.g., 100 req/s per API key or per client ID). This is the soft isolation.

When a request arrives, you check the integration-level bucket first. If it exceeds its sub-limit, reject immediately—that specific integration is blocked, but the tenant’s other integrations remain untouched. Only when a *global tenant burst* happens do you fall back to the tenant-level bucket.

**Practical implementation detail:** The integration-level limit should be stricter than the tenant-level, but they are not additive. If a tenant has 10 integrations each with 100 req/s, but the tenant cap is 500 req/s, the effective limit is min(integration sum, tenant cap). This prevents a tenant from increasing their limit simply by creating more API keys.

## 4. Headers and Error Messages: The Client Needs to Self-Heal

Rate limiting is only useful if clients can respond intelligently. Return these headers on every response, whether successful or rejected:

- `X-RateLimit-Limit`: The maximum requests allowed in the current rate limit window (or per second for token bucket). Tell the client the ceiling.
- `X-RateLimit-Remaining`: How many tokens remain in the bucket at the moment the response was sent. Use this with care—it’s a snapshot and can change instantly.
- `X-RateLimit-Reset`: For token bucket, this is problematic because there is no fixed reset time. Instead, return `Retry-After` in seconds for *throttled* responses. This is the single most important header for self-healing clients.

**Error responses:**

For 429 Too Many Requests:
```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit for this endpoint. Please reduce your request rate and retry after the specified Retry-After period.",
  "retry_after_seconds": 30
}
```

Crucially, *differentiate from quota violations*. Do not return 429 for quota errors. Use 403 Forbidden with `error: "quota_exceeded"` and a link to the billing portal. This avoids client confusion and support tickets.

## 5. Observability: Do the Limits Actually Work?

A rate limiter that never triggers is either too generous or dead code. A rate limiter that triggers constantly is blocking legitimate use. Observability must answer both sides.

### Metrics (every 15s or via histogram)
- `rate_limit.hits`: Total requests evaluated.
- `rate_limit.throttled`: Count of 429 responses, broken down by `tenant_id`, `integration_id`, and `endpoint`.
- `rate_limit.token_bucket_usage_pct`: Average fill level of the token bucket per tenant. If this stays near 100% for a premium tenant during normal load, your limits might be too low.
- `rate_limit.retry_after_seconds`: Distribution of wait times. If most are < 1s, clients can retry immediately—fine. If median is > 30s, you’re causing severe degradation.

### Logs
Log every throttled request with:
- `tenant_id`, `integration_id`, `endpoint`, `method`.
- `context`: Was this a tenant-level or integration-level rejection?
- `current_bucket_level`: Helps debugging false positives.

Do **not** log every successful request—that’s a firehose. Use sampled logging for success paths.

### Alerts
- **High throttle rate for a single tenant:** If one tenant is being throttled >5% of their requests, alert. That tenant has a noisy integration or misconfigured client.
- **Global throttle rate rising:** If overall 429 rate exceeds 1% of traffic, investigate load drivers. Are your limits too low, or is there an attack?
- **Bucket depletion for critical tenants:** If a VIP enterprise tenant’s token bucket stays near zero during their normal business hours, your limits are too tight. Alert the engineering team, not the tenant.

## 6. Recommended Baseline Design

For a generic multi-tenant API serving 10 to 10,000 tenants:

- **Algorithm:** Token bucket. Redis-backed for distributed consistency (one key per tenant, one key per integration). Lua script for atomic check-and-consume. TTL on keys to auto-clean idle tenants.
- **Default limits:** 100 req/s per tenant (burst 200); 20 req/s per integration (burst 40). Adjust via per-tenant configuration in a database table that feeds a hot reload cache (e.g., a 30-second TTL Redis hash).
- **Key hierarchy:** `rate_limit:{tenant_id}:global` → `rate_limit:{tenant_id}:integration:{integration_id}`.
- **Headers:** Every response includes `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After` on 429.
- **Observability:** StatsD or Prometheus counters with tenant/integration labels. Alerts on >5% throttling for any tenant with >1,000 requests/minute.
- **Fallback:** If Redis is down, fall back to an in-memory token bucket with a per-instance rate limit *higher* than normal (and log loudly). Do not block traffic on a rate limiter outage.

Rate limiting is not about punishing users—it’s about protecting the system so that users can keep using it. When designed with isolation, clear signals, and observability, it becomes invisible infrastructure. When done poorly, it becomes a support ticket factory. Choose token bucket, isolate integrations, and measure everything. Your tenants—and your on-call engineer—will thank you.
````
