# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `default`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 22.790538
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2420, "completion_tokens": 2268, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2268
- Total tokens: 2420

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

When you build a multi-tenant API that serves both small teams and enterprise customers, rate limiting becomes one of the most consequential infrastructure decisions you’ll make. Get it right, and your API remains stable under load from a thousand integrations while giving each tenant predictable access. Get it wrong, and you either block legitimate traffic or let a noisy neighbor degrade everyone’s experience. This article walks through the architectural considerations, practical algorithms, and observability patterns that enable you to design a rate-limiting system that works for tenants of any scale.

## Core Concepts: Authentication, Authorization, Quotas, and Rate Limits

Before designing the limit itself, you must understand how rate limiting differs from three related but distinct concepts:

**Authentication** verifies *who* the caller is. It answers “Are you who you claim to be?”—typically via API keys, OAuth tokens, or mutual TLS. Without authentication, you cannot even begin to apply per-tenant limits.

**Authorization** verifies *what* the caller is allowed to do. It answers “Can you perform this action on this resource?”—enforced through roles, scopes, or permissions. Authorization decides whether a request reaches your business logic at all.

**Quotas** define a hard upper bound on usage over a long period (daily, monthly). They answer “How many requests may this tenant make this month?” Quotas are enforced at billing boundaries; exceeding them typically triggers a 429 or a request to upgrade.

**Rate limits** govern the *rate* of traffic over short windows (seconds to minutes). They answer “How fast may this tenant send requests?” Rate limits protect system resources (CPU, database connections, external API calls) from short bursts that could overwhelm shared infrastructure.

In a typical pipeline, the sequence is: authenticate → authorize → check quota → check rate limit → process request. If you apply rate limits before authentication, you cannot distinguish tenants; if you apply quotas before rate limits, you may overcommit resources during a burst. Both are necessary, but they serve different protection roles.

## Algorithm Comparison: Token Bucket, Fixed Window, and Sliding Window

Three algorithms dominate production rate-limiting designs. Each has trade-offs in accuracy, memory overhead, and behavior under bursty traffic.

### Token Bucket

A token bucket maintains a fixed-size bucket that refills at a steady rate. Each request consumes one token. Bursts are allowed up to the bucket capacity, after which requests are queued or rejected.

- **Strengths:** Handles bursts gracefully. A small team that sends 50 requests in one second after an hour of inactivity can do so if its bucket holds 50 tokens. The refill rate then smooths subsequent traffic.
- **Weaknesses:** Requires careful configuration of bucket size and refill rate. If you over-provision the bucket, you defeat the purpose; under-provision it, and you reject legitimate bursts that are natural (e.g., cache warm-up).
- **Best for:** Tenants with variable traffic patterns, especially enterprise customers who may need periodic batch processing.

### Fixed Window

A fixed window divides time into discrete intervals (e.g., 100 requests per minute). At the start of each minute, the counter resets.

- **Strengths:** Simple to implement. Low memory per tenant (just a counter and a timestamp).
- **Weaknesses:** Vulnerable to “traffic spikes at window boundaries.” If a tenant sends 100 requests at 00:59 and another 100 at 01:01, the system sees 200 requests in two seconds—but technically within two different windows. This defeats the purpose of rate limiting.
- **Best for:** Simple APIs with low traffic variance, or when you can tolerate boundary spikes because you have excess capacity.

### Sliding Window

A sliding window tracks request timestamps within a rolling window (e.g., the last 60 seconds). Each new request removes expired timestamps.

- **Strengths:** Smoothest rate enforcement. No boundary spikes. A tenant sending 100 requests at timestamp T will be blocked for the next 60 seconds until at least one timestamp expires.
- **Weaknesses:** Higher memory cost (must store timestamps per tenant). Logically scalable with sorted sets or ring buffers, but requires more coordination in distributed systems.
- **Best for:** Strict enforcement where you cannot tolerate any boundary spikes. Often chosen for APIs that integrate with payment or real-time systems.

### Practical Recommendation

Start with token bucket for most multi-tenant APIs. It offers the best balance of burst tolerance and memory efficiency. Use sliding window only if you have hard latency or concurrency SLAs that cannot tolerate the boundary spike problem of fixed windows. Fixed window should be avoided unless your traffic is trivially low or you can afford to double the limit in the worst case.

## Avoiding Punishing an Entire Tenant for One Integration

This is the hardest problem in multi-tenant rate limiting. An enterprise tenant may have five separate internal services, each using a different API key, all consuming the same shared pool of resources. A buggy integration in one service—say a polling loop that spins out of control—should not block the other four services.

