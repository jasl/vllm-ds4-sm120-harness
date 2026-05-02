# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-v4-flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: expectation checks skipped
- Detail: `expectation checks skipped`
- Elapsed seconds: 26.226505
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "completion_tokens": 2084, "total_tokens": 2236, "prompt_tokens_details": {"cached_tokens": 128}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 24}`
- Prompt tokens: 152
- Completion tokens: 2084
- Total tokens: 2236

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
# Rate Limiting in the Wild: Designing for Multi-Tenant APIs Used by Small Teams and Enterprise Customers

## 1. Authentication, Authorization, Quotas, and Rate Limits – The Four Pillars

Before designing rate limiting, we must distinguish four concepts that engineers frequently conflate:

- **Authentication** answers “Who are you?” – validating identity via API keys, OAuth tokens, or mTLS certificates.
- **Authorization** answers “What are you allowed to do?” – checking permissions (e.g., read vs. write, access to specific resources).
- **Quotas** answer “How much total usage are you allowed over a billing period?” – a contractual limit (e.g., 100,000 requests per month) enforced soft or hard.
- **Rate limits** answer “How fast can you send requests?” – a real-time traffic-shaping mechanism to protect system stability, not to cap total usage over long periods.

**Key insight:** A quota is a business contract; a rate limit is an operational guardrail. An enterprise tenant might pay for 10 million requests/month (quota), but still be rate-limited to 500 requests/second to prevent a single misconfigured integration from degrading other tenants.

---

## 2. Algorithm Choices: Practical Trade-offs

### Token Bucket
Maintains a bucket of tokens that refills at a fixed rate (e.g., 10 tokens/second). Each request consumes one token; if the bucket is empty, the request is blocked.

- **Strengths:** Allows short bursts (up to bucket capacity). Simple to reason about. Memory efficient – one counter per tenant, plus a last-refill timestamp.
- **Weaknesses:** A burst of capacity + slow refill can still cause a spike. Hard to enforce *sustained* average rate over very short windows without tweaking bucket depth.
- **Best for:** APIs where short bursts are acceptable (e.g., batch upload endpoints, webhook deliveries).

### Fixed Window
Counts requests in discrete time buckets (e.g., 1,000 requests per minute). Reset at the end of each minute.

- **Strengths:** Extremely simple to implement and debug. Easy to reason about for billing and dashboards.
- **Weaknesses:** “Stampeding herd” problem – at the boundary of two windows, a client can burst 2x the limit (last 500 ms of minute N + first 500 ms of minute N+1). This can flood downstream services.
- **Best for:** Coarse control where minor bursts are tolerable (e.g., read-only analytics endpoints with long cache TTLs).

### Sliding Window (Log or Counter-Based)
Maintains a rolling log of timestamps (or uses a smooth approximation like a sliding window counter). Rejects requests when the count in the last N seconds exceeds a threshold.

- **Strengths:** Eliminates the boundary burst problem. Fairer to clients.
- **Weaknesses:** Higher memory overhead for log-based (storing timestamps). Counter-based approximation (e.g., Redis sorted sets) reduces accuracy slightly but is far cheaper.
- **Best for:** Production-critical APIs where request patterns are bursty but must be smoothed, and where fairness across tenants matters.

**Practical recommendation:** Use *token bucket* for most endpoints (burst tolerance + simplicity), and *sliding window counter* for high-value write paths like payment or order creation where bursty traffic could cause data integrity issues.

---

## 3. Tenant Isolation: Don’t Punish the Entire Customer for One Noisy Integration

A multi-tenant API serves both small teams (one integration, low throughput) and enterprise customers (multiple internal services, high throughput). The worst outcome: a single misbehaving integration within an enterprise tenant consumes that tenant’s entire rate limit, starving their other legitimate services.

**Solution: Two-tier rate limiting**

1. **Global tenant limit** (e.g., 5,000 requests/minute per tenant). This protects the platform from a tenant monopolizing capacity.
2. **Per-integration (or per-API key) limit** nested *under* the tenant limit (e.g., 200 requests/minute per API key, with a max of 25 keys per tenant).

When a call arrives, the system checks:
   - Does this API key exceed its own limit? → `429 Too Many Requests` with `retry-after` header.
   - Does this tenant (aggregated across all keys) exceed its limit? → same `429`, but the error message should indicate *which* key caused the problem (without leaking info from other keys).

This way, a noisy integration within an enterprise tenant hits its own limit – not the tenant’s entire pool. The enterprise can still operate other integrations. The small team with one key never sees cross-tenant interference.

---

## 4. Headers and Error Responses That Clients Actually Understand

Clients need three things: **transparency**, **actionability**, and **predictability**.

### Standard Rate-Limit Headers (Returned on Every Response)

```
X-RateLimit-Limit: 200
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1672531199
Retry-After: 12
```

- `X-RateLimit-Limit`: the maximum allowed requests in the current window (e.g., 200 requests per minute).
- `X-RateLimit-Remaining`: how many requests the client can still make in this window.
- `X-RateLimit-Reset`: Unix timestamp when the window resets. Helps clients plan retries.
- `Retry-After`: sent only on `429`, in seconds – tells the client when it can safely retry.

### Error Body (HTTP 429 Too Many Requests)

```json
{
  "error": {
    "type": "rate_limit_exceeded",
    "message": "Too many requests. Retry after 12 seconds.",
    "scope": "api_key",
    "retry_after_seconds": 12,
    "limit": 200,
    "remaining": 0
  }
}
```

- `scope` can be `"api_key"`, `"tenant"`, or `"global"`. Helps the client know *which* limit they hit.
- Never reveal exact limits of other tenants or internal thresholds.

---

## 5. Observability: Metrics, Logs, and Alarms

Rate limits are a *protective* mechanism – but if they’re too aggressive, they block legitimate use. Observability answers: “Are we protecting reliability or punishing good customers?”

### Key Metrics (Expose to Grafana / Datadog / Prometheus)

- `ratelimit.requests_total{tenant, key, status}` – count of allowed vs. blocked requests per tenant and per key.
- `ratelimit.blocked_ratio{tenant}` – **critical**: blocked requests / total requests. Sudden spikes indicate a noisy integration or a misconfigured limit.
- `ratelimit.remaining_median{tenant}` – median remaining capacity across requests. If it’s always zero for a healthy tenant, your limit is too low.
- `ratelimit.time_until_reset_p99` – helps tune window sizes. High p99 means clients wait too long.

### Logging (Structured, Sampled)

Every `429` should log:
- Tenant ID, API key hash, endpoint, HTTP method
- Whether the key or tenant limit was hit
- Current limit values and client’s `X-RateLimit-Remaining` before the block

**Do not log** full request bodies or authentication secrets in error logs. Sample debug logs at 1% unless hitting a critical threshold (e.g., >10% block ratio).

### Alerts

- **If any tenant exceeds 5% blocked requests over 5 minutes** → investigate. Could be a misconfigured limit or an attack.
- **If platform-wide block ratio exceeds 2%** → critical – rate limits may be too tight or a DDoS is in progress.
- **If any tenant’s rate-limit block ratio drops below 0.01% for 24 hours** → consider raising their limit; they may be underusing capacity.

---

## 6. Recommended Baseline Design

For a multi-tenant API serving teams of 5–500 and enterprises with thousands of integrations, start with this:

- **Algorithm:** Token bucket (capacity = rate * 2 for burst tolerance). Separate buckets for `POST /write` and `GET /read` endpoints.
- **Tiers:**
  - *Free/Small team:* 100 requests/min per key, 5 keys max per tenant.
  - *Enterprise:* 500 requests/min per key, 50 keys max per tenant.
- **Isolation:** Each API key gets its own bucket. A key’s bucket is depleted independently. Tenant-level bucket enforces the aggregate cap.
- **Headers:** Return `X-RateLimit-*` on every response; `Retry-After` only on 429.
- **Observability:** Log every 429, track `blocked_ratio`, alert on >5% for any tenant.
- **Graceful degradation:** When a tenant hits a write limit, slow them down with a 5-second delay before retrying (via `Retry-After`) instead of dropping all requests instantly. For read limits, consider serving stale cached data with a warning header.

**Bottom line:** Rate limits are not a tool for revenue enforcement – they are a tool for operational sanity. Treat them as dynamic, observable contracts between you and your customers. When they work well, neither the small team with a viral webhook nor the enterprise with a buggy batch script can break the platform. When they fail, you’ll see it immediately in your 429 logs – and you’ll know exactly which key to talk to.
````
