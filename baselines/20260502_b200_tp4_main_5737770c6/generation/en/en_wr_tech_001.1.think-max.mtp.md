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
- Elapsed seconds: 9.841712
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2328, "completion_tokens": 2176, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2176
- Total tokens: 2328

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
# Designing Rate Limits for a Multi-Tenant API Serving Both Small Teams and Enterprise Customers

**By [Your Name]**

## 1. Clarifying the Four Pillars of Access Control

Before designing rate limiting, we must distinguish four related but distinct concepts that often get conflated:

**Authentication** answers *who* you are. It verifies identity via API keys, OAuth tokens, or mTLS. Without authentication, rate limiting has no subject to bind to.

**Authorization** answers *what you are allowed to do*. It checks permissions (e.g., “can this team read the /admin/reports endpoint?”). Rate limits are not authorization—they cap usage regardless of permissions.

**Quotas** are *hard, long-term caps*—typically monthly or daily—enforced for billing or resource planning. A quota might say “5 million requests per month.” Once exhausted, the tenant is blocked until the next period. Quotas are rigid and often require a plan upgrade.

**Rate limits** are *short-term burst controls*—seconds to minutes—designed to prevent system overload, not to cap total usage. A rate limit might say “100 requests per second.” A tenant can hit it, back off, and resume. Rate limits protect stability; quotas protect business logic.

In a multi-tenant system, rate limits are per-tenant (or per-user within a tenant), while quotas are per-plan.

## 2. Window Algorithms: Practical Trade-Offs

Three algorithms dominate production rate limiters. Here is how they behave under multi-tenant load.

### Token Bucket
- **How it works**: A bucket holds tokens that refill at a fixed rate (e.g., 100 tokens refilled per second). Each request consumes a token. Bursts are allowed up to the bucket size (e.g., 200 tokens).
- **Why it wins**: Handles natural traffic spikes without rigid boundaries. A team that is idle for 10 seconds can burst 1,000 requests (if bucket size = 1,000). No “thundering herd” at window edges.
- **Trade-off**: Requires state (the bucket fill level) per tenant, per minute granularity. Memory grows linearly with tenant count. For 50,000 tenants, you need 50,000 counters. Acceptable with Redis or a local in-memory store with persistence.

### Fixed Window
- **How it works**: Count requests in a static time window (e.g., 1 minute). If count exceeds limit, reject until the next window.
- **Why it fails**: A tenant sending 3,000 requests in the last 10 seconds of minute N, then another 3,000 in the first 10 seconds of minute N+1, sees a 6,000 request burst—double the intended rate. This punishes polite tenants while noisy ones exploit edge cases.
- **Trade-off**: Simple to implement (one counter per tenant per window) but poor for bursty workloads.

### Sliding Window (Log or Counter)
- **How it works**: Reject if requests in the last 60 seconds exceed N. Implemented either by storing timestamped logs (O(n) memory) or using a weighted counter that approximates the sliding window.
- **Why it matters**: Smoother than fixed window, avoids edge-case bursts. No unrealistic spikes at minute boundaries.
- **Trade-off**: Log-based sliding window is memory-heavy for high-throughput tenants (thousands of timestamps). Weighted sliding window (e.g., Redis Sorted Set or a hybrid counter) is more efficient but slightly less precise.

**Practical advice**: Prefer token bucket for burst-friendly APIs, or sliding window if you must guarantee a hard ceiling. Avoid fixed window unless you can tolerate edge-case spikes.

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

A common anti-pattern: apply a single rate limit keyed on `tenant_id`. If one integration inside that tenant misbehaves (e.g., a webhook client retrying with exponential backoff gone wrong), it consumes the entire tenant’s budget. All other integrations—and all human users—are blocked.

**Solution: Rate-limit at the API key level, not the tenant level.**

- Every API request carries a key. The key is bound to a specific user, service account, or integration.
- The primary rate limit applies to that key. If key A fires 500 req/s and the limit is 100 req/s, only key A is throttled.
- A secondary, *higher* rate limit applies to the tenant as a whole (e.g., 10× the per-key limit). This protects against a tenant creating many keys to bypass per-key limits.

**Exception handling**: If a single key consumes the tenant’s secondary limit, *still block only that key*. Log a critical alert for the tenant admin: “Your key [XYZ] is causing tenant-wide throttling.” The tenant’s other keys remain operational.

