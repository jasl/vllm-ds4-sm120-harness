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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.054309
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2323, "completion_tokens": 2171, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2171
- Total tokens: 2323

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
# Designing Rate Limiting for Multi-Tenant APIs: Balancing Small Teams and Enterprise Customers

## 1. Authentication, Authorization, Quotas, and Rate Limits – The Critical Distinctions

Before designing rate limiting, we must clarify four distinct concepts that are frequently conflated:

**Authentication** verifies *who* you are. It answers: "Is this request coming from a valid API key, OAuth token, or client certificate?"

**Authorization** determines *what you may do*. It answers: "Does this tenant have permission to call this endpoint, perform this action, or access this resource?"

**Quotas** define *how much you may consume over a long period* (e.g., 10,000 requests per month, 5 GB of storage per day). Quotas are enforced periodically (often daily or monthly) and are typically soft limits—exceeding them might degrade service or require contacting sales, not immediately reject requests.

**Rate limits** control *how fast you may consume* over short windows (e.g., 100 requests per second, 10,000 per hour). Rate limits protect system stability, prevent accidental loops, and guard against a single noisy client degrading service for others. Exceeding a rate limit should *immediately* reject the offending request.

The practical consequence: quota enforcement can be offline and eventually consistent; rate limiting must be evaluated on every request, in the hot path, with minimal latency.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window – Practical Trade-offs

### Fixed Window (e.g., reset every 60 seconds)
- **Pros**: Simple to implement; requires only a counter per tenant and a window boundary.
- **Cons**: Burst traffic at the window boundary can cause double throughput. Example: a client sends 100 requests at 59.9s and 100 requests at 60.1s—both windows allow 100 requests, so the server sees 200 in 0.2s.
- **Practical use**: Acceptable for very coarse limits (e.g., 10,000/hour) where the boundary spike is tolerable, but dangerous for sub-minute limits.

### Sliding Window Log
- **Pros**: Perfectly smooth—tracks timestamps of every request in the current window. No boundary spikes.
- **Cons**: O(N) memory per tenant where N is the limit. For 10,000 requests per minute, you store 10,000 timestamps in memory for that tenant.
- **Practical use**: Unworkable for high-traffic enterprise tenants. Use only for very low limits (e.g., 10 requests per second).

### Sliding Window Counter (Approximate)
- **Pros**: Uses two counters (current and previous window partial) with a weighted calculation. O(1) memory per tenant. No boundary spike.
- **Cons**: Slightly imprecise (usually within 5-10% of true rate). Implementation requires careful handling of overlapping windows.
- **Practical use**: The best general-purpose choice for multi-tenant APIs. Provides near-perfect fairness with minimal memory.

### Token Bucket
- **Pros**: Allows bursts up to bucket capacity while enforcing average rate. Intuitive: refills tokens at a steady rate; requests consume tokens.
- **Cons**: Requires maintaining both token count and last refill timestamp. Burst behavior can still overwhelm backends if bucket size is too large.
- **Practical use**: Excellent for APIs where clients need occasional spikes (e.g., CI/CD pipelines). **Recommendation**: Combine token bucket with a hard cap on burst size (e.g., bucket of 1,000 tokens, refill 100/s, but never allow more than 1,000 requests in any 10-second window).

**Practical rule**: Use sliding window counter for per-second limits, token bucket for per-minute/ per-hour limits, and fixed window only for daily quotas.

## 3. Protecting the Tenant from One Noisy Integration

The cardinal sin of multi-tenant rate limiting: a malfunctioning integration (e.g., a retry loop, a stuck webhook consumer, a misconfigured script) can exhaust the entire tenant's rate limit, blocking all other users, API keys, and services on that tenant.

### Solution: Hierarchical Rate Limiting

Implement three levels of rate limits, enforced in order:

1. **Global tenant limit** (per-tenant, across all keys). This is the outermost gate. Protects your infrastructure from a tenant going rogue.
2. **Per-integration (API key) limit**. Each API key gets its own bucket/ counter. This is *lower* than the global tenant limit. The sum of all per-key limits should be slightly less than the global limit (e.g., 90% of global).
3. **Per-endpoint limit** (optional). Write-heavy endpoints (create, update) get separate limits from read-heavy endpoints (get, list).

