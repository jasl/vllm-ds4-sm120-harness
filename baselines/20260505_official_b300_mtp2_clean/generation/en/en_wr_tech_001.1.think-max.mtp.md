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
- Elapsed seconds: 13.464984
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2547, "completion_tokens": 2395, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2395
- Total tokens: 2547

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
# Designing Rate Limiting for a Multi-Tenant API: Balancing Protection and Fairness

Building a rate limiting system for a multi-tenant API that serves both small teams and enterprise customers requires careful design. The stakes are high: too aggressive limits break integrations for power users, while too permissive limits risk cascading failures across tenants. This article covers practical design decisions for backend engineers, from core concepts to observability.

## 1. Authentication, Authorization, Quotas, and Rate Limits – Not the Same

Before designing, clarify the four distinct layers every API needs:

- **Authentication** verifies *who* the client is (e.g., API key, OAuth token).
- **Authorization** determines *what* the client is allowed to do (e.g., read vs. write, access specific resources).
- **Quotas** are *allocated capacity over a long period* (e.g., 1 million requests per month) – they govern business agreements, not real-time protection. Quotas are checked after rate limits.
- **Rate limits** are *short-term traffic controls* (e.g., 100 requests per second) that protect system stability. They are enforced in real-time, often before authentication.

Common mistake: treating rate limits as a replacement for quotas. A team that pays for 10,000 requests/day shouldn’t be rate-limited at 10/second unless necessary – and if it is, the error should explain the difference.

## 2. Algorithm Comparison: Token Bucket, Fixed Window, Sliding Window

At a practical level, these three algorithms trade off accuracy, memory, and fairness.

### Token Bucket
- **How it works**: A bucket holds tokens (refreshed at a constant rate). Each request consumes one token. Bursts are allowed up to the bucket size.
- **Best for**: APIs where occasional bursts are acceptable (e.g., CI/CD pipelines that send many requests after a build).
- **Pitfall**: Long idle periods can accumulate tokens, leading to a sudden large burst that may overwhelm downstream services. Practical implementations cap the bucket size.

### Fixed Window
- **How it works**: Count requests per fixed time window (e.g., per second). Reset at window boundaries.
- **Best for**: Simple, predictable workloads (e.g., cron jobs that run on the minute).
- **Pitfall**: The "thundering herd" at window boundaries. At 00:00:00, all clients may send requests simultaneously, causing a spike. Also, a client sending 100 requests at 00:00:59 and 100 at 00:01:00 gets 200 requests in a 2-second span – unfair to other tenants.

### Sliding Window (Log or Counter-Based)
- **How it works**: Maintain a rolling window (e.g., last 60 seconds). Requests older than the window are discarded. Implementations use either request timestamps (accurate, but high memory) or counter approximations.
- **Best for**: Production APIs that need fairness and burst dampening.
- **Pitfall**: Higher memory cost (storing timestamps) or complexity if approximating. For single-request-per-second limits, the overhead is negligible; for thousands of tenants, use a counter-based sliding window (e.g., Redis sorted sets with expiration).

**Practical recommendation**: Use *token bucket* for per-tenant limits to allow natural bursts, but combine with a *sliding window* on a per-API-key level to prevent a single key from exhausting the tenant’s entire token bucket.

## 3. Avoiding Tenant Punishment for a Noisy Integration

Multi-tenant APIs often share infrastructure. A noisy integration (e.g., a misconfigured exporter or a retry loop) from one team should not degrade service for other teams in the same tenant – or worse, for other tenants.

### Key Strategies

**a) Hierarchical limit scoping**
Apply limits at multiple levels, not just tenant-wide. Example structure:
- **Tenant-level**: Global cap (e.g., 500 req/s) – protects the backend.
- **API-key level**: Per-key cap (e.g., 50 req/s) – prevents one integration from consuming the tenant’s entire budget.
- **Integration/endpoint-level**: Optional, for especially heavy endpoints.

**b) Concurrency limits vs. request-rate limits**
A noisy integration might send many requests that each take little time (high rate) or a few requests that take seconds (high concurrency). Use both: a *request rate limit* (req/s) and a *concurrent request limit* (max in-flight). The latter catches slow, blocking calls that stall connection pools.

**c) Dedicated pools or queues**
For enterprise tenants, allocate isolated worker pools or queue partitions. This creates a hard boundary: even if one tenant’s traffic spikes, other tenants’ queues are unaffected. The cost is resource reservation (wasteful for small tenants) but essential for SLA guarantees.

**d) Per-route cost weighting**
Not all requests are equal. A `GET /items` might cost 1 weight unit; a `POST /batch` might cost 5. Rate limit on *weight* rather than raw count. This prevents a cheap request flood from blocking expensive ones.

**e) Sticky rate limiting per source IP/user-agent**
If a tenant uses one integration from a single IP, apply a sub-limit per IP. This doesn’t solve the problem for multi-IP services but helps contain misconfigured on-premise agents.

