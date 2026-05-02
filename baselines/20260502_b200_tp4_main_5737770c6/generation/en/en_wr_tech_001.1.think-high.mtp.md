# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.207758
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2155, "completion_tokens": 2003, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2003
- Total tokens: 2155

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
# Designing Rate Limiting for a Multi-Tenant API: Balancing Small Teams and Enterprise Customers

## 1. Foundational Concepts: Authentication, Authorization, Quotas, and Rate Limits

Before designing rate limiting, you must understand how it differs from related but distinct concepts.

- **Authentication** verifies *who* you are. It answers: "Does this request carry a valid API key, OAuth token, or mTLS certificate?" Without authentication, rate limiting is meaningless—you cannot attribute requests to tenants.

- **Authorization** determines *what you are allowed to do*. It checks: "Can this user read this resource? Can this integration write to that endpoint?" Authorization does not control *how much* or *how fast*—only access rights.

- **Quotas** define *how much* total work a tenant can perform over a billing period (e.g., 100,000 requests per month). Quotas are enforced asynchronously—often post-hoc in billing systems—and can be overridden by prior agreements. They are not real-time traffic controls.

- **Rate limits** control *how fast* requests arrive. They protect system stability by rejecting bursts that could degrade performance for all tenants. Rate limits are enforced synchronously, per unit time (e.g., 100 requests per second).

The critical insight: rate limits and quotas serve different purposes. A tenant may have a high monthly quota but still need strict per-second rate limits to prevent cascading failures.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window: Practical Trade-offs

Three algorithms dominate production systems. Each has distinct behavior under load.

**Fixed Window** divides time into discrete intervals (e.g., 1-minute buckets). A counter resets at the start of each window. If a tenant exhausts their limit in the first second, they lose 59 seconds of capacity. This creates a "burst at window boundary" problem: a client that held back requests can slam the API at 00:00, potentially overwhelming downstream services.

**Sliding Window Log** (or sliding window counter) eliminates the boundary issue by tracking timestamps per request. The window continuously moves: a request at 12:01:30 counts against activity from 12:00:30 onward. This provides smooth enforcement but requires O(n) memory per tenant, where n is the request count in the window. For high-throughput tenants (thousands of requests per second), this becomes expensive in storage and garbage collection.

**Token Bucket** refills tokens at a steady rate (e.g., 100 tokens/sec) and allows a burst up to a configurable capacity (e.g., 200 tokens). An idle tenant accumulates tokens; a busy tenant drains them. This naturally handles traffic spikes while capping sustained throughput. The burst capacity provides breathing room for legitimate retries or periodic heavy writes. Memory cost is constant per tenant (two integers: tokens and last refill timestamp). For most backends, token bucket is the pragmatic choice.

Recommendation: Use token bucket per tenant, per endpoint group (read vs. write). Avoid one global bucket per tenant—a UI polling endpoint should not starve a payment webhook.

## 3. Avoiding "Punish the Entire Tenant" for One Noisy Integration

Enterprise tenants run multiple integrations: a cron job, a webhook receiver, and user-facing dashboards. A misconfigured cron job polling every 100ms should not block a real-time dashboard used by the CEO.

**Solution: Nested Rate Limits with Shared Budgets**

Implement two tiers:
- **Per-API-key** rate limit (tight, e.g., 50 requests/sec per key)
- **Per-tenant aggregate** rate limit (looser, e.g., 500 requests/sec across all keys)

Each API key has its own token bucket. When a key exceeds its limit, only that key is throttled. However, if the total across all keys exceeds the tenant limit, *all* keys from that tenant are rejected—but only after the per-key limits have already constrained the noisy key.

Additionally, implement **least-recently-used (LRU) per-route limits**. If integration A hammering `/health` exhausts the tenant's read budget, but integration B calls `/reports`, B should still succeed. Route-based token buckets prevent cross-contamination.

For enterprise customers, expose a **"priority" field** in the API key configuration. Higher-priority keys (e.g., for webhooks) can reserve a percentage of the tenant's aggregate budget, protected from lower-priority keys (e.g., for scheduled scripts).

