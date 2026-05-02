# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 18.424322
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2418, "completion_tokens": 2266, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2266
- Total tokens: 2418

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
# Rate Limiting for Multi-Tenant APIs: Balancing Fairness and Reliability Across Teams and Enterprises

## Introduction

Designing rate limiting for a multi-tenant API that serves both small teams (dozens of requests per minute) and enterprise customers (thousands of requests per second) is fundamentally a distributed fairness problem. The core challenge is not just capping usage, but ensuring that a bursty integration from one tenant does not degrade the experience for another, while also allowing legitimate scaling. This article clarifies the foundational concepts, evaluates practical algorithms, and provides a baseline design for backend engineers building such systems.

---

## 1. Authentication, Authorization, Quotas, and Rate Limits — The Four Layers

Engineers often conflate these four mechanisms. They serve distinct purposes and must be implemented as separate layers:

- **Authentication** verifies *who* the client is (e.g., via API keys, OAuth tokens). It answers: “Are you a known entity?”
- **Authorization** determines *what* that client is allowed to do (e.g., read vs. write scopes, endpoint access). It answers: “Are you allowed to perform this action?”
- **Quotas** enforce *cumulative* usage over a billing period (e.g., 10,000 requests per month). They are long-term, soft limits tied to contracts, often reset on a calendar basis. Exceeding a quota typically triggers an invoice or warning, not a rejection.
- **Rate limits** enforce *short-term* request frequency (e.g., 100 requests per second). They are hard limits meant to protect system stability. Exceeding a rate limit results in immediate HTTP 429.

In a multi-tenant API, rate limiting is the frontline defense. Quotas govern *capacity planning* and billing; rate limits govern *real-time system health*.

---

## 2. Token Bucket vs. Fixed Window vs. Sliding Window

### Fixed Window
The simplest algorithm: count requests in discrete time intervals (e.g., per second). At the start of each second, the counter resets.

**Practical problem**: Bursts at the boundary. If a tenant sends 100 requests in the last 10ms of second N, and 100 more in the first 10ms of second N+1, the system sees 200 requests in 20ms. This defeats the purpose of rate limiting. Fixed window is acceptable only for low-frequency, non-critical traffic.

### Sliding Window Log
Maintains a sorted log of timestamps per tenant. On each request, remove timestamps older than the window, then check if the count exceeds the limit.

**Practical problem**: Memory and compute cost. For a tenant issuing 10,000 requests per second, storing and scanning 10,000 timestamps per check is expensive. It is accurate but not scalable.

### Sliding Window Counter
A hybrid: track the count for the current and previous window, and compute a weighted estimate.

Example: For a 1-second window, store `current_count`, `previous_count`, and the timestamp when the current window started. If the window size is 1 second and the request arrives 0.3 seconds into the current window, the effective count is `previous_count * (1 - 0.3) + current_count`.

This is memory-efficient (two integers per tenant) and smooths boundary bursts without logs. It is the best practical trade-off for multi-tenant APIs with high throughput.

### Token Bucket
A bucket holds tokens (capacity). Tokens are added at a fixed rate (refill rate). Each request consumes a token. If the bucket is empty, the request is rejected.

**Practical problem**: Burst allowance. A bucket of 500 tokens with a refill of 100 per second allows a burst of 500 requests immediately, then throttles to 100/s. For enterprise tenants, this is desirable. For small teams, it can overload the system. Token bucket is excellent when you need to allow short bursts but control average rate. However, it is more complex to implement in distributed systems because token state must be synchronized across nodes (or you accept eventual consistency).

**Recommendation**: Sliding window counter for most cases. Token bucket for tenants that require burst capabilities (e.g., data sync jobs) — but only as a separate tier.

---

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

A common pitfall: applying a single global rate limit per tenant across all API keys, IPs, or integrations. One misconfigured script in a team’s CI pipeline can exhaust the tenant’s entire budget, blocking their production traffic.

**Solution**: Implement hierarchical or labeled buckets.

- **Per-API-Key limits** (also called "sub-limits"): Each API key or client credential has its own rate limit bucket, which is a fraction of the tenant’s global limit. If one key exhausts its sub-limit, only that key is blocked. The tenant can still operate via other keys.
- **Per-endpoint or per-resource limits**: Ensure expensive endpoints (e.g., `/search`, `/export`) have lower limits than lightweight ones (`/health`, `/status`). A noisy polling loop against an export endpoint should not block read-only GET requests.
- **Priority-based eviction**: Tag requests with a priority (e.g., `production` vs `staging`). Under load, reject low-priority requests first. This requires the client to set a priority header, which is validated on your side.

