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
- Elapsed seconds: 10.300353
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2361, "completion_tokens": 2209, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2209
- Total tokens: 2361

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
# Designing Rate Limiting for Multi-Tenant APIs Serving Small Teams and Enterprise Customers

## 1. Foundational Concepts: Authentication vs. Authorization vs. Quotas vs. Rate Limits

Before designing any throttling mechanism, you must be precise about what each concept controls:

- **Authentication** verifies *who* the caller is (e.g., API key validation, OAuth token expiry). It is a binary pass/fail gate: “Is this request from a known identity?”

- **Authorization** determines *what* the caller is allowed to do (e.g., read vs. write, access to specific resources). It defines scope, not frequency.

- **Quotas** enforce *long-term usage budgets* over billing cycles (e.g., 10,000 requests per month, 1 TB of egress per day). They protect your business model and prevent runaway consumption across hours or days.

- **Rate limits** control *short-term request velocity* (e.g., 100 requests per second per tenant). They protect system stability—CPU, database connections, external API calls—from sudden bursts that could degrade service for other tenants.

Key insight: rate limits are not quotas. A tenant may have quota remaining but still be rate-limited if they spike. Conversely, a tenant below their rate limit may still exhaust their monthly quota.

## 2. Algorithm Choices: Token Bucket, Fixed Window, Sliding Window

### Fixed Window

The simplest model: count requests in discrete intervals (e.g., per minute). If the counter exceeds the limit, reject new requests until the next window.

**Practical problem with multi-tenant:** Burstiness at window boundaries. If all tenants align their activity to the top of the minute, the system sees sudden load spikes. Worse, a single tenant can time their 100 allowed requests at the very end of one window and the very start of the next, effectively sending 200 requests in near-zero time. This defeats the purpose of rate limiting for reliability.

### Sliding Window Log

Maintain a timestamped log of recent request times (e.g., in Redis sorted sets). Count all timestamps within the last N seconds.

**Practical problem with multi-tenant:** Memory and compute overhead. For a high-throughput API, maintaining an ordered set per tenant per endpoint can become expensive. You also risk clock skew issues in distributed deployments.

### Token Bucket

A bucket holds tokens, refilled at a fixed rate (e.g., 10 tokens per second). Each request consumes one token. If the bucket is empty, the request is deferred or rejected.

**Why it wins for multi-tenant:** It naturally absorbs short bursts up to the bucket capacity while enforcing a long-term average rate. A tenant can accumulate tokens during idle periods, then send a moderate burst—without overloading the system. Crucially, the refill rate is constant, so no single tenant can line up requests across arbitrary window edges. Implementation is lightweight (a counter and a timestamp per tenant).

**Recommended default:** Token bucket with capacity equal to (refill_rate * 2) to allow bursts of twice the sustained rate. This prevents legitimate small-team integrations from failing during CI/CD spikes while capping enterprise-level DDoS-like behavior.

## 3. Protecting the Multi: Two-Level Rate Limiting

A common mistake: apply a single per-tenant rate limit. If tenant A has 10 integrations and one integration goes rogue (e.g., retry storm from a misconfigured client), that single integration can consume the entire tenant’s budget, starving the other 9 integrations.

**Design principle:** Isolate by integration (API key, client ID, or IP+user-agent pair) *within* the tenant’s global limit.

**Implementation approach:**
- **Global tenant limit:** A token bucket at tenant level (e.g., 500 req/s).
- **Per-integration cap:** Each integration gets its own token bucket, but its capacity is a fraction of the tenant’s total (e.g., 50 req/s for an integration, and a maximum of 10 integrations active per tenant).

When a request arrives:
1. Check the integration’s bucket. If it has tokens, consume one and proceed.
2. If the integration’s bucket is empty, check the tenant’s global bucket. If the tenant has tokens, *borrow* one (decrement tenant bucket, mark the integration as having exceeded its local rate). This allows a spikey integration to temporarily draw from shared tenant capacity, but it cannot do so indefinitely because the tenant bucket will drain.
3. If both buckets are empty, reject with 429.

**Why this works:** A noisy integration can only borrow from the tenant’s shared pool for a short burst. Once the tenant’s global bucket is exhausted, *all* integrations of that tenant are throttled. This is a natural incentive: the tenant’s admin must either fix the misbehaving integration or upgrade their plan. The system does not punish the entire tenant for one integration’s normal behavior—only when that integration exhausts both its own and the shared pool.