## 4. HTTP Headers and Error Messages for API Clients

Clients need actionable information to back off intelligently. Return these headers on every response:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 47
X-RateLimit-Reset: 1691234567
```

- `X-RateLimit-Limit`: The maximum requests allowed in the current window (for token bucket, this is the per-second refill rate).
- `X-RateLimit-Remaining`: How many requests the client can still make before being throttled.
- `X-RateLimit-Reset`: Unix timestamp when the bucket will have refilled enough to allow the next request. For token bucket, calculate: `now + (tokens_needed / refill_rate)`.

**On rejection**, return HTTP 429 Too Many Requests with a JSON body:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Your API key has exceeded its per-second rate limit. Retry after 2.3 seconds.",
  "retry_after_seconds": 2.3,
  "limit_type": "per_key"
}
```

Include `limit_type` to distinguish between per-key and per-tenant throttling. This helps clients decide which key to rotate or whether to escalate support tickets.

For enterprise customers, also return `X-RateLimit-Scope: tenant` when the aggregate limit is hit, so their ops team knows the entire team is affected.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting is a safety valve, not a substitute for capacity planning. Without observability, you may block legitimate traffic or silently degrade reliability.

**Metrics to expose to your monitoring system:**

- `rate_limit_current_usage{tenant_id, api_key, route_group}` — Gauges how full each token bucket is (0 = empty, 1 = full). A bucket staying below 0.2 during peak hours suggests the limit is too low.
- `rate_limit_rejected_total{tenant_id, limit_type}` — Count of 429 responses. Spike per tenant? Investigate misconfigured clients. Steady increase across all tenants? Limits are too tight.
- `rate_limit_bucket_refill_rate{tenant_id}` — How fast tokens are being consumed vs. refilled. If consumption consistently exceeds refill for a major enterprise, consider adjusting their plan.
- `rate_limit_burst_capacity_exceeded_total` — How often the burst capacity is hit. Frequent bursting indicates clients need higher steady-state limits.

**Logging:** Every rejected request should include throttled fields (tenant, key, route, limit_type) at WARN level. Do *not* log accepted requests at INFO unless debugging—log volume will overwhelm systems.

**Alerts:** Set three tiers:

1. **P0 Alert**: Any single tenant's rejection rate exceeds 30% of their request volume for 5 minutes. This indicates a client misconfiguration or a breaking change causing retries.
2. **P1 Alert**: Aggregate 429 rate across all tenants exceeds 5% of total API traffic. This likely means limits are globally too low or a DDoS is in progress.
3. **P2 Alert**: A top-10 enterprise tenant has >1000 429 responses in 1 hour. Proactively reach out to their ops team before they complain.

## Recommended Baseline Design

Start simple, then evolve:

1. **Algorithm**: Token bucket per API key + per tenant aggregate. Token bucket capacity = 2x the per-second refill rate to allow short bursts.
2. **Defaults**:
   - Small team plan: 50 req/sec per key, 200 req/sec tenant aggregate, burst capacity 100 per key.
   - Enterprise plan: 200 req/sec per key, 1000 req/sec tenant aggregate, burst capacity 400 per key. All configurable via admin API.
3. **Route groups**: Separate read (GET, HEAD) and write (POST, PUT, DELETE) buckets. Write buckets should have lower limits (e.g., 20 req/sec) to protect data integrity.
4. **Headers**: Always return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. On 429, include JSON body with `retry_after_seconds`.
5. **Observability**: Export `current_usage` and `rejected_total` per tenant to your metrics pipeline. Alert on P0 (tenant >30% rejection) and P1 (global >5% rejection).
6. **Escalation path**: Enterprise customers can request a "burst override" via API key metadata—temporarily doubles their per-key capacity for 1 hour (logged and audited).

This baseline withstands real-world patterns: a small team's scraping script cannot DDOS the API, and a large enterprise's internal migration can burst without support tickets. Adjust as you observe actual traffic shapes—every multi-tenant system eventually requires tuning based on production data.
````