In practice: For each tenant, maintain a map of `{api_key: sliding_window_counter}`. The global tenant limit is enforced only if the sum of all key-level counters exceeds it. But rejection is always at the key level.

---

## 4. Headers and Error Messages

Clients need precise feedback to retry intelligently, not guess. Return the following headers on every response:

- `X-RateLimit-Limit`: The maximum number of requests allowed per window (e.g., `100`).
- `X-RateLimit-Remaining`: The number of requests remaining in the current window (e.g., `42`).
- `X-RateLimit-Reset`: Unix timestamp (or ISO 8601) when the current window resets. This allows clients to sleep until that time.

On rejection (HTTP 429 Too Many Requests):

- **Body**: JSON object with a clear, actionable message:
  ```json
  {
    "error": "rate_limit_exceeded",
    "message": "API key 'abc123' exceeded its rate limit of 100 requests per second. Retry after 2025-04-01T12:00:03Z.",
    "retry_after_seconds": 3
  }
  ```
- **Header**: `Retry-After: 3` (integer seconds). This is a standard HTTP header that clients and proxies (e.g., CDNs, load balancers) understand.

Do *not* return generic 5xx errors. A 429 is a contract violation by the client, not a server failure. Distinguishing this in logs is vital for alerting.

---

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting is only useful if you know it is working. Three layers:

### Metrics (counters and histograms, sampled at 1–10s intervals)
- `rate_limit.requests.total`: Total requests.
- `rate_limit.requests.accepted`: Accepted requests.
- `rate_limit.requests.rejected`: Rejected requests (by tenant, API key, endpoint).
- `rate_limit.bucket.capacity_usage`: Percentage usage per tenant (P50, P95, P99). A tenant consistently at 95%+ may need a limit increase.
- `rate_limit.effective_latency`: Time spent in rate limit checks. Should be <1ms; higher suggests algorithmic or caching issues.

### Logs (structured, sampled)
- Log every rejection with: `tenant_id`, `api_key`, `endpoint`, `current_rate`, `limit`, `reason` (e.g., "per-key limit exceeded"). Do *not* log every accepted request — it is too noisy. Use sampled logging for accepted requests (e.g., 1 in 1000).

### Alerts
- **p0**: `rate_limit.requests.rejected` spikes 5x above baseline for >5 minutes — potential DDoS or misconfigured client.
- **p1**: A single tenant’s rejection rate exceeds 10% of their total requests — their integration may be broken, or their limit is too low.
- **p2**: `rate_limit.effective_latency` exceeds 10ms P99 — likely a system bottleneck (e.g., Redis hot key, GC pause).
- **p0 (empty)**: `rate_limit.requests.rejected` drops to 0 for 24 hours — suggests rate limits are too high and not protecting the system. This is a silent failure.

---

## 6. Recommended Baseline Design

For a typical multi-tenant API with traffic from small teams (50 req/s) to enterprise (10,000 req/s):

1. **Algorithm**: Sliding window counter, implemented in-memory with a distributed cache (e.g., Redis as a shared counter store, not as a log). Use atomic increment with expiry. Accept eventual consistency across nodes (5–10ms stale is fine).

2. **Structure**: Three tiers per tenant:
   - **Global tenant limit**: Hard cap at contract level.
   - **Per-API-key limit**: 25% of global limit (so at least 4 keys can operate independently).
   - **Per-endpoint priority**: `/export` limited to 10% of per-key limit; `/status` limited to 100%.

3. **Default limits for new tenants** (starting small, no bad surprises):
   - 100 requests per second per API key.
   - 500 requests per second per tenant.
   - 10 requests per second for any endpoint with known high cost.

4. **Headers and errors**: As specified in Section 4. Always include `Retry-After`.

5. **Observability**:
   - Metrics per tenant (costly, but necessary; use bucketed tenant IDs to reduce cardinality).
   - Alert on rejection spikes and zero rejection.

6. **Override mechanism**: For enterprise customers, allow a one-time burst of 2x the limit for up to 60 seconds, triggered by a header (`X-RateLimit-Override: burst`). This is a deliberate, auditable escape hatch — not a default.

---

Rate limiting is often viewed as a necessary evil. Designed correctly, it becomes a transparent contract between your platform and its tenants — one that protects everyone’s reliability, from the lone developer’s side project to the enterprise’s mission-critical integration.
````
