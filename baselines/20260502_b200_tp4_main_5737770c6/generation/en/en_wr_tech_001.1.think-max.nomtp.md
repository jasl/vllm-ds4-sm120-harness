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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 15.297373
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2303, "completion_tokens": 2151, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2151
- Total tokens: 2303

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
# The Multi-Tenant Rate Limiting Tightrope: Protecting Reliability Without Breaking Integration

**By: [Your Name]**
*For backend engineers building shared infrastructure that must serve both scrappy startups and Fortune 500 procurement systems*

Rate limiting is one of those topics that seems simple until you have to do it right in a multi-tenant API. A single bursty integration from a small team can degrade performance for an enterprise customer's entire tenant—but applying the same rigid limits to both can break legitimate workflows. This article walks through the design decisions that separate a system that protects reliability from one that frustrates users.

---

## 1. Authentication, Authorization, Quotas, and Rate Limits: Know the Layers

Before designing anything, we must be precise about what we’re building. These four concepts are often conflated, but they serve fundamentally different purposes:

- **Authentication** answers *who you are*. It’s the gate—validating API keys, JWTs, or OAuth tokens. Without it, no other checks happen.

- **Authorization** answers *what you are allowed to do*. It checks scopes, roles, or resource-level permissions. A token might authenticate a user, but authorization determines whether they can call `POST /billing`.

- **Quotas** define *how much you can use over a long period*. They are typically enforced monthly or daily and are contractual (e.g., "Enterprise plan: 1,000,000 requests per month"). Exceeding a quota often results in a 402 or a 403 with a clear billing error.

- **Rate limits** control *how fast you can use the API*. They are enforced over short windows (seconds to minutes) and exist to protect system stability. A rate limit violation (429 Too Many Requests) should never be about billing—it’s about fairness and resource preservation.

**Key insight for multi-tenant**: Quotas are per-tenant and tied to billing; rate limits should be per-tenant *and* per-client to isolate noisy neighbors. A client hitting 100 req/s should not block another client under the same tenant.

---

## 2. Choosing the Right Algorithm: Token Bucket, Fixed Window, or Sliding Window

Practical trade-offs matter more than theoretical elegance.

### Fixed Window
The simplest: reset a counter at the start of each minute. If counter > limit, reject.

- **Pros**: Easy to implement, low memory, atomic counters work fine.
- **Cons**: Traffic spikes at the window boundary. If limit is 100 req/min and a client sends 100 requests in the last second of minute N, then 100 more in the first second of minute N+1, the system sees 200 requests in 2 seconds. This defeats the purpose.
- **When to use**: Coarse throttling where burst tolerance is acceptable (e.g., batch reporting endpoints).

### Sliding Window Log
Track a list of timestamps per client. On each request, remove timestamps older than the window, count remaining, reject if count >= limit.

- **Pros**: Smooths out boundary bursts. Accurate to the millisecond.
- **Cons**: Memory usage grows with request volume. Log maintenance (pruning old timestamps) adds CPU overhead.
- **When to use**: High-precision limits where clients expect consistent latency.

### Token Bucket
A bucket holds tokens; tokens refill at a fixed rate. Each request consumes one token. If the bucket is empty, the request is rejected or queued.

- **Pros**: Naturally allows bursts equal to bucket size. Easy to implement with Redis or in-memory counters. Refill rate smooths out traffic over time, no boundary spikes.
- **Cons**: Slightly more complex than fixed window. Bursts can still be large if bucket size is set too high.
- **When to use**: The general-purpose choice. Most production systems use a variant.

**Recommendation**: Start with **token bucket per client + per tenant cap**. This gives each integration its own burst allowance while providing a ceiling for the entire tenant.

---

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

This is the hardest design challenge. Imagine: Acme Corp has a CRM integration hammering your API at 500 req/s, and a separate HR tool under the same tenant that sends 2 req/min. If you rate-limit at the tenant level, the HR tool gets 429s for absolutely no reason.

**Solution: Hierarchical (two-level) rate limiting**.

- **Level 1 (Client-level)**: Each API key or integration gets its own token bucket. This isolates noise. The CRM integration hits its own limit and is throttled, while the HR tool continues normally.
- **Level 2 (Tenant-level)**: A separate bucket that tracks *total requests across all clients for the tenant*. If the cumulative traffic exceeds a tenant-wide threshold (e.g., 10x the highest client limit), throttle *all* clients under that tenant.

