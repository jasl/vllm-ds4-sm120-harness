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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 14.805016
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2226, "completion_tokens": 2074, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2074
- Total tokens: 2226

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
# Rate Limiting for Multi-Tenant APIs: Balancing Protection and Fairness Across Teams and Enterprises

Designing rate limiting for a multi-tenant API that serves both small teams and enterprise customers is fundamentally a reliability engineering problem—not a security one. The goal is to protect shared infrastructure from overload while ensuring that one tenant’s noisy integration does not degrade service for others. This requires careful architectural choices around throttling algorithms, tenant isolation, observability, and client communication.

## 1. Clarifying the Four Controls

Before designing rate limits, you must distinguish them from adjacent concepts:

**Authentication** verifies *who* the client is (e.g., API key validation).
**Authorization** determines *what* the client is allowed to do (e.g., read vs. write scopes).
**Quotas** define a *hard, pre-agreed* maximum usage over a long period (e.g., 1 million requests per month for a free tier). Exceeding a quota typically blocks further requests until the period resets or the plan is upgraded.
**Rate limits** enforce *short-term* request velocity (e.g., 100 requests per second). They prevent burst traffic from overwhelming resources and are typically enforced regardless of quota headroom.

A common mistake is conflating quotas with rate limits. Quotas are contractual; rate limits are operational. Enterprise customers may have high monthly quotas but still need per-second rate limits to prevent cascading failures.

## 2. Practical Algorithm Selection

Three algorithms dominate production systems. Their practical differences lie in burst tolerance, memory overhead, and fairness under load.

**Token Bucket** is the most flexible for multi-tenant workloads. Each tenant has a bucket that refills at a configured rate (e.g., 10 tokens per second) and a maximum burst size (e.g., 100 tokens). A request consumes one token; if the bucket is empty, the request is rejected or queued. Bursts are naturally absorbed as long as tokens remain. The algorithm allows tenants who are idle to accumulate tokens and then spike, which is valuable for batch-processing integrations. However, it requires per-tenant state and careful choice of refill granularity.

**Fixed Window** (e.g., resetting counters every second) is simple to implement but suffers from “boundary effects.” Suppose a tenant sends 80 requests at the end of second 0, and 80 more at the start of second 1. Both windows show 80 requests, so the rate is “allowed” even though 160 requests arrived within one actual second. This makes fixed windows unsuitable for protecting latency-sensitive systems.

**Sliding Window Log** maintains timestamps of each request, allowing precise enforcement over a moving time horizon (e.g., “no more than 30 requests in the last 10 seconds”). It is memory-intensive—every request must be stored until it expires—but provides the fairest behavior for noisy neighbors. A more efficient variant, **Sliding Window Counter**, tracks an approximate request count by summing the previous window’s count with the current window’s fraction. This is a good practical compromise.

**Recommendation for multi-tenant APIs:** Use token bucket for most cases, with per-tenant keys, because it handles natural bursts without penalizing idle periods. Reserve sliding window for enterprise tenants with strict SLAs on request timing.

## 3. Avoiding Punishment of an Entire Tenant for One Noisy Integration

A single misconfigured script or CI pipeline can consume an entire tenant’s rate limit, causing all legitimate user requests to be blocked. This is a common—and painful—failure mode.

The solution is multi-dimensional rate limiting:

**Per-client-key sub-limits.** If a tenant has one API key per integration (e.g., one for mobile apps, one for CI/CD, one for back-office scripts), enforce a sub-limit per key *within* the tenant’s global limit. For example, a tenant’s global limit is 500 req/s, but any single key is capped at 200 req/s. This ensures that one noisy key cannot exhaust the tenant’s entire budget.

**Tenant-level isolation with headroom.** Always enforce a hard tenant-level cap *after* per-key limits. This prevents a key from accidentally bypassing the tenant cap, but the tenant cap should be generous enough to absorb normal cross-key variance.

**Priority tiers.** For enterprises, allow critical integrations (e.g., checkout APIs) to request higher priority. Non-critical requests from the same tenant are dropped first when limits approach. This requires request metadata (e.g., a `X-Priority` header) and a priority-aware token bucket.