## 4. Headers and Error Messages

Every rate-limited response must give the client enough information to self-correct without support tickets.

**Request accepted (200):**
```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 487
X-RateLimit-Reset: 1623456789   (Unix timestamp when the bucket refills to full)
```

**Request rejected (429):**
```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1623456789
Retry-After: 3                    (integer seconds the client should wait)
```

**Response body for 429:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded the rate limit. Please retry after the time specified in the Retry-After header.",
    "scope": "integration",       // "integration", "tenant", or "global"
    "limit": 500,
    "reset_at": "2025-04-10T10:15:30Z"
  }
}
```

**Why scope matters:** If the scope is “integration”, the client knows only that single key is blocked—other keys of the same tenant are unaffected. If scope is “tenant”, all keys share the problem. This transparency helps teams debug faster.

**Additional consideration:** Include a `Retry-After` header in seconds (integer). Avoid returning fractional seconds—most HTTP clients do not handle them. Also include `X-RateLimit-Reset` as a Unix timestamp for programmatic scheduling.

## 5. Observability: Seeing Whether Limits Work

Rate limiting without observability is faith-based operations. You need to know:

**Metrics to track (per integration and per tenant):**
- `rate_limit.requests_total` (counter)
- `rate_limit.throttled_requests_total` (counter, labelled by `reason: integration|tenant|global`)
- `rate_limit.bucket_usage` (gauge, percentage of tokens remaining — compute from remaining/capacity)
- `rate_limit.burst_borrow_count` (counter, how often a noisy integration borrowed from the tenant bucket)

**Alerts to define:**
- **Throttle rate per tenant > 5% over 5 minutes:** A tenant is repeatedly hitting limits. Could be a legitimate usage spike (upsell opportunity) or a misconfigured client.
- **Throttle rate per integration > 50% over 1 minute:** A specific integration is likely stuck in a retry loop. Alert the platform team.
- **Global rate limit (shared system capacity) exceeded:** If you have a third cluster-level bucket for overall capacity, breach indicates you need to scale.
- **Borrow rate > 10% of total requests:** Noisy integrations are draining the tenant’s shared pool, which will eventually degrade other integrations. Consider raising the per-integration caps or notifying the tenant.

**Logs (structured, include correlation ID):**
- Every throttle event: `{tenant_id, integration_id, request_path, rate_limit_scope, bucket_remaining, latency_ms}`
- Every bucket refill (periodic, aggregated): `{action: "refill", tenant_id, before_count, after_count}` — helps detect clock drift or misconfigurations.

**Dashboards:**
- Heatmap showing throttle rate per tenant-hour (identify noisy tenants without paging).
- Distribution of response times before vs. after throttling—if average latency increases *after* limits are applied, your rate limiter itself may be the bottleneck (e.g., Redis hot key contention).

**Practical tip:** Log the `Retry-After` value you send. If clients ignore it and resend immediately, you can detect non-compliant integrations and escalate.

## Recommended Baseline Design

For a multi-tenant API serving both small teams and enterprise customers:

1. **Algorithm:** Token bucket per integration + token bucket per tenant. Integration bucket capacity = tenant capacity / max_integrations_per_tenant (e.g., 10). Tenant bucket refill = plan-specific rate. Allow borrowing from tenant bucket when integration bucket is empty, but only up to tenant bucket capacity.

2. **Storage:** In-memory (local Go/Rust map) or Redis with 1-minute TTL per bucket key. Avoid distributed counters requiring consensus—you can tolerate +-5% variance for rate limiting.

3. **Headers:** Always return `X-RateLimit-*` and `Retry-After`. Error response includes scope and reset time.

4. **Observability:** Counters for throttled requests per scope, logs with tenant+integration ID, alerts for >5% tenant throttle rate and >50% integration throttle rate.

5. **Enforcement point:** Middleware at API gateway level, before authentication if possible (you can check the API key in the header without fully validating it). This prevents wasted work on rejected requests.

6. **Graceful degradation:** If the rate limiter’s backend (e.g., Redis) is unreachable, fail *open* (allow requests) temporarily, but log aggressively. Rate limiting is a reliability feature; losing availability over a sidecar is worse.

This design ensures that a small team with a single integration enjoys burst-friendly protection, while an enterprise with 50 integrations cannot be brought down by one misbehaving client. The metrics will tell you when the balance needs adjusting—and the headers will tell your customers before they call support.
````
