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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 13.283672
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2222, "completion_tokens": 2070, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2070
- Total tokens: 2222

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
# Throttling by Tenancy: Designing Rate Limits That Scale from Startup to Enterprise

## 1. Clearing the Fog: Auth, Authorization, Quotas, and Rate Limits

Before designing a rate limiter, we must agree on what we are *not* doing. These four concepts are frequently conflated, but each serves a distinct purpose.

- **Authentication** verifies *identity*: "Who is calling the API?" It answers with an API key, JWT, or mTLS certificate. Without it, nothing else matters.
- **Authorization** verifies *permission*: "Is this identity allowed to call this endpoint with these parameters?" It enforces roles and scopes (e.g., "read-only" vs. "admin").
- **Quotas** are *cumulative hard caps* over a billing cycle: "You may create 1,000 projects per month." Exceeding a quota usually returns a 403 Forbidden because the action is financially or operationally prohibited.
- **Rate Limits** are *time-based velocity controls*: "You may send 100 requests per second." They protect system resources from short-term bursts—not from long-term overuse. Exceeding a rate limit returns a 429 Too Many Requests, and the request is rejected but the quota is unaffected.

**Key insight for multi-tenancy:** Quotas are per-tenant contractual limits; rate limits are per-tenant *and per-key* safety valves. A small team may have a low quota but a generous rate limit; an enterprise may have a high quota but a stricter rate limit to ensure fair resource sharing.

## 2. Practical Algorithms: Token Bucket, Fixed Window, Sliding Window

### Fixed Window
Simplest: count requests in a wall-clock interval (e.g., 100 requests per minute, resetting at :00).
**Problem:** At the boundary, a client can send 100 requests at 0:59 and another 100 at 1:01—200 requests in two seconds. This violates the intended rate and punishes the system.
**Practical use:** Only acceptable for non-critical endpoints (e.g., status checks) where granularity does not matter.

### Sliding Window Log
Tracks timestamps of each request in a sorted set. The window moves continuously.
**Problem:** Storage grows with request volume. For a high-throughput tenant, maintaining a sorted set per key becomes expensive.
**Practical use:** Works for low-rate, auditable endpoints (e.g., password reset attempts).

### Sliding Window Counter (Hybrid)
Combines fixed window counters with a weighted overlap. Example: if the window is 1 second and you have 80 requests in the current window and 40 in the previous, the effective count at t+0.5s is `80 + 40 * 0.5 = 100`.
**Trade-off:** Almost as smooth as sliding log but O(1) memory per key.
**Practical use:** Best for most production APIs.

### Token Bucket
You have a bucket that fills at a steady rate (e.g., 10 tokens per second) up to a max burst capacity (e.g., 50 tokens). Each request consumes one token. If the bucket is empty, the request is denied.
**Strength:** Naturally handles bursts up to the bucket size, then enforces the average rate. Intuitive for developers.
**Weakness:** Stateful—requires atomic updates to the bucket counter and last refill timestamp.
**Practical use:** Ideal for multi-tenant APIs where tenants have different burst allowances.

**Recommendation:** Start with **token bucket** per API key, with a configurable burst capacity (e.g., 2× the sustained rate). It is the most forgiving for legitimate bursty workloads (e.g., a batch import) while still protecting the backend.

## 3. Avoiding Collateral Damage: One Noisy Integration

A single aggressive integration in a shared tenant can starve all other keys under that tenant. Solutions:

- **Per-key limits, not per-tenant limits.** Each API key gets its own bucket. This is the minimum requirement.
- **Hierarchical rate limiting.** Maintain two buckets: a *per-key* bucket and a *per-tenant* parent bucket. A request passes only if both buckets have tokens. The parent bucket limits the *sum* across all keys. This prevents a tenant with 100 keys from amplifying abuse.
- **Cost-aware weighting.** Not all endpoints are equal. A `GET /users` might cost 1 token; a `POST /batch` might cost 10. Weight the token consumption by endpoint resource cost.
- **Concurrency limits as a safety net.** Rate limits are for request velocity; concurrency limits (max in-flight requests) protect against slow clients. Use a separate semaphore per tenant (e.g., max 50 concurrent requests per tenant). If a client holds connections open, concurrency limits kick in before rate limits.

