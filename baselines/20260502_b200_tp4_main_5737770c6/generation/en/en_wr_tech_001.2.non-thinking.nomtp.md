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
- Elapsed seconds: 14.786214
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2225, "completion_tokens": 2073, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2073
- Total tokens: 2225

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
# Rate Limiting for Multi-Tenant APIs: Balancing Protection and Precision

## 1. The Four Pillars of API Governance

Before designing rate limits, we must distinguish four concepts that often get conflated:

**Authentication** answers "Who are you?" — verifying identity via API keys, OAuth tokens, or JWT claims. It operates at the request level.

**Authorization** answers "What are you allowed to do?" — checking permissions against resources (e.g., "Can this user DELETE invoices?"). It operates at the action level.

**Quotas** answer "How much total usage are you entitled to over a billing period?" — hard ceilings on events per month, storage consumed, or requests made. They operate at the account/tenant level over long windows (days, months).

**Rate limits** answer "How fast can you send requests?" — protecting system stability by smoothing traffic within short windows (seconds to minutes). They operate at the request level and are distinct from quotas: a tenant can hit a rate limit well before exhausting their monthly quota.

For a multi-tenant system serving both small teams and enterprise customers, quotas are a contractual/commercial concern while rate limits are a technical safety mechanism. The design must support both independently.

## 2. Practical Comparison of Rate Limit Algorithms

### Token Bucket
Conceptually: a bucket holds N tokens; each request consumes one token; tokens refill at rate R per second. If the bucket is empty, the request is denied.

**Strengths:** Allows bursts up to bucket size (ideal for small teams that may spike briefly). No hard-window boundaries; traffic can be smooth across clock edges.

**Weaknesses:** Memory-inefficient per-tenant (requires storing current token count and last refill timestamp). Can be slightly imprecise under very high concurrency without atomic updates.

**Best for:** Enterprise tenants with variable traffic patterns who need to absorb occasional bursts.

### Fixed Window
Conceptually: each clock-aligned window (e.g., 1 second, 1 minute) has a counter. When counter exceeds threshold, requests are blocked for the remainder of the window.

**Strengths:** Extremely simple to implement, constant memory per tenant (just a counter and window start time).

**Weaknesses:** Thundering herd at window boundaries: all tenants can hammer at the start of a new window. Allows 2x the limit in adjacent windows if a request passes at the very end of one window and the very start of the next.

**Best for:** Very high throughput systems where simplicity outweighs fairness, but dangerous for multi-tenant where one tenant can exploit boundary effects.

### Sliding Window (Log or Counter)
Two common implementations: sliding log (stores timestamps of all requests) and sliding window counter (approximate, using weighted overlap of two fixed windows).

**Strengths:** Smoothest rate enforcement; no boundary spikes. Precisely enforces "100 requests in the last 60 seconds" without gaps.

**Weaknesses:** Sliding log is memory-heavy for high-rate tenants. Sliding window counter requires careful implementation to handle clock skew and concurrent updates.

**Best for:** Systems where fairness and predictability are critical — especially multi-tenant APIs where one tenant's burst shouldn't affect another.

**Recommendation:** Sliding window counter with a precision of 1 second and a rolling window length of 60 seconds. This balances accuracy and memory. Store per-tenant counters in a fast cache (Redis-like) with atomic increment-and-expire operations.

## 3. Tiered Isolation: Not Punishing the Whole Tenant

A common mistake: applying a single global rate limit per tenant. If one noisy integration (e.g., a misconfigured auto-sync script) exhausts the tenant's limit, *all* other users and integrations of that tenant are blocked.

**Solution: Three-level rate limiting hierarchy**

1. **Integration-level limits:** Each API key or OAuth client gets its own lightweight rate limit (e.g., 10 requests/second). This contains the blast radius.

2. **Team/Project-level limits:** If your API supports sub-accounts or projects within a tenant, add an intermediate bucket. This prevents one rogue team from starving another.

3. **Tenant-level limits:** A global ceiling that only activates when aggregate traffic from all integrations approaches dangerous levels. This should be set high enough to never fire under normal operation — it's a failsafe, not a throttle.

When a request is rate-limited, the response must indicate *which* limit was hit: `X-RateLimit-Scope: integration`. This lets clients debug without confusion.

