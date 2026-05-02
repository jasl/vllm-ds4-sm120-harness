# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.026353
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2055, "completion_tokens": 1903, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 1903
- Total tokens: 2055

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
# Rate Limiting for Multi-Tenant APIs: Balancing Team Agility and Enterprise Reliability

## 1. Authentication, Authorization, Quotas, and Rate Limits: Clear the Confusion

Before designing rate limiting, you must understand how it differs from adjacent concepts:

- **Authentication** verifies *who* a client is (e.g., API key, OAuth token). It is a gate: pass or fail.
- **Authorization** determines *what* a client is allowed to do (e.g., read vs. write, tenant-scoped resources).
- **Quotas** enforce *cumulative* usage over a long period (e.g., 10,000 API calls per month). Quotas are about *capacity planning and billing*—they allow bursts within the period and only block when the cumulative cap is exhausted.
- **Rate limits** enforce *instantaneous* request velocity (e.g., 100 requests per second). Rate limits protect system stability, not budget. They smooth traffic spikes and prevent one tenant from degrading others.

A common anti-pattern is conflating quotas with rate limits. A small team may burst 500 requests in two seconds, then stay quiet for an hour. A rate limit that drops that burst would block legitimate usage *that is well within their quota*. Rate limits must be tuned for concurrency and velocity, not cumulative volume.

## 2. Algorithm Choices: Token Bucket, Fixed Window, Sliding Window

Each has trade-offs in multi-tenant environments.

**Token Bucket** (bucket with capacity `B` tokens, refill rate `R` per second) allows short bursts up to `B`, while enforcing sustained rate `R`. Practical strengths:
- Burst-friendliness: small teams can spike without hitting a hard ceiling.
- Simple to implement locally per tenant (in-memory or Redis).
- Weakness: In a multi-tenant system, a single tenant with a small bucket can still flood if `B` is too large relative to global capacity. You must size `B` per tenant tier.

**Fixed Window** (e.g., count requests in each clock second) is simple but has the “edge problem”: if a tenant sends 90 requests at the end of second 1 and 90 at the start of second 2, the system sees 180 requests in a near-instant, bypassing a 100 req/s limit. For small teams that might spike across window boundaries, this is dangerous.

**Sliding Window** (e.g., sliding log or sliding window counter using sorted sets) eliminates the edge problem by evaluating a rolling time window. It is fairer for bursty work patterns. Practical concern: storage and computational cost. For thousands of tenants, storing a sorted set per tenant can be expensive. A practical hybrid: use a **sliding window counter** (track counts for the current and previous minute, weighted by overlap) to approximate sliding window behavior with O(1) memory per tenant.

**Recommendation**: Use token bucket for small teams (bursts are expected) and sliding window for enterprise tenants where traffic patterns are steadier and fairness matters. This avoids applying the same algorithm to vastly different usage profiles.

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

A common design mistake: a single rate limit *for the entire tenant*. If one integration (e.g., a misconfigured webhook) saturates the tenant’s limit, all other integrations—or even human users—get blocked.

**Solutions:**

- **Per-integration rate limits**: Each API key or client ID (often mapping to a specific integration) gets its own limit, *in addition to* a tenant-wide aggregate limit. The integration limit acts as a circuit breaker for noise, while the tenant limit protects the backend from total tenant traffic. A noisy webhook hits its own limit first, leaving other integrations untouched.

- **Hierarchical buckets**: A parent bucket (tenant) and child buckets (integration keys). When a child bucket is empty, that integration is blocked, but the parent bucket still allows requests from other children. Implement with a token bucket per integration, decrementing the parent bucket only when the child has tokens. This prevents one noisy caller from draining the tenant’s shared tokens.

- **Traffic shaping for misbehaving clients**: Instead of blocking outright, delay excess requests (e.g., return 429 with a Retry-After header). For a noisy integration, apply progressive delays or downgrade its priority—still allows its legitimate bursts but softens impact.

- **Alerting on per-integration violations** to detect a misconfigured client before it affects others.

## 4. Headers and Error Messages for API Clients

Clients need actionable information to self-regulate. Return these in every response:

| Header | Purpose |
|--------|---------|
| `X-RateLimit-Limit` | The maximum requests allowed in the current window (per tenant or integration). |
| `X-RateLimit-Remaining` | How many requests remain in the current window. |
| `X-RateLimit-Reset` | Unix timestamp when the window resets (or when the bucket refills the next token). |
| `Retry-After` | Seconds the client should wait before retrying (on 429 responses). |

**Error body for 429** (JSON):
```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the request rate limit. Please retry after the Retry-After period.",
  "rate_limit_per_integration": 50,
  "rate_limit_per_tenant": 500,
  "window_size_seconds": 60
}
```

Use a machine-readable `error` field (not just a message) so clients can programmatically decide to retry or degrade. Include both per-integration and per-tenant limits so debugging is transparent.

## 5. Observability: Metrics, Logs, and Alerts

You cannot tune rate limits without seeing their real-world impact.

**Metrics (aggregated per tenant, per integration, per endpoint):**
- `rate_limit_requests_total` — total requests.
- `rate_limit_throttled_total` — requests that were blocked (by integration and tenant).
- `rate_limit_bucket_usage` — current fill percentage of token buckets (to see if limits are too tight or too loose).
- `rate_limit_queue_length` — if you use queuing, how many requests are waiting? (Alert if backlog grows.)
- `latency_p99` — if rate limiting is in front of a database, measure if throttling reduces p99 latency for other tenants.

**Logs:**
- Log every rate limit violation with tenant ID, integration ID, endpoint, and their current bucket state. This helps diagnose which integration is noisy and why.
- Log bucket refill events only at debug level to avoid noise.

**Alerts (three distinct signals):**
1. **Tenant approaching limit** (e.g., remaining <10% of window). This is *not* an incident; it’s early warning for the tenant. Consider sending a webhook to their slack.
2. **Tenant hitting limit repeatedly** (e.g., >10% of its requests are throttled over 5 minutes). This indicates either a misconfigured client or a limit too tight. Alert the platform team.
3. **Global throttling rate exceeds a threshold** (e.g., >10% of total API requests are being throttled). This signals that either a DDoS-like event is happening or that default limits are grossly misconfigured. Alert immediately.

**Key principle**: If your alerts never fire, you are either not observing or your limits are too permissive. If alerts fire constantly, limits are too aggressive and you are blocking legitimate usage. Tune until the alert rate is a genuine signal of misbehavior, not background noise.

## Recommended Baseline Design

For a multi-tenant API serving small teams and enterprise customers:

1. **Three-tier rate limits**:
   - **Per integration** (API key): token bucket, capacity 100 tokens, refill 10 tokens/s.
   - **Per tenant**: sliding window counter, 1000 requests per 60 seconds.
   - **Per endpoint** (global): sliding window, e.g., `/search` gets 500 req/s across all tenants. This protects a specific backend from being overloaded regardless of tenant behavior.

2. **Hierarchical enforcement**: Check integration bucket first; if satisfied, decrement tenant bucket. If tenant bucket has tokens, route to backend. If not, 429.

3. **Hard per-endpoint limits** to protect backend resources (e.g., database connections, compute) from any combination of tenants.

4. **Return headers and structured errors** as described, with per-integration information.

5. **Observe per-integration metrics** separately from per-tenant metrics. Alert on per-integration throttling > 5% of that integration’s requests.

This design gives small teams room to burst while enterprise customers get predictable, steady limits; prevents a single noisy integration from starving its tenant; and gives you observability to tune without overreacting.
````