**Real-world pattern:** On a request, check concurrency limit first (quick rejection if too many in-flight), then check per-key token bucket, then check per-tenant parent bucket. This ensures one noisy integration only exhausts its own key—not the entire tenant.

## 4. Headers and Error Messages: What Clients Need

Clients should never have to guess why they were rejected. Return consistent, machine-parseable headers and error bodies.

### Response Headers (on every request, not just throttled ones)
- `X-RateLimit-Limit`: The maximum requests per window (e.g., `100`). Tells developers their configuration.
- `X-RateLimit-Remaining`: Tokens remaining in the current bucket (e.g., `42`). Proactive signal.
- `X-RateLimit-Reset`: Unix timestamp when the bucket will refill enough tokens for a new request (e.g., `1712345678`). Allows precise backoff.

### 429 Response
```json
{
  "error": {
    "type": "rate_limit_exceeded",
    "message": "Too many requests. Retry after 5 seconds.",
    "retry_after_seconds": 5
  }
}
```
- Include a `Retry-After` header (in seconds) so HTTP clients can use standard retry logic.
- For per-tenant limits (parent bucket hit), return a distinct error type: `"tenant_rate_limit_exceeded"`. This tells clients that the whole tenant is blocked, not just their key, which is crucial debugging info.

## 5. Observability: Are Limits Protecting or Punishing?

Rate limiting is a control loop. Without observability, you cannot tune it.

### Metrics (cardinality-aware)
- **Per-key counters:** Requests allowed, requests throttled. This is high cardinality but essential for debugging.
- **Per-endpoint counters:** Requests throttled by endpoint. Helps identify if a specific endpoint is systematically over-limit.
- **Per-tenant counters (aggregated):** Total throttled across all keys. Alerts on sharp increases.
- **Latency of rate limit check:** A slow rate limiter becomes a performance bottleneck. Track p99 duration of the rate limit decision (should be <1ms in-memory).
- **Concurrency limit utilization:** How many concurrent requests per tenant. If it is always near the ceiling, the rate limit is too generous.

### Logs
- **Every throttle event** should log: `tenant_id`, `api_key_id`, `endpoint`, `retry_after`, and `reason` (per-key vs. per-tenant limit hit). Do not log successful requests except at debug level.
- **Periodic snapshots** (every minute) of bucket fullness for top-N tenants. Helps detect slow leaks.

### Alerts
- **Spike in throttled requests overall:** Could indicate a misconfigured client or a DDoS.
- **Single tenant consuming >90% of its rate limit for >5 minutes:** Could be a noisy integration. Investigate before it causes collateral damage.
- **Concurrency limit being hit frequently:** Indicates a slow endpoint or a client that does not close connections. This is often more dangerous than rate limit violations.
- **Rate limit check latency exceeds 5ms:** The rate limiter itself is under stress—maybe the data store is congested.

## Recommended Baseline Design

1. **Algorithm:** Token bucket per API key, with a parent token bucket per tenant. Use an in-memory store (e.g., a sharded hash map with atomic updates) for sub-millisecond checks. Persist bucket states to a distributed cache for crash recovery, but do not read from cache on the hot path—write asynchronously.
2. **Burst allowance:** Set burst capacity to 2× the sustained rate for all tiers. Enterprises pay for higher sustained rates; small teams get a reasonable burst for their scale.
3. **Limit configuration:** Store limits in a config service, keyed by tier (`tier:small`, `tier:enterprise`) and optionally per-tenant overrides. Reload config every 60 seconds without restart.
4. **Concurrency limit:** Separate per-tenant semaphore, max 50 concurrent requests. This is a hard stop before rate limits.
5. **Headers and errors:** Always return `X-RateLimit-*` headers and a structured JSON error with `retry_after_seconds`. Use distinct error types for key vs. tenant limits.
6. **Observability:** Export metrics with tenant and endpoint labels (but not individual key labels to avoid explosion). Log every throttle event. Alert on sustained high throttle rates or unexpected latency in the limiter itself.

A multi-tenant API rate limiter is not just a burst protector—it is a fairness enforcer. Design it to be visible, debuggable, and configurable per tenant, and your small teams and enterprise customers will trust your platform even under load.
````