Additionally, implement **priority queuing**: enterprise tenants may have SLAs that require lower latency. Tag requests with a priority (derived from tenant tier) so that during contention, lower-priority requests are rejected first. The token bucket can be implemented with two nested buckets — one for guaranteed capacity, one for best-effort burst.

## 4. Response Headers and Error Messages

Every rate-limited response must tell the client exactly what happened and when to retry. Standard headers (inspired by GitHub and Twitter APIs):

**Request Accepted:**
- `X-RateLimit-Limit`: The maximum requests allowed in the current window (e.g., 100)
- `X-RateLimit-Remaining`: Number of requests left in the current window
- `X-RateLimit-Reset`: Unix timestamp when the window resets (for sliding window, this is the end of the rolling window)
- `X-RateLimit-Scope`: `integration`, `project`, or `tenant` — shows which level was measured

**Request Denied (HTTP 429 Too Many Requests):**
- `Retry-After`: Seconds until the client should retry (integer, not a timestamp)
- `X-RateLimit-Limit`, `X-RateLimit-Remaining` = 0, `X-RateLimit-Reset`
- JSON body: `{"error": "rate_limit_exceeded", "scope": "integration", "retry_after": 30, "message": "Integration 'staging-auto-sync' exceeded 10 requests/second. Retry after 30 seconds."}`

**Why not 503?** 503 implies server-side failure; 429 is explicit about client behavior. Distinguish between "you're too fast" and "server is overloaded".

**Error messages must include the scope and the specific limit that was breached.** Enterprise tenants managing dozens of integrations need to identify which integration caused the block without guessing.

## 5. Observability: Measuring Protection Without Blocking Legitimate Use

Your rate limiting system must not be a black box. Instrument the following:

### Metrics (to a time-series system)
- `rate_limit.requests.total` (counter): All requests
- `rate_limit.requests.accepted` (counter): Passed rate limit
- `rate_limit.requests.rejected` (counter): Rejected, tagged by scope (`integration`, `project`, `tenant`) and reason
- `rate_limit.current_usage` (gauge): For each tenant/integration, current token bucket fill level or window count — helps spot approaching limits before they trigger
- `rate_limit.enforcement_latency` (histogram): Time spent in the rate limit check — should be <1ms. Spikes indicate backend overload.

### Logs
- **Every rate limit hit** must log the tenant ID, integration ID, current limit, and threshold.
- **Noisy integration detection**: If a single integration triggers rate limiting more than N times in a rolling hour, emit a warning log. This is a signal to investigate misconfiguration.
- **Do not log every accepted request** — you'll drown in data. Sample at 1% for accepted requests.

### Alerts (three tiers)
1. **Warning:** Any tenant exceeds 80% of their limit for 5 consecutive minutes → proactive outreach possible.
2. **Critical:** A tenant is rate-limited for more than 1% of their requests over 10 minutes → a noisy integration is likely hurting their own users.
3. **Pager-worthy:** Rate limit checks themselves are failing (e.g., cache is down) → all requests may pass through unprotected, risking cascading failure.

### Dashboards
- Top 10 tenants by rejection rate
- Rejection rate by scope (integration vs. tenant)
- Time-series showing "rejections / total requests" — if this ratio drops as traffic grows, limits are too permissive; if it rises sharply, limits may be too tight.

## Recommended Baseline Design

For a multi-tenant API serving teams of 5 to enterprises of 5,000:

- **Algorithm:** Sliding window counter with 1-second precision and 60-second window. Use atomic increments in a distributed cache.
- **Three tiers of limits:**
  - Integration: 10 req/s (default), configurable per key.
  - Project: 100 req/s (default), with per-project override.
  - Tenant: 500 req/s (default), with strict enforcement only when aggregate exceeds 80% of this value.
- **Priority:** Enterprise tenants get a higher token bucket fill rate and a larger burst allowance (e.g., 500 tokens vs. 100).
- **Headers:** Always return `X-RateLimit-*` with scope; for denials, include `Retry-After` and a descriptive JSON body.
- **Observability:** Track rejections by scope; alert if any integration causes >5% of its own requests to be rate-limited over 10 minutes.
- **Fallback:** If rate limit cache is unreachable after retries, **allow the request** but log a critical alert. Better to risk overload than to block all traffic due to infrastructure failure.

This design isolates noisy integrations, protects tenant-wide availability, and gives both small teams and enterprise customers predictable, debuggable behavior. Rate limiting should be invisible to well-behaved clients and loudly explanatory to misbehaving ones.
```