**Solution:** Use **nested rate limits with scoped keys**.

Design your rate limit structure as a hierarchy:

- **Global tenant pool:** 10,000 requests per minute for the tenant ID.
- **Per-key limits:** 2,000 requests per minute per API key (or per integration).
- **Per-endpoint limits (optional):** 500 requests per minute for a heavy endpoint like `/reports`.

When a noisy integration exceeds its per-key limit, you reject only that key. The tenant’s other integrations continue to operate normally, up to the global pool limit. This prevents one bad actor from starving the entire tenant.

Additionally, implement **differentiation by endpoint weight**. A `GET /users/list` is lightweight; a `POST /export/generate` is heavy. Assign a cost (e.g., 1 unit vs. 10 units) to each endpoint and decrement from the bucket accordingly. This ensures a tenant cannot DOS your system with expensive calls even within their limit.

## Headers and Error Messages

Clients need actionable information to respond appropriately to rate limiting. Standardize these response headers:

**429 Too Many Requests**
```
Retry-After: 45
X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1620000000
X-RateLimit-Scope: tenant
```

- `Retry-After`: seconds the client should wait before retrying (mandatory for sane client behavior).
- `X-RateLimit-Limit`: the cap for this scope.
- `X-RateLimit-Remaining`: remaining requests in the current window.
- `X-RateLimit-Reset`: Unix timestamp when the limit resets.
- `X-RateLimit-Scope`: indicates which limit was hit (e.g., `tenant`, `key`, `endpoint`).

**Body (JSON)**
```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the limit for this tenant. The limit is 10,000 requests per minute.",
  "scope": "tenant",
  "retry_after_seconds": 45
}
```

Do not return HTTP 200 with an error body. Clients that fast-fail on 429 will retry correctly; clients that parse 200 bodies may not. Use consistent error codes and always include retry timing.

## Observability: Metrics, Logs, and Alerts

Without observability, you cannot distinguish between “rate limits are working” and “rate limits are silently blocking legitimate users.”

### Metrics
- `rate_limit_hits_total{tenant, scope, status}` – Increment on each request. Tag with tenant ID, scope (tenant/key/endpoint), and whether it was allowed or blocked.
- `rate_limit_bucket_usage{tenant}` – Track how full each tenant’s bucket is over time. A consistently near-empty bucket means the limit is too low; a nearly full bucket means the tenant is always at risk.
- `rate_limit_throttling_duration_seconds{tenant}` – Average time between a blocked request and the next allowed request. High values indicate clients are not retrying correctly or limits are too tight.

### Logs
Log rate limit decisions with structured fields: `tenant_id`, `api_key`, `endpoint`, `limit_type`, `window_start`, `remaining`, `action` (allow/reject). Keep log volume manageable by sampling or logging only rejections and near-limit states. Do not log every allowed request unless debugging.

### Alerts
- **High rejection rate for a single tenant** (>5% of their requests rejected): Might indicate a noisy integration or that the tenant has legitimate need for a higher limit. Investigate.
- **Global rejection rate rising** without a corresponding traffic increase: Could be a configuration error or a distributed attack.
- **Bucket depth consistently above 80% for critical tenants**: They are living dangerously close to the edge. Proactively contact them to discuss upgrading.
- **No rejections at all** for any tenant: Your limits are too permissive, or your traffic is far below capacity. Either way, you are not testing your rate limiter and risk surprise outages during a traffic spike.

## Recommended Baseline Design

Here is a design that works for most teams building a multi-tenant API today:

1. **Identity:** Use API keys that are scoped to both a tenant and an integration (key ID). Authenticate before rate limiting.
2. **Primary algorithm:** Token bucket with a per-tenant capacity of 10,000 requests and a refill rate of ~167 requests/second (10,000 per minute). Store bucket state in a low-latency key-value store (Redis-style, not SQL).
3. **Secondary algorithm:** Per-key token bucket with capacity 2,000 per minute. Check after the tenant bucket.
4. **Exception handling:** When a per-key limit is exceeded, reject only that key. Return a payload including `scope: "key"`.
5. **Headers:** Always return `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `X-RateLimit-Scope`.
6. **Observability:** Export counters for allowed/rejected by tenant and key. Log rejections. Alert on per-tenant rejection rate >5%.
7. **Documentation:** Publish limit values, reset intervals, and header semantics. Provide clear guidance on handling 429s with exponential backoff and jitter.

This design protects small teams from their own bursts while giving enterprise tenants the runway they need—without letting one integration ruin the experience for everyone else.
````