**Behavior**: If "Integration A" goes into a retry storm, it hits its per-key limit first. Other API keys on the same tenant continue to operate normally. Only if every key is saturated does the global tenant limit engage.

Additionally, separate *burst* capacity from *sustained* capacity. Every tenant gets a small burst pool (e.g., 50 requests) that can be used by any key—but when exhausted, each key must stay within its own rate. This prevents a legitimate new integration from being denied just because another key exhausted the tenant's burst cushion.

## 4. Headers and Error Messages – A Contract, Not a Surprise

Clients must be able to programmatically understand their limit status. Every response (success and error) should include:

**Required headers on every response:**

| Header | Content | Example |
|--------|---------|---------|
| `X-RateLimit-Limit` | The limit for the current enforcement period | `100` (requests per minute) |
| `X-RateLimit-Remaining` | Requests remaining in the current window | `73` |
| `X-RateLimit-Reset` | Unix timestamp when the window expires | `1735689600` |

**When rate limited (HTTP 429 Too Many Requests):**

Return a JSON body with:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded for this API key. Limit: 100 requests per minute. Reset at: Mon, 01 Jan 2024 00:00:00 UTC.",
    "retry_after": 12
  }
}
```

- **`retry_after`** (seconds until retry): Critical for clients implementing exponential backoff.
- **Never return `message: "Too many requests"` without details.** Developers need to know *which* limit they hit (key-level vs. tenant-level) and *when* they can retry.

For tenant-level blocking: return a different error code, e.g., `TENANT_RATE_LIMIT_EXCEEDED`, so the client knows it's not just their key but an entire account issue.

## 5. Observability – Proving Limits Work

Rate limits are a defensive mechanism. You must observe three things:

| Sensor | What it measures | How to use it |
|--------|------------------|---------------|
| **Requests per second** (per tenant) | Raw throughput | Baseline for setting limits. Alert if a single tenant > 50% of total capacity. |
| **429 response rate** (per tenant, per key) | How often limits are hit | Alert if 429 rate > 5% of requests for any key (suggests integration is misconfigured). |
| **Rate limit latency** | Time spent checking limits | Must be < 1ms p99. If > 5ms, your rate limiter is the bottleneck. Log p99/p999. |

**Alerts (actionable, not noise):**

1. **P1**: Any tenant's 429 rate exceeds 50% of its requests for > 5 minutes → likely a loop. Contact the tenant.
2. **P2**: Global rate limit latency p99 > 5ms → your rate limiter implementation is failing. Switch to local Redis/ in-memory + replica reads.
3. **P3**: A tenant consistently uses 90%+ of its limit but never hits it → consider offering a plan upgrade.

**Logging**: Every 429 response should log: tenant_id, api_key_id, endpoint, current limit, remaining, reset time. Do *not* log every successful request—too expensive.

**Metrics (internal dashboards)**: Track rate limit state per tenant as a gauge: `remaining_count / limit` ratio. When this ratio stays below 0.1 for an extended duration, it's a signal that limits may be too tight or the client needs a higher tier.

## Recommended Baseline Design

For a backend serving small teams (10-100 req/s burst) and enterprises (1000+ req/s sustained):

- **Algorithm**: Sliding window counter for per-second limits; token bucket for per-minute limits. Store counters in Redis (or equivalent in-memory store with TTL) partitioned by tenant + API key.
- **Hierarchy**: Three tiers—global tenant limit (e.g., 5000 req/min), per-key limit (e.g., 2000 req/min per key, with max 5 keys per tenant), and a system-wide ceiling (e.g., 100,000 req/min total).
- **Burst buffer**: Each tenant gets a 50-request burst pool shared across all keys, refreshed every minute.
- **Headers**: Always return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. On 429, include `retry_after` in seconds and human-readable `message` with limit details.
- **Error codes**: Separate `RATE_LIMIT_EXCEEDED` (per-key) from `TENANT_RATE_LIMIT_EXCEEDED` (global).
- **Observability**: Log every 429 with tenant_id and key_id. Alert on 429 rate > 5% per key, or rate limiter latency > 5ms. Visualize remaining/limit ratio per tenant over time.

This design keeps small teams unblocked, protects enterprises from their own mistakes, and ensures your API remains available and fair.
````
