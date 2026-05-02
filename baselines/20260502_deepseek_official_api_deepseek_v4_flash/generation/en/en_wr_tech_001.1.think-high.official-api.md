# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-v4-flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 35.953284
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "completion_tokens": 2808, "total_tokens": 2960, "prompt_tokens_details": {"cached_tokens": 128}, "completion_tokens_details": {"reasoning_tokens": 820}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 24}`
- Prompt tokens: 152
- Completion tokens: 2808
- Total tokens: 2960

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
We need to write a technical article for backend engineers about designing rate limiting for a multi-tenant API used by small teams and enterprise customers. The article must be 800-1000 words, no code, no vendor-specific services. Must cover: difference between auth/authz/quotas/rate limits; token bucket vs fixed window vs sliding window practical; avoid punishing entire tenant for one noisy integration; headers/error messages; observability metrics/logs/alerts. End with "recommended baseline design". Need to structure as a coherent article with a title. Title: up to us. Let's think of a good title: "Rate Limiting for Multi-Tenant APIs: Balancing Protection and Fairness Across Teams and Enterprises" or something similar. Keep it technical but clear.

We'll write in a professional, instructive tone. No code, so use descriptions. Ensure word count. Let's outline:

1. Introduction: Multi-tenant APIs face unique challenges. Different tenants have different needs. Need to protect reliability without blocking legitimate use.

2. Clarify terms: Authentication (who you are), Authorization (what you can do), Quotas (how much you can use over a long period), Rate limits (how fast you can use). Distinguish clearly. Example: quota = 100k requests per day, rate limit = 100 requests per second.

3. Algorithms comparison: Token bucket (smooth, allows bursts, good for variable workloads), Fixed window (simple but allows bursts at boundaries, can cause spikes), Sliding window (more precise, avoids boundary effects but more complex). Practical considerations: Token bucket often preferred for APIs because it handles bursts gracefully. Need to implement with per-tenant keys, possibly per-endpoint or per-user.

4. Avoiding punishing entire tenant: Use per-tenant limits, but also per-key (API key) limits within a tenant. If one integration is noisy, it should hit its own limit, not affect other keys in same tenant. Also consider hierarchical limits: tenant-level limit (aggregate) and key-level limit. When a key is throttled, other keys still have their own limits. Also implement "priority" or "cost" based limiting for enterprise vs small teams? Not required but can mention. Use separate rate limit counters per key, with a global tenant limit as a secondary check.

5. Headers and error messages: Standard headers like X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset (or Retry-After). For multi-tenant, clarify which limit is being reported. Return 429 Too Many Requests with JSON body explaining which limit exceeded (e.g., "key rate limit exceeded" vs "tenant rate limit exceeded"). Include Retry-After header in seconds. Use consistent error codes.

6. Observability: Metrics: per-tenant request rates, throttle rates, error rates by status code. Latency distributions. Logs: each request with tenant ID, key ID, whether rate limited, which limit triggered. Alerts: when overall tenant error rate due to rate limiting exceeds threshold (e.g., >1% of requests being throttled? Actually throttling is intentional, but if many throttles it may indicate under-provisioning). Also alert on sudden spikes in throttling for a tenant, or on excessive retries from clients. Monitor tail latency to see if rate limiting is causing contention.

7. Recommended baseline design: Use token bucket per API key (or per user) with a tenant-level token bucket as a "parent" that can limit aggregate concurrency. Use hierarchical token buckets. Set limits based on tier (small team vs enterprise). Return standard headers and error messages. Log all throttle events. Alert on tenant-level throttle rate exceeding 5% of total requests for that tenant. Monitor per-key usage to identify noisy integrations. For enterprise, allow higher bursts but with cost.

Need to keep length 800-1000. Write concisely. No code, so describe algorithms in prose.

Let's write.
```

## Assistant

````markdown
# Rate Limiting for Multi-Tenant APIs: Balancing Protection and Fairness Across Teams and Enterprises