This design prevents one misconfigured CI/CD pipeline from taking down an entire enterprise customer.

## 4. Headers and Error Messages: What Clients Need

Every rate-limited response must give the client enough information to react intelligently. Follow the IETF draft standard (`draft-ietf-httpapi-ratelimit-headers`).

### Headers on every response (successful or throttled):
| Header | Meaning | Example |
|--------|---------|---------|
| `X-RateLimit-Limit` | The maximum requests allowed in the window | `100` |
| `X-RateLimit-Remaining` | Requests left in the current window | `87` |
| `X-RateLimit-Reset` | Unix timestamp when the window resets | `1719955200` |

### On throttling (HTTP 429 Too Many Requests):
Add these to the `429` response:
| Header | Meaning | Example |
|--------|---------|---------|
| `Retry-After` | Seconds to wait before retrying | `12` |
| `X-RateLimit-Key` | The API key that was throttled | `sk_live_abc123` |
| `RateLimit-Type` | Which limit was hit: `per_key`, `per_tenant`, or `burst` | `per_key` |

### Error body:
```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit for API key sk_live_abc123. 87 requests allowed per second. Retry after 12 seconds.",
  "details": {
    "limit": 100,
    "remaining": 0,
    "reset_at": 1719955200,
    "throttled_key": "sk_live_abc123",
    "throttled_reason": "per_key"
  }
}
```

Do *not* return internal tenant IDs or IP addresses. Keep the message actionable.

## 5. Observability: Knowing Whether Limits Work

Without observability, rate limiting becomes guesswork. You need answers to three questions:

- Are we throttling too often (blocking legitimate traffic)?
- Are we not throttling enough (overloading the system)?
- Is one tenant causing disproportionate harm?

### Metrics (expose via Prometheus or similar):
- `rate_limit_requests_total { tenant, key, action="allowed|throttled" }` – count of requests.
- `rate_limit_throttled_requests_total { tenant, reason="per_key|per_tenant|burst" }` – breakdown by limit type.
- `rate_limit_bucket_fill_ratio { tenant }` – for token bucket, how full is each bucket (0 = empty, 1 = full). Useful to detect persistent near-empty buckets.
- `rate_limit_cost_per_request_p99` – latency added by the rate limiter itself. Should be <1ms.

### Logs (structured, sampled):
Log all throttled requests (sampled 1:1). Log allowed requests at 1% sample to reduce noise. Include:
- `tenant_id`, `key_id`, `reason`, `window_start`, `reset_at`, `current_count`.

### Alerts:
- **High throttling rate globally**: >5% of all requests returning 429. This indicates either a legitimate attack or a too-aggressive limit.
- **Single tenant consuming >50% of total allowed requests**: Could be a misbehaving integration or traffic migration.
- **Rate limiter latency >10ms p99**: The limiter itself is becoming a bottleneck. Consider moving logic to a local cache or edge.

**Baseline**: When throttling is <1% of total requests, your limits are likely safe for legitimate traffic. When >10%, revisit your limits or talk to the tenant.

## 6. Recommended Baseline Design

For a multi-tenant API serving both small teams (10 req/s typical) and enterprise customers (500 req/s typical):

1. **Algorithm**: Token bucket per API key. Bucket size = 2× the per-key limit (allows short bursts). Secondary token bucket per tenant with bucket size = 10× the per-key limit.

2. **Key hierarchy**: Rate limit at `api_key` level first. If any key hits its limit, apply backpressure. Only throttle the tenant-level bucket if a single key is burning through it (rare). In that case, throttle that key, not the tenant.

3. **Storage**: Redis for counters (token bucket state), with TTL equal to the refill interval. For multi-region, use a fast local cache with async Redis sync.

4. **Headers**: Always return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. On 429, also return `Retry-After`, `X-RateLimit-Key`, and `RateLimit-Type`.

5. **Observability**: Expose per-tenant and per-key throttle counts as metrics. Alert when per‑tenant throttling exceeds 0.1% of that tenant’s requests—this catches noisy integrations early.

6. **Graceful degradation**: If Redis is unreachable, allow requests (fail open) but log the event. A brief spike of unthrottled traffic is better than a full API outage for all tenants.

This design ensures small teams get predictable limits, enterprise customers get high bursts, and one misbehaving CI pipeline never takes down an entire company.
````