## 4. Headers and Error Messages

Clients need to understand *why* they were limited and *when* they can retry. Return consistent, machine-readable headers.

### Response Headers (every request)

| Header | Purpose |
|--------|---------|
| `X-RateLimit-Limit` | Maximum allowed requests per window (tenant-level) |
| `X-RateLimit-Remaining` | Remaining requests for the current window |
| `X-RateLimit-Reset` | Unix timestamp (or ISO 8601) when the window resets |

Additionally, for hierarchical limits, include:
| Header | Purpose |
|--------|---------|
| `X-RateLimit-Scope` | Which limit was applied (tenant, key, route) |
| `X-RateLimit-Currently-Allowed` | Whether the request would have been allowed if not for another constraint (useful for debugging) |

### Error Responses (429 Too Many Requests)

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded the rate limit of 500 requests per 60 seconds for this tenant.",
    "limit": 500,
    "remaining": 0,
    "reset_at": "2025-04-27T14:30:00Z",
    "retry_after_seconds": 45,
    "scope": "tenant",
    "documentation_url": "https://docs.api.example.com/rate-limiting"
  }
}
```

**Critical**: Include `retry_after_seconds` – clients often ignore headers, but a numeric value in seconds is easier to parse than a timestamp. Use a monotonic clock for this value.

Also, return a `Retry-After` header (HTTP standard) with the same seconds value so load balancers and CDNs can interpret it.

### When to warn, not reject

For tenants approaching their limit, include a warning header:
`X-RateLimit-Warning: "approaching limit: 450/500 used. Reset in 300 seconds."`

This allows proactive clients to slow down before hitting errors.

## 5. Observability – Are Limits Protecting or Blocking?

Without observability, rate limiting is a black box. Engineers should know if limits are preventing overload or silently blocking legitimate traffic.

### Key Metrics (prometheus-style, but can be counters)

- **`rate_limit_requests_total`** – by tenant, key, result (allowed / blocked)
- **`rate_limit_blocked_requests_total`** – by reason (tenant limit, key limit, concurrency limit, system overload)
- **`rate_limit_current_usage_percent`** – gauge, per tenant (current usage / limit) – useful for capacity planning
- **`rate_limit_window_seconds`** – histogram of the time requests spend in the rate limiter (to detect slow implementations)
- **`rate_limit_concurrent_requests`** – gauge, per tenant (number of in-flight requests)
- **`rate_limit_changes`** – audit log of limit adjustments (who changed what and when)

### Alerts

- **Rate limit hit ratio > 90%**: If a tenant is consistently near its limit, it’s a sign they need a plan upgrade or their integration is overly aggressive. Don’t alert on a single spike.
- **Rate limit error rate > 5% for 5 minutes**: Indicates a configuration change (maybe limits too tight) or a retry storm. Pager-worthy.
- **Rate limit limiter latency > 50ms**: The rate limiter itself is becoming a bottleneck. Scale the rate limiter’s storage (e.g., Redis cluster) or switch to a local, distributed algorithm.
- **Concurrent requests approaching CPU/connection pool limit**: Rate limits are not enough – the system is still overloaded. Look at queue depth and backpressure signals.

### Logs

Log every blocked request with:
- Tenant ID
- API key prefix (never log full keys)
- Route
- Limit applied (value and scope)
- Retry-After value
- Request duration (to correlate with load)

Use structured logging (JSON) so you can aggregate by tenant and route. A single tenant blocking 10,000 requests per minute might be a misconfiguration, not an attack.

## 6. Recommended Baseline Design

For a multi-tenant API with small teams and enterprise customers, start with this:

1. **Algorithm**: Token bucket per tenant (for bursts) + sliding window per API key (for fairness). Store state in a replicated in-memory cache (Redis or similar) with per-key TTL.
2. **Limit tiers**:
   - Small teams: 100 req/s tenant, 20 req/s per key, 10 concurrent requests.
   - Enterprise: 1000 req/s tenant, 200 req/s per key, 100 concurrent requests.
   - All tiers: weight-based costing (e.g., batch endpoints cost 5x).
3. **Headers**: Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`, and scope information on every response. `X-RateLimit-Warning` when above 80% usage.
4. **Error response**: Always 429 with a stable error code, a human-readable reason, and `retry_after_seconds`.
5. **Observability**: Track allowed vs. blocked by scope. Alert on high hit ratio and high limiter latency. Log every block event with tenant, key, and route.
6. **Isolation**: Place enterprise tenants on a dedicated worker pool with a separate rate limiter instance. For small teams, share the pool but enforce key-level limits aggressively to contain noisy integrations.

Start conservative – you can always relax limits. Monitor latency and error rates before and after deployment. And never, ever rate-limit health check endpoints.
````
