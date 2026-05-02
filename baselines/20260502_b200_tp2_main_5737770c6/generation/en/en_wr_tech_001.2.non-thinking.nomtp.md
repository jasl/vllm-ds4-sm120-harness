# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 35.884575
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2309, "completion_tokens": 2157, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2157
- Total tokens: 2309

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
# Designing Rate Limits That Don't Break Your Multi-Tenant API

A single noisy integration can degrade an entire tenant's experience—or worse, spill over and affect other tenants sharing your API infrastructure. For backend engineers building multi-tenant APIs that serve both small teams and enterprise customers, rate limiting is not just about throttling requests; it's about preserving fairness, reliability, and predictability across vastly different usage patterns.

This article walks through the core concepts, algorithmic trade-offs, and practical design principles for a rate-limiting system that protects your infrastructure without punishing tenants for a single misbehaving client.

## 1. Authentication, Authorization, Quotas, and Rate Limits—They Are Not Synonyms

Before designing rate limits, you must understand what they are *not*.

- **Authentication** answers: *Who is this?* It verifies identity via API keys, OAuth tokens, or mTLS certificates. Without authentication, you cannot map a request to a tenant.
- **Authorization** answers: *What is this allowed to do?* It enforces permissions (e.g., read-only vs. write access, scoped resources). A tenant may be authenticated but not authorized for a specific endpoint.
- **Quotas** are *absolute, non-resetting limits* over a long period (e.g., 100,000 API calls per month). They define what a tenant has purchased or been allocated. Exceeding a quota typically returns a 403 or 429 and often requires a plan upgrade or manual reset.
- **Rate limits** are *short-term, rolling limits* (e.g., 100 requests per minute) designed to protect system stability. They prevent a tenant from overwhelming the API in a burst, even if they haven't hit their monthly quota.

Key insight: quotas govern *how much* over time; rate limits govern *how fast* right now. Failing to distinguish them leads to confusing error messages and unpredictable retry behavior.

## 2. Algorithm Choices: Token Bucket, Fixed Window, Sliding Window

Three algorithms dominate practical rate-limiting implementations. Each has trade-offs you must evaluate for your tenant mix.

### Token Bucket
- **How it works**: A bucket holds a fixed number of tokens (capacity). Tokens are added at a constant rate (refill rate). Each request consumes one token. If the bucket is empty, the request is denied.
- **Pros**: Handles bursts naturally—unused tokens accumulate up to capacity. Smooths traffic over time. Easy to implement.
- **Cons**: Requires careful choice of capacity and refill rate. Too large a capacity allows bursts that may still overwhelm downstream dependencies.
- **Best for**: Enterprise customers with predictable, high-volume workloads who need occasional bursts for batch operations.

### Fixed Window
- **How it works**: Time is divided into fixed intervals (e.g., 1 minute). A counter per tenant resets at the start of each interval. If the counter exceeds the limit, requests are denied until the next window.
- **Pros**: Extremely simple, low memory and CPU overhead.
- **Cons**: "Traffic cliff" at window boundaries—a tenant can send two windows' worth of requests in a single second if they time the reset perfectly. This punishes shared infrastructure and other tenants.
- **Best for**: Internal tools or low-stakes APIs where spikes are acceptable.

### Sliding Window (Log or Log-Counter Hybrid)
- **How it works**: Tracks request timestamps within a rolling time window (e.g., last 60 seconds). A request is allowed if the count of timestamps in the window is below the limit. Variants use a sorted set for precision or a counter with a sliding approximation.
- **Pros**: Eliminates the boundary spike problem. More accurate for burst detection.
- **Cons**: Higher memory usage (storing timestamps for every request per tenant) or complexity for the hybrid approach.
- **Best for**: Multi-tenant SaaS APIs where fairness across tenants is critical, and bursts must be controlled without ambiguity.

**Practical recommendation**: Start with Token Bucket per tenant for most workloads, but evaluate Sliding Window if you observe burst-related incidents at window boundaries.

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

A single misconfigured script, webhook flood, or polling loop in one of a tenant's services should not degrade the experience for their other, well-behaved integrations—nor should it consume capacity allocated to the tenant's enterprise customers.

### Per-Integration (Sub-Tenant) Rate Limits
Treat each API key or client scope as a separate rate-limited identity, while still enforcing an overall tenant cap. For example:
- Integration A: 50 req/min
- Integration B: 50 req/min
- Tenant overall: 100 req/min