**Graceful degradation.** When a tenant exceeds limits, do not drop *all* requests. Instead, reject requests from the specific overloaded key, returning a `429 Too Many Requests` with an estimate of when new tokens will be available. Other keys from the same tenant continue to work.

## 4. Headers and Error Messages for API Clients

Clients need clear, machine-readable feedback to self-throttle and debug issues. A well-designed rate-limit response includes:

**Response headers (for every request):**
- `X-RateLimit-Limit` – The maximum requests allowed per window/burst (e.g., `100`).
- `X-RateLimit-Remaining` – The number of requests left in the current window (e.g., `42`).
- `X-RateLimit-Reset` – Unix timestamp (or ISO 8601) when the limit resets (for windows) or when the bucket refills to full (for token buckets).

**429 response headers:**
- `Retry-After` – Number of seconds (or `HTTP-date`) the client should wait before retrying.
- `X-RateLimit-RetryAfter` – Same value as `Retry-After`, but as an integer of seconds, for easier parsing.

**Error body (JSON):**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Request rate limit exceeded. Please reduce your request rate.",
    "retry_after": 5,
    "limit": 100,
    "remaining": 0,
    "reset": 1691234567
  }
}
```

Avoid vague messages like “Too Many Requests.” Include the tenant ID or key ID (if safe to expose) to aid debugging. For enterprise customers, consider adding a `X-RateLimit-Tier` header indicating their current provisioned tier, so they can correlate limits with their plan.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting is only effective if you know it’s working—or failing. The observability stack must answer: “Are rate limits protecting reliability without blocking legitimate use?”

**Key metrics (expose via Prometheus or similar):**
- `rate_limit_requests_total{tenant, key, status}` – Count of allowed vs. denied requests, sliced by tenant and key.
- `rate_limit_tokens_available` – Current token count per tenant (percentile distribution). Useful for detecting when tenants are chronically close to limits.
- `rate_limit_throttled_duration_seconds` – How long requests are delayed (if using queuing) or how long clients wait before retrying.
- `rate_limit_burst_peak_per_second` – Max request rate per tenant, per second. Spikes indicate noisy integrations.

**Logs:** Log every limit denial with structured fields: tenant ID, key ID, request ID, endpoint, limit value, current count, and timestamp. Avoid logging every *allowed* request—cardinality will explode. Instead, sample at low rate (e.g., 1%) for allowed requests to debug latency issues.

**Alerts:**
- **Critical:** Any tenant hits 100% of its limit for more than 1 minute. This may indicate misconfiguration or a genuine DDoS.
- **Warning:** A tenant consistently uses >90% of its limit over a 5-minute sliding window. This signals growth or a noisy integration that may soon cause issues.
- **High-priority:** Rate-limit denial rate across the entire platform exceeds 0.5% of total requests. This suggests a system-wide bottleneck, not a tenant problem.

**Dashboards:** Build a per-tenant heatmap showing request rate vs. limit over time. Color-code denial rates. This quickly reveals which tenants are “close to the edge” and which are quiet.

## 6. Recommended Baseline Design

For a multi-tenant API supporting teams to enterprises, start with this architecture:

- **Algorithm:** Per-tenant token bucket with a key-level sub-bucket. Use sliding window counters for tenants with strict concurrency SLAs.
- **Storage:** In-memory (e.g., Redis) with per-tenant keys and TTLs aligned to bucket refill intervals. Use Lua scripts for atomic token consumption.
- **Configuration:** Store limits in a central config service mapping `(tenant_id, api_key)` to `(max_tokens, refill_rate_per_second, burst_size)`. Expose a UI for enterprise customers to adjust per-key limits within their plan bounds.
- **Headers:** Return `X-RateLimit-*` on every response, with `Retry-After` on 429s.
- **Observability:** Export metrics per tenant and per key. Alert on >90% utilization and any 429 spikes.
- **Graceful isolation:** Never allow one key to consume the entire tenant budget. Use per-key sub-limits that sum to no more than 80% of the tenant limit, reserving 20% as headroom for other keys.

This design balances protection, fairness, and practical implementation complexity. Rate limiting is not a “set and forget” feature—it requires iterative tuning as tenant behavior evolves. The metrics will tell you when to adjust.
````
