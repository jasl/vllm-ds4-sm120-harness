# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 14.577876
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2199, "completion_tokens": 2047, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2047
- Total tokens: 2199

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
# Rate Limiting in a Multi-Tenant API: Balancing Fairness and Reliability for Teams and Enterprises

## The Four Pillars of Access Control

Before designing rate limits, we must distinguish four concepts that are often conflated:

- **Authentication** verifies *who* you are (e.g., API key, OAuth token). It answers "Are you a known client?"
- **Authorization** determines *what you can do* (e.g., read vs. write scopes, endpoint permissions). It answers "Are you allowed to perform this action?"
- **Quotas** define *how much you are allowed over a long period* (e.g., 100,000 requests per month). Quotas are billing-related, enforced after the fact or via soft warnings.
- **Rate limits** control *how fast you can make requests* (e.g., 100 requests per second). Rate limits protect real-time system stability and are enforced synchronously.

For a multi-tenant API, rate limits must coexist with per-tenant quotas. A small team with a 10,000 request/month quota might burst at 100 requests/sec, while an enterprise with 10 million requests/month might need a higher burst ceiling. The rate limit should be a function of both the tenant tier and the current system load.

## Algorithm Comparison: Token Bucket, Fixed Window, and Sliding Window

### Token Bucket
A conceptual bucket holds tokens that refill at a steady rate (e.g., 10 tokens per second). Each request consumes one token. If the bucket is empty, the request is denied. A maximum bucket size (burst capacity) allows short traffic spikes.

**Practical behavior:** Predictable, handles bursts naturally, no "starvation." Ideal for APIs where traffic is bursty but bounded. The downside: requires memory per tenant (bucket state) and careful tuning of refill rate vs. burst.

### Fixed Window
Divide time into fixed intervals (e.g., 1 second). Count requests in the current window. If the count exceeds the limit, reject until the next window.

**Practical behavior:** Simple to implement, but suffers from "boundary effect" — a burst at the end of one window and the start of the next can double the allowed rate. For example, 100 requests/sec limit could actually handle 200 requests in a 0.1-second span crossing a window boundary. This defeats the purpose of rate limiting.

### Sliding Window (Log or Counter)
Maintain a sliding time window, either by storing timestamps of recent requests (log) or by using a decaying counter. The log approach is exact but memory-intensive for high-throughput tenants. The counter approach (e.g., using a sorted set or sliding window counter) approximates the sliding window with lower cost.

**Practical behavior:** Smooths out boundary effects. More complex to implement, but essential for APIs where precise enforcement matters. For multi-tenant systems, sliding window with a counter per tenant is the most common production choice.

**Recommendation for multi-tenant:** Use sliding window with a token bucket variant. The token bucket naturally handles bursts, and sliding window ensures fairness across clock boundaries. For tenants with very high throughput, switch to a sliding window counter to reduce memory overhead.

## Avoiding Tenant Punishment from a Single Noisy Integration

A classic problem: one integration (e.g., a misconfigured webhook retry loop) consumes the entire tenant's rate limit, starving other legitimate integrations under the same tenant. Solutions:

1. **Per-integration rate limits within a tenant.** Each API key or sub-account should have its own bucket, capped by a tenant-level aggregate limit. If integration A exhausts its sub-bucket, it is denied while integration B continues.

2. **Priority queuing.** Label requests by criticality (e.g., user-facing vs. background sync). High-priority requests can borrow from a shared reserve. This prevents a slow background job from blocking a user's real-time action.

3. **Excess traffic isolation.** If a single integration consistently exceeds its share, redirect its requests to a separate "noisy neighbor" pool with stricter limits or a slower fallback path. This containment ensures the tenant's primary throughput remains unaffected.

4. **Graceful degradation at tenant level.** Instead of a hard 429, allow the tenant to exceed its limit by a small margin (e.g., 10%) with increased latency. This gives time for monitoring and alerting before a full block. Enterprise tenants often prefer this predictable slowdown over sudden rejection.

## Headers and Error Messages for API Clients

Transparency is critical. Every response should include:

**On every API response:**
- `X-RateLimit-Limit`: The maximum requests allowed per window (e.g., `100`).
- `X-RateLimit-Remaining`: The number of requests left in the current window (e.g., `42`).
- `X-RateLimit-Reset`: Unix timestamp when the window resets (or seconds until reset). Use UTC.