This prevents one noisy client from exhausting the tenant's shared budget. Implementation requires a two-tier bucket: one for the integration (key-level), one for the tenant (account-level). A request must pass *both* to proceed.

### Priority Queuing and Concurrency Limits
Rate limits are about *count* of requests over time. Concurrency limits control *how many requests are in-flight at once*. For enterprise tenants with many parallel integrations, a concurrency limit (e.g., 10 simultaneous requests per tenant) prevents a single long-running batch from blocking others. Combine this with weighted fair queuing to ensure low-priority bulk operations don't starve interactive API calls.

### Warning Headers Before Blocking
Return a `X-RateLimit-Warning` header when a client reaches 80% of its limit. This gives the noisy integration time to back off before the tenant's entire budget is consumed. The warning is per-integration, not per-tenant, so the tenant operator can identify the offending client.

## 4. Headers and Error Messages Clients Need

Clients—both small teams and enterprise integrators—must be able to build resilient retry logic. Your API must provide consistent, machine-readable feedback.

### Standard Headers (per response)
- `X-RateLimit-Limit`: The maximum number of requests allowed in the current window (e.g., 100).
- `X-RateLimit-Remaining`: How many requests remain in the current window.
- `X-RateLimit-Reset`: Unix timestamp (or ISO 8601) when the window resets or when the bucket will have a new token.
- `Retry-After`: Seconds (or a HTTP-date) the client should wait before retrying. **Always include this on 429 responses.**

### Error Response Body (429 Too Many Requests)
```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit for this API key. Retry after 30 seconds.",
  "retry_after_seconds": 30,
  "limit": 100,
  "remaining": 0
}
```

### Differentiate Between Rate Limits and Quotas
- 429: rate limit exceeded (you can retry after a short wait).
- 403: quota exhausted or authorization failure (you need to upgrade or contact support).

Never return a 429 for quota exhaustion—clients will retry indefinitely and waste resources.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting only protects reliability if you know it's working—and not blocking legitimate traffic.

### Key Metrics (per tenant, per integration, globally)
- **Requests throttled**: Count of 429 responses, broken down by tenant tier (small team vs. enterprise).
- **Requests allowed vs. limit**: How close tenants are running to their limits, as a percentile distribution (p50, p95, p99).
- **Burst depth**: For token bucket, the average and max tokens consumed from the bucket. High average indicates sustained near-limit usage; max near capacity indicates bursty behavior.
- **Concurrency**: Number of in-flight requests per tenant. Spikes here signal potential queue build-up.

### Logs
Log every rate-limit decision (allow or deny) with:
- Tenant ID and integration ID
- Rate limit algorithm parameters (limit, remaining, window start)
- Downstream service latency (to correlate throttling decisions with backend health)

**Crucially**, do *not* log the full request body for denied requests—that's a security risk. Log the URI, method, and headers.

### Alerts
- **Global throttle rate > X%**: If more than, say, 5% of all requests result in 429s, your limits may be too aggressive or your capacity is saturated.
- **Enterprise tenant hitting rate limit > Y times in an hour**: A legitimate enterprise pattern (data export) may need a higher limit or a different algorithm.
- **Single integration consuming > 80% of tenant bucket for Z minutes**: Detect noisy neighbors before they disrupt other integrations.

## Recommended Baseline Design

For a multi-tenant API serving teams of 5 and Fortune 500 companies:

1. **Authentication**: API keys per integration, scoped to a tenant account.
2. **Two-tier Token Bucket per integration**: A small bucket (capacity = 50 tokens, refill = 50 tokens/min) for each API key, plus a larger tenant-wide bucket (capacity = 500 tokens, refill = 100 tokens/min). A request consumes tokens from both—deny if either is empty.
3. **Concurrency limit per tenant**: 20 simultaneous requests. Implement using a semaphore at the ingress layer.
4. **Headers**: Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After` on every response.
5. **Observability**: Log and metric every rate-limit decision. Alert when global throttle rate exceeds 5% or an enterprise tenant exceeds its limit more than 10 times in an hour.
6. **Quota enforcement**: Separate from rate limits. Check monthly quota asynchronously after a request completes, returning 403 if exceeded. Never retry.

This baseline allows small teams to burst within their single key's limit, while enterprise tenants can scale across many integrations without one noisy client starving the rest.

---

Rate limiting is a first-class feature of your API, not an afterthought. Design it with clarity, fairness, and observability from day one—your infrastructure (and your customers) will thank you.
````
