# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `default`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 21.484954
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2292, "completion_tokens": 2140, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2140
- Total tokens: 2292

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

```markdown
# Rate Limiting for Multi-Tenant APIs: Protecting Reliability Without Blocking Legitimate Use

Designing rate limiting for a multi-tenant API that serves both small teams and enterprise customers requires balancing protection against abuse with fairness across vastly different usage profiles. A small team might send 100 requests per minute during a CI/CD pipeline run, while an enterprise customer might sustain 50,000 requests per second across dozens of integrations. Getting this wrong means either allowing a single noisy tenant to degrade service for everyone, or frustrating legitimate users with arbitrary caps. This article covers the foundational concepts, algorithmic tradeoffs, tenant isolation strategies, client communication patterns, and observability practices needed to build a robust rate limiting system.

## 1. Authentication, Authorization, Quotas, and Rate Limits: Definitions Matter

These four concepts are frequently conflated, but they solve distinct problems:

- **Authentication** verifies *who* the client is (e.g., validating an API key or JWT). It answers: “Is this request coming from a known entity?”
- **Authorization** determines *what* that entity can do (e.g., read only vs. read-write, access to specific endpoints). It answers: “Is this request allowed for this identity?”
- **Quotas** define *how much* a tenant can consume over a long period (e.g., 1 million requests per month). Quotas are enforced asynchronously—you can exceed them temporarily, but you’ll be billed or blocked at month end.
- **Rate limits** control *how fast* a tenant can send requests (e.g., 100 requests per second). Rate limits are enforced synchronously—exceed them, and you get an immediate error.

For multi-tenant APIs, rate limits protect system reliability (CPU, database connections, external API dependencies), while quotas protect business boundaries (plan tiers, fair usage). A good design enforces both, but with different time windows and consequences.

## 2. Token Bucket, Fixed Window, and Sliding Window: Practical Tradeoffs

Three algorithms dominate production rate limiting. Here’s how they behave in practice:

### Fixed Window
Divide time into discrete windows (e.g., 1 second). Each tenant has a counter per window. At the start of each window, counters reset to zero.

- **Pro:** Simple to implement, low memory (one counter per tenant per window).
- **Con:** Burst allowance at window boundaries. If a tenant uses 100 requests at 0.999s and 100 requests at 1.001s, they effectively execute 200 requests in ~2ms. This can overwhelm downstream systems.
- **Best for:** Low-precision limits, internal tools, or when you accept brief bursts.

### Sliding Window
Track request timestamps in a window (e.g., last 60 seconds). Reject if count exceeds limit.

- **Pro:** Smooth enforcement, no boundary bursts.
- **Con:** Higher memory (store timestamps per tenant), more CPU to prune old entries. A logarithmic approximation (e.g., using a sorted set with TTL) reduces overhead.
- **Best for:** Most production APIs, especially when customers rely on precise limits (e.g., third-party integrations).

### Token Bucket
Maintain a bucket with a fixed number of tokens that refill at a constant rate. Each request consumes a token. If the bucket is empty, reject.

- **Pro:** Allows controlled bursts (up to bucket capacity) while smoothing long-term rate. Simple to reason about. No window boundary issues.
- **Con:** Requires a background refill process or lazy refill logic. Memory per tenant is constant (just current token count and last refill timestamp).
- **Best for:** APIs where bursty-but-constrained traffic is expected (e.g., CI/CD pipelines, webhook callbacks).

**Practical advice:** Start with a token bucket for per-second limits (allows short bursts) and a sliding window for per-minute/per-hour limits (smoother long-term enforcement). Never use fixed window alone—it creates too many support tickets.

## 3. Avoiding Punishment for One Noisy Integration

In a multi-tenant world, a single misconfigured or abusive integration (e.g., a customer’s bot that loops after a 429 error) must not degrade other tenants’ limits. Three isolation strategies work together:

- **Per-tenant buckets:** Every tenant gets its own token bucket or sliding window counter. This is non-negotiable. Never share a global pool.
- **Per-key subdivision within a tenant:** If a tenant has multiple API keys (e.g., one per environment or integration), treat each key as a separate limiter. This prevents a CI/CD pipeline from starving the tenant’s production key.
- **Burden pooling with soft caps:** For enterprise customers with many keys, aggregate their usage across keys into a tenant-level pool. If one key goes rogue, it hits its own key-level limit first. If multiple keys collectively exceed the tenant-level pool, all keys are throttled. This ensures fairness: a misbehaving integration affects only its own key, while the tenant-wide cap protects the system.

**Example design:** A tenant with 10 keys has a per-key limit of 100 req/s and a tenant-wide limit of 500 req/s. If key A sends 150 req/s, key A is blocked after 100. If every key sends 60 req/s (total 600), they all get blocked at 500—but they’re sharing the pain fairly.

## 4. Headers and Error Messages That Actually Help Clients

Clients need enough information to implement retry logic and adjust their sending rate. Return these headers on every response:

- `X-RateLimit-Limit`: The maximum allowed requests per window (e.g., 100).
- `X-RateLimit-Remaining`: How many requests remain in the current window.
- `X-RateLimit-Reset`: Unix timestamp when the current window resets or tokens refill.

On a rate limit violation (HTTP 429 Too Many Requests), additionally return:

- `Retry-After`: Seconds the client should wait before retrying (e.g., `2`). Use a precise integer; avoid fractions or decimals.
- A JSON body with: `{"error": "rate_limit_exceeded", "message": "API rate limit exceeded for key abc123. 50 requests allowed per second. Retry after 2 seconds.", "retry_after_seconds": 2, "type": "key"}`

Include the `type` field to indicate whether the limit was key-level (“key”) or tenant-level (“tenant”). This helps enterprise customers debug which of their integrations is causing the tenant-wide cap to fire. For authentication failures, use 401 (Unauthorized); for authorization failures, use 403 (Forbidden). Never confuse these with rate limits.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting only works if you know it’s working—and not overcorrecting. Collect these metrics system-wide and per tenant:

### Metrics
- **Requests allowed vs. blocked** per tenant, per key, per endpoint. Use histograms to track rate limit utilization (e.g., “90% of tenant requests use less than 50% of their limit”).
- **Retry-After values issued** per tenant. A sudden spike might indicate an integration bug, not a capacity issue.
- **Current bucket fill level** (for token bucket) or **window utilization** (for sliding window). If most tenants hover near 100% of their limit, you’re setting limits too low.
- **Error rate for 429 responses** as a fraction of total traffic. Alarm if >5% of traffic to any tenant returns 429—it suggests the limit is too tight or the client’s retry logic is broken.

### Logs
Log every 429 response with: tenant ID, key ID, endpoint, current limit, current usage, and the Retry-After value served. This is essential for debugging noisy neighbor incidents.

### Alerts
- **Tenant-level exhaustion:** If a tenant consistently hits 100% of their rate limit for >5 minutes, investigate—they may need an upgrade or have a stuck retry loop.
- **Global error rate:** If system-wide 429 rate exceeds a threshold (e.g., 1% of all API traffic), it may indicate capacity issues rather than tenant misbehavior.
- **Unusual utilization patterns:** If a tenant that normally uses 10% of its limit suddenly jumps to 80% with no plan change, it could be a compromised key or a new integration gone wild.

## Recommended Baseline Design

1. **Algorithm:** Token bucket for per-second limits (allows bursts); sliding window (approximate, using sorted sets with decay) for per-minute and per-hour limits. Run the token bucket in-memory (e.g., an atomic counter with a last-refill timestamp per key) and the sliding window in a Redis-like store if you have one; otherwise, keep everything in-memory with periodic persistence to avoid single points of failure.

2. **Isolation:** Per-key buckets + per-tenant aggregate bucket. Enforce key limit first; if passed, check tenant limit. Block with a 429 indicating which limit was hit.

3. **Limits:** For small teams, start with 100 req/s per key and 500 req/s per tenant. For enterprise customers, negotiate limits based on contracted throughput and store them in a configuration service.

4. **Client communication:** Return `X-RateLimit-*` headers and structured JSON errors. Use precise `Retry-After` values. Document that clients should retry with exponential backoff plus jitter.

5. **Observability:** Expose per-tenant and per-key metrics via a stats endpoint. Log all 429s with full context. Set alerts for sustained high utilization, sudden spikes, and global 429 rates above 1%.

Rate limiting is a system of constant tension between protection and availability. When designed with these principles, it becomes a silent safety net—rarely noticed, but essential when it works. When it fails, it’s the fastest way to generate a support ticket. Invest in the design now, and your future self—and your customers—will thank you.
```
