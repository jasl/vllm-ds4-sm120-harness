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
- Elapsed seconds: 12.5012
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2135, "completion_tokens": 1983, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 1983
- Total tokens: 2135

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
# Throttle Wisely: Designing Multi-Tenant Rate Limiting for Teams and Enterprises

## 1. The Four Pillars of Access Control

Before designing a rate limiter, you must distinguish four concepts that engineers often conflate:

- **Authentication** answers “Who are you?” – verifying identity via API keys, OAuth tokens, or mTLS.
- **Authorization** answers “What are you allowed to do?” – checking scopes, roles, or resource-level permissions.
- **Quotas** define “How much can you use over a long period?” – monthly API call limits, storage caps, or concurrent job counts. Quotas are enforced asynchronously (e.g., via billing cycles).
- **Rate limits** answer “How fast can you use it?” – short-term traffic shaping to protect system stability. They are enforced synchronously on every request.

A tenant may be authorized to call an endpoint but fail rate limiting because their burst exceeds a second-level window. Conversely, a tenant may be within rate limits but blocked by a monthly quota. These are orthogonal controls.

## 2. Practical Window Algorithms

Three algorithms dominate production choices. Here is how they behave under load:

### Fixed Window
Divide time into discrete intervals (e.g., 1 minute). Each interval has a counter per tenant. When the counter exceeds the limit, reject until the next interval.

*Pros*: Simple, low memory (one counter per tenant per window).
*Cons*: “Boundary burst” problem – at the edge of a window, a tenant can send twice the limit in rapid succession (e.g., 100 requests at 0:59, then 100 more at 1:00). This defeats the purpose of smoothing traffic.

### Sliding Window (Log or Counter)
Track timestamps of recent requests (log) or use a rolling counter with sub-windows (e.g., 1-second buckets within a 60-second window).

*Pros*: No boundary bursts; smooth enforcement.
*Cons*: Memory proportional to request rate (log) or more complex window logic (counter). Worth the complexity for multi-tenant APIs.

### Token Bucket
Each tenant holds a bucket of tokens that refill at a fixed rate (e.g., 10 tokens per second). Each request consumes one token. Bursts are allowed up to the bucket size.

*Pros*: Natural burst absorption; decouples average rate from peak rate.
*Cons*: Requires correctness under concurrent access; token math must handle long idle periods (bucket stays full). Excellent for APIs where small teams occasionally spike but should not saturate the system.

**Practical recommendation**: Use token bucket for per-tenant limits (burst-friendly) and sliding window for global infrastructure protections (e.g., database connection pool limits). Overlap them: a request must pass both.

## 3. Avoiding Tenant-Level Collateral Damage

The cardinal sin in multi-tenant rate limiting is punishing all tenants because one “noisy neighbor” saturates a shared resource. Here is how to design isolation:

### Per-Tenant Buckets with Global Cap
Give each tenant its own token bucket (or sliding window counter). Enforce a global “hard ceiling” (e.g., 10× the highest per-tenant limit) at the load balancer or gateway. This prevents a single tenant from overwhelming the entire system, but it does not hurt other tenants until that global ceiling is breached.

### Integrations as Sub-Tenants
Large enterprise customers often run multiple integrations (webhooks, CI/CD pipelines, internal tools). If you treat the entire enterprise as one tenant, one noisy integration blocks all others. **Solution**: Allow tenants to provision multiple sub-keys or integration-specific tokens, each with its own rate limit bucket, nested under a parent tenant aggregate limit. For example, a tenant’s aggregate limit is 5000 req/min, but each integration is capped at 1000 req/min. Integration A misbehaves; only A is throttled.

### Weighted Priority Queues
For critical endpoints (e.g., authentication, billing), assign a higher priority class. Non-critical traffic (e.g., analytics exports) from a noisy tenant should not preempt critical traffic from other tenants. Implement a weighted fair queuing scheme where each tenant has a minimum guaranteed share of request capacity.

### Circuit Breaker per Integration
If an integration exceeds its limit for N consecutive windows, temporarily blacklist it (HTTP 429) for a cooldown period (e.g., 30 seconds). This prevents retry storms from decaying tokens. The rest of the tenant continues unblocked.