**On rate-limited (429) responses:**
- `Retry-After`: Seconds the client should wait before retrying (not seconds until reset, but a safe delay).
- Response body (JSON):
  ```json
  {
    "error": "rate_limit_exceeded",
    "message": "You have exceeded the rate limit for this API key. Please retry after the specified delay.",
    "retry_after_seconds": 5,
    "global_limit": false,
    "tenant_scope": "integration_key: abc123"
  }
  ```
- Include a `X-RateLimit-Scope` header indicating whether the limit is per-integration, per-tenant, or global. This helps clients debug which limit was hit.

**Important:** Never expose internal limits (e.g., server capacity) in headers. Only expose the tenant's contractual rate limit. If the system is under global strain, return a 503 (Service Unavailable) with its own headers, not a rate limit error.

## Observability: Metrics, Logs, and Alerts

Rate limiting should not be a black box. You need visibility into whether it's protecting reliability without blocking legitimate traffic.

### Metrics (every 10–30 seconds)
- `rate_limit.requests_total` by status (allowed, rejected, throttled).
- `rate_limit.rejected_per_tenant` — top 10 tenants by rejection count.
- `rate_limit.current_utilization` — as a percentage of limit per tenant (e.g., 80% full).
- `rate_limit.burst_buffer_remaining` — for token bucket, average remaining tokens across high-traffic tenants.
- `rate_limit.latency_impact` — p50/p99 latency for allowed requests vs. rejected request handling.

### Logs (sampled or structured)
- Every rate limit rejection should log: tenant ID, integration key, endpoint, IP (anonymized), reason ("global limit", "per-key limit", "noisy neighbor isolation"), and `Retry-After` value.
- Avoid logging every allowed request — sample at 0.1% or use structured metrics instead.

### Alerts
- **P0 (Immediate):** More than 5% of all API requests are rejected. Indicates systemic misconfiguration or DDoS.
- **P1 (High):** A single enterprise tenant sees >20% rejection rate for >5 minutes. Investigate noisy integration or limit mis-tuning.
- **P2 (Medium):** Any tenant consistently operating at >90% utilization. Proactive outreach or auto-increase for enterprise contracts.
- **P3 (Info):** Unusual pattern: a previously quiet tenant suddenly spikes to 100% of limit. Could be a legitimate campaign or a retry storm.

**Crucial metric:** Compare rejection rate to error rate (5xx). If rejection is high but 5xx is low, rate limits are working. If both are high, your backend has a bottleneck that rate limits are masking — you need capacity planning, not tighter limits.

## Recommended Baseline Design

For a multi-tenant API serving both small teams and enterprises:

1. **Algorithm:** Sliding window with token bucket per integration key. Each tenant has a master token bucket that enforces the aggregate limit. Inside the tenant, each API key gets a sub-bucket sized proportionally to its historical usage (with a minimum floor).

2. **Tiered limits:** Small teams: 10 req/s, burst of 50. Enterprise: 500 req/s, burst of 2000. Expose a flexible "overage" option where enterprises can exceed the burst by 10% at higher latency.

3. **Isolation:** Per-integration enforcement, with a tenant-level cap. If an integration exceeds its share, it gets a separate token bucket with 50% lower refill rate — not a hard block — to avoid sudden cutoffs.

4. **Headers:** Always return `X-RateLimit-*` headers. On 429, include `Retry-After` (computed as 2x the average response time for that tenant, capped at 60 seconds). Return 503 for global capacity limits, not 429.

5. **Observability pipeline:** Every 10 seconds, emit per-tenant utilization metrics to a time-series database. Log every 429 with tenant ID and integration key. Alert on >5% global rejection or >20% enterprise rejection.

6. **Grace period for small teams:** New tenants get a 48-hour "learning" phase with relaxed limits (2x normal). This prevents misconfiguration during onboarding from triggering alarms.

This design ensures that one team's misbehaving integration does not bring down the entire API, while enterprises enjoy predictable, high-throughput access with transparent feedback. The key is to rate-limit at the finest granularity possible (integration key) while keeping tenant-level visibility and control.
````