Why the tenant cap? Because even if each client stays under its limit, ten clients each running at 80% could still overwhelm the backend. The tenant cap provides a safety valve. When it trips, you return 429 with a clear message: *"Your tenant's combined traffic exceeded capacity. Please review your integration patterns."*

**Practical enforcement**: Use Redis with separate keys:
- `rate_limit:{tenant_id}:{client_id}` for client-level
- `rate_limit:{tenant_id}:global` for tenant-level

On each request, check and decrement the client bucket first. If allowed, then check and decrement the tenant bucket. If the tenant bucket is empty, reject—even if the client bucket still has tokens.

---

## 4. What Headers and Error Messages Should You Return?

Clients need to adjust their behavior automatically. Return these headers on every response (including errors):

- `X-RateLimit-Limit`: The maximum requests allowed in the current window/bucket burst (e.g., 100).
- `X-RateLimit-Remaining`: Tokens remaining in the current bucket.
- `X-RateLimit-Reset`: Unix timestamp (or epoch seconds) when the bucket will be full again (or when the window resets).

**On a 429 response**, add:

- `Retry-After`: Seconds the client should wait before retrying. Use an integer seconds value (RFC 7231). Avoid floating point.
- A JSON body explaining the breach:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Client rate limit exceeded. Retry after 12 seconds.",
    "retry_after_seconds": 12,
    "scope": "client"  // or "tenant"
  }
}
```

**Critical distinction**: If the tenant-level cap tripped, set `scope: "tenant"` and include a message like: *"Your tenant's aggregate traffic exceeded the shared limit. Please review active integrations."* This prevents confusion when the client itself is well within its own limit.

---

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting without observability is blind trust. You need to know whether limits are protecting reliability or blocking legitimate users.

### Key Metrics
- **429 rate by scope**: `rate_limit_rejected{scope="client"}` vs `rate_limit_rejected{scope="tenant"}`. A high tenant-level 429 rate means a noisy tenant is starving its own integrations.
- **Token bucket fill level** (as percentile per client): If the median client is running at 5% of limit, your thresholds are too loose. If the 95th percentile is at 95%, you’re at risk of cascading failures.
- **Latency impact**: Compare p99 latency when limits are enforced vs. not enforced. If latency drops under heavy limit enforcement, the system was close to saturation.

### Logs
Log each rate limit check only when it *rejects* a request. Include:
- Tenant ID, client ID (anonymized if necessary)
- Scope (client vs. tenant)
- Current bucket fill level and limit
- Request path and method

**Important**: Do *not* log every allowed request. That’s noise. A sampling rate of 1% for allowed requests is enough to detect drift.

### Alerts
- *Any* tenant-level 429 in production? Page the on-call. This indicates a systemic problem where a single tenant is consuming capacity meant for others.
- *Client-level 429 rate > 5% of total traffic to a critical endpoint*? Investigate whether the limit is too low or a client has a bug (e.g., polling without backoff).
- *p99 latency increase > 20% when rate limits are actively rejecting traffic*? The limits might be masking a deeper capacity issue.

---

## Recommended Baseline Design

Start simple—you can always tighten later.

1. **Algorithm**: Token bucket per client with a burst of 2x the per-second rate. Tenant-level token bucket with a cap of 5x the highest client limit.

2. **Storage**: Redis for counters (token buckets) with TTL equal to the refill period. Use `INCR` and `EXPIRE` for simplicity; migrate to Lua scripts for atomicity when needed.

3. **Integration isolation**: Every unique API key gets its own bucket. Map API keys to client IDs via a fast cache (Redis or local).

4. **Headers**: Always return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. On 429, include `Retry-After` and a JSON body with `scope`.

5. **Observability**: Expose metrics on 429s by scope and endpoint. Alert on any tenant-level 429. Log only rejections with full context.

6. **Documentation**: Publish rate limit policies publicly so teams can design their integrations to respect limits before they hit them.

The goal is not to eliminate all bursts—it’s to contain them. A well-designed rate limiter should be invisible to well-behaved clients and a clear, actionable signal to misbehaving ones. Get the isolation right, and your multi-tenant API can scale from two-person startups to enterprise megacorps without constant firefighting.
````