When you design an API that serves both small teams and large enterprises under the same infrastructure, rate limiting becomes a chess game. Small teams need low latency and minimal friction; enterprises demand high throughput and predictable behavior. Meanwhile, a single misconfigured integration from one enterprise user can cascade into degraded performance for every other tenant. This article walks through the key decisions and practical trade-offs you’ll face when building a rate‑limiting layer that protects reliability without punishing legitimate use.

## Clarifying the Vocabulary

Before diving into algorithms, it’s essential to distinguish four concepts that are often conflated:

- **Authentication** verifies *who* the caller is (e.g., API key validation, OAuth token).
- **Authorization** determines *what* the caller is allowed to do (e.g., read vs. write, access to specific resources).
- **Quotas** are long‑term usage allowances (e.g., 100,000 requests per day, 10 GB of storage).
- **Rate limits** control the *velocity* of requests (e.g., 100 requests per second).

Quotas are enforced over hours or days; rate limits smooth traffic in seconds or minutes. While both protect backend resources, they serve different purposes. A user can hit their daily quota while still being rate‑limited at the second level, and vice versa.

## Algorithm Selection: Practical Trade‑Offs

Three common algorithms meet most multi‑tenant needs. Each has strengths and weaknesses when applied at scale.

### Token Bucket
Tokens are added at a fixed rate (e.g., 10 tokens per second) up to a maximum bucket size (e.g., 200 tokens). Each request consumes one token. Unused tokens accumulate, allowing short bursts. This is the most intuitive for APIs: a team can “sprint” when needed (e.g., after an idle period) but cannot sustain a rate above the refill. The downside is implementation complexity – you need to maintain per‑tenant or per‑key counters, and tokens must be refilled either periodically or in a background loop.

### Fixed Window
Divide time into discrete windows (e.g., one second). Count requests within the window; reject once the limit is hit. Implementation is trivial (a Redis key with TTL). The problem: traffic spikes at window boundaries. If a tenant sends 100 requests at 00:00:00.999 and another 100 at 00:00:01.001, they effectively double the allowed rate. For enterprise customers running near their limit, this can cause unpredictable throttling.

### Sliding Window
Maintain a log of timestamps for each request or use a rolling window counter (e.g., via sorted sets or probabilistic data structures). This eliminates boundary spikes but increases memory and CPU per request. For a multi‑tenant system with hundreds of thousands of distinct keys, the overhead can become significant.

**Practical recommendation**: Use token bucket as your primary algorithm for per‑key limits. It offers the best trade‑off between burst tolerance and algorithmic simplicity when implemented with a sliding‑window refill strategy (e.g., refill tokens on the fly using the elapsed time since the last update). For aggregate tenant limits, a fixed window with a small bucket size can work, but you must monitor boundary effects and possibly adopt sliding windows for high‑tier tenants.

## Avoiding Punishment for the Whole Tenant

One noisy integration – a polling client with an aggressive retry loop – should not degrade the experience of other teams or services using the same tenant account. The solution is **hierarchical rate limiting**:

1. **Per‑key limits** (e.g., per API key or per user token) are the first gate. Each key operates independently with its own token bucket.
2. **A tenant‑level limit** acts as a second gate. When any key in the tenant consumes a token, a parent counter is also debited. If the tenant‑level bucket is empty, *all* keys within that tenant are throttled – but ideally this only happens when the aggregate traffic is truly excessive.

The hierarchy must be implemented with **fair queuing** in mind. For example, if tenant A has a limit of 1000 requests per second and two API keys each try to send 1000 req/s, both will be throttled (since sum > tenant limit). But if only one key misbehaves (800 req/s) while the other is calm (200 req/s), the calm key should never see a 429. Achieving this requires the tenant bucket to be “borrowed” from each key in proportion – a token bucket with per‑key weight is the simplest way.