## 4. Headers and Error Responses

Clients need actionable feedback, not just a “429 Too Many Requests.” Standardize these response headers:

```
X-RateLimit-Limit: 1000          # maximum requests per window
X-RateLimit-Remaining: 42        # remaining requests in current window
X-RateLimit-Reset: 1620000000    # Unix timestamp when the window resets (or bucket refills)
Retry-After: 30                  # seconds to wait before retrying (for 429 responses)
```

**Error bodies** (JSON):

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Integration 'webhook-prod-1' exceeded its rate limit of 100 requests per minute. Retry after 30 seconds.",
    "tenant_id": "acme-corp",
    "integration_id": "webhook-prod-1",
    "retry_after_seconds": 30
  }
}
```

**Key design decisions**:
- Return `X-RateLimit-Limit` even for successful responses – let clients prefetch their limit.
- Use `Retry-After` (RFC 7231) with a numeric value, not a date. Most client libraries handle seconds better.
- Include `integration_id` in the error body so enterprises can identify which internal service caused the block.
- For 401/403 (auth/authz), return separate error codes – do not conflate with rate limit errors.

## 5. Observability: Knowing You Are Protecting, Not Blocking

The worst-case scenario is a silent limiter that blocks legitimate traffic while false positives hide in logs. Build these observability pillars:

### Metrics (three golden signals)
- **Per-tenant request rate**: Histogram of requests/second, labeled by tenant tier (small team vs. enterprise). Compare against the limit.
- **Throttle rate by tenant and integration**: Count of 429 responses, segmented. If one integration has a 30% throttle rate, investigate its retry behavior.
- **Global saturation**: P99 latency of the rate limiter itself. If the limiter adds >5ms overhead, it becomes part of the problem.

### Logs
Log every rate limit decision with structured fields: `tenant_id`, `integration_id`, `limit_type` (rate vs. quota), `action` (allowed/throttled), `window_start`. Do **not** log the full request body for throttled requests (privacy & noise). Instead, log a hash of the API key.

### Alerts
- **P1**: Aggregate throttle rate across all tenants exceeds 1% for 5 minutes – indicates a systemic issue (limiter bug or global resource exhaustion).
- **P2**: A single enterprise tenant’s throttle rate exceeds 5% – may indicate a noisy integration or misconfigured client.
- **P3**: Rate limiter CPU/memory utilization >80% – ensure the limiter itself does not become a bottleneck.
- **Positive alert**: When throttle rate drops below 0.1% after a configuration change, confirm the fix is working.

### Testing regimen
Regularly send synthetic burst traffic from a test tenant to verify that (a) throttling kicks in at the correct limit, (b) other tenants are unaffected, and (c) error responses match the specification.

## Recommended Baseline Design

For a multi-tenant API serving both small teams (100 req/min typical) and enterprises (100,000 req/min typical):

1. **Algorithm**: Token bucket per tenant + per integration, with a shared global sliding window for connection-level protections. Token burst size = 2× per-minute limit (allows short spikes).
2. **Isolation**: Each integration key gets its own bucket. Enterprise tenants can request up to 50 integration keys. The parent tenant aggregate bucket (soft limit) is 1.5× the sum of all integration limits – accommodates some concurrency without exact coordination.
3. **Global safety net**: Hard cap at 10% above the highest-tenant aggregate limit. If hit, throttle the current heaviest integration, not the entire tenant.
4. **Headers**: Standard `X-RateLimit-*` headers on all responses, `Retry-After` on 429s. Error body includes `integration_id`.
5. **Observability**: Prometheus-style metrics per tenant and integration; structured logs with 1% sampling of allowed requests; P1 alert on global throttle >1%.
6. **Quota enforcement**: Separate service (async, daily batch) that compares current usage against monthly limits. Do not conflate with rate limiter.

This design ensures that a startup’s cron job can spike without breaking an enterprise’s user-facing API, and a misconfigured enterprise webhook cannot degrade the entire platform. Rate limiting, done well, is invisible to every client except the one causing harm.
````