Additionally, consider **cost‑based limiting**: assign each endpoint a “cost” (e.g., 1 token for a lightweight GET, 10 tokens for a bulk write). A noisy integration hammering an expensive endpoint will exhaust its own key bucket quickly without affecting other keys that use cheaper endpoints.

## What to Return to Clients: Headers and Errors

Every rate‑limited API must communicate clearly. Use standard headers that clients can parse programmatically:

- `X-RateLimit-Limit`: The maximum requests allowed in the current window (e.g., 1000).
- `X-RateLimit-Remaining`: The number of requests left before throttling.
- `X-RateLimit-Reset`: Unix timestamp (or seconds until reset) when the limit will refresh.

For multi‑tenant systems, be precise about *which* limit was hit. Include a header like `X-RateLimit-Scope: key` or `X-RateLimit-Scope: tenant` so clients can distinguish a per‑key throttle from a tenant‑level throttle.

The HTTP 429 status code must include a body with a clear message:

```json
{
  "error": "rate_limit_exceeded",
  "scope": "key",
  "message": "This API key has exceeded its rate limit. Retry after 12 seconds.",
  "retry_after_seconds": 12
}
```

If the tenant limit is exceeded, the message changes to indicate that all keys under the tenant are affected. This helps enterprise customers pinpoint the root cause – often a misconfigured integration elsewhere in their org.

**Important**: Return a `Retry-After` header (in seconds). Clients using exponential backoff will respect this automatically. Without it, they may retry immediately, compounding the load.

## Observability: Metrics, Logs, Alerts

Rate limiting is only useful if you know it’s working – and not over‑restricting legitimate traffic. Instrument the following:

**Metrics** (per tenant, per key):
- `requests_total`, `throttled_total` (by 429 status)
- `rate_limit_remaining` (average or percentile) – helps see if limits are too generous or too tight
- `rate_limit_exhausted` (count of times a key’s bucket became empty)
- `tenant_throttle_share` (percentage of tenant requests that were throttled)

**Logs** for every throttling event: tenant ID, key ID, endpoint, scope (key or tenant), and the current bucket levels. This is invaluable for debugging “my calls are being dropped” complaints.

**Alerts**:
- **Tenant throttle rate > 5%**: If more than 5% of a tenant’s requests are being throttled, it indicates the tenant is regularly exceeding their allowance. This may be acceptable for some tenants, but you should notify the support team or auto‑escalate.
- **Key throttle rate > 20% for >5 minutes**: A single key is likely misconfigured. Proactive outreach to the tenant can prevent frustration.
- **P99 latency spike coinciding with high throttle rate**: Could indicate that the rate limiter itself is becoming a bottleneck. Investigate if the data store (e.g., Redis) is saturated.
- **Unexpected drop in throttle rate**: If throttling suddenly vanishes, check if the rate‑limiter is still healthy – a bug could silently disable enforcement.

## Recommended Baseline Design

For a multi‑tenant API serving both small teams and enterprise customers:

1. **Use per‑key token buckets** with a server‑side sliding refill. Set default limits per tier (e.g., 10 req/s for free, 100 req/s for enterprise).
2. **Add a tenant‑level token bucket** as a backstop. The tenant limit should be approximately (number of keys) × (per‑key limit) – but with a cap to prevent aggregate abuse.
3. **Enforce per‑endpoint cost weights** to prevent expensive operations from starving cheaper ones.
4. **Return standard headers** (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`) with a `Retry-After` header on 429 responses. Include a `scope` indicator.
5. **Emit throttling logs** with tenant and key identifiers, and **alert** when a tenant’s throttle rate exceeds 5% or a single key’s rate exceeds 20%.
6. **Monitor aggregate throttle rates** across all tenants to ensure the rate limiter is not blocking legitimate traffic due to excessive global limits.

By layering per‑key and per‑tenant limits, you allow small teams to burst freely while preventing any one enterprise integration from monopolizing shared resources. The result is a system that feels fast, fair, and predictable – regardless of tenant size.
````
