# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 31.130115
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2147, "completion_tokens": 1995, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 1995
- Total tokens: 2147

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
# The Four-Layer Cake of API Governance: Designing Rate Limits for Multi-Tenant Systems

## 1. Authentication, Authorization, Quotas, and Rate Limits – The Critical Distinction

Before designing any rate limiting scheme, you must internalize the difference between four concepts that engineers frequently conflate:

- **Authentication** answers *"Who are you?"* – verifying identity via API keys, OAuth tokens, or mTLS certificates.
- **Authorization** answers *"What are you allowed to do?"* – checking permissions, scopes, and roles after identity is established.
- **Quotas** answer *"How much can you use over a long period?"* – a hard ceiling on total usage (e.g., 10,000 requests per month) enforced at billing boundaries. Quotas are soft limits until exceeded; then they become hard blocks.
- **Rate Limits** answer *"How fast can you use it right now?"* – a per-second or per-minute cap to protect infrastructure from traffic spikes, regardless of remaining quota.

The critical insight: **rate limits protect reliability; quotas protect revenue.** A tenant with 99% of their monthly quota remaining can still be rate-limited to 100 requests per second. Conversely, a tenant with zero quota should be rejected even if they are below the rate limit.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window – Practical Tradeoffs

### Fixed Window
Simplest to implement: count requests in discrete clock-aligned windows (e.g., every minute: 00:00–00:59, 01:00–01:59).
**Problem:** Traffic bursts at window boundaries. If a tenant sends 100 requests at 00:59 and another 100 at 01:00, the actual spike is 200 requests in two seconds, but each window sees only 100. This punishes legitimate neighbors during "edge collisions."

### Sliding Window Log
Tracks timestamps of every request. When a new request arrives, it removes timestamps older than the window and checks the count.
**Pros:** Smooth, precise.
**Cons:** Memory-intensive for high-traffic tenants; O(n) cleanup per request. Not practical at enterprise scale without a sliding window counter approach.

### Sliding Window Counter
Compromises between fixed and log: keeps a counter for the current clock window and a fractional weight for the overlap with the previous window.
**Tradeoff:** ~5% drift from perfect accuracy, but O(1) operations. Acceptable for most API use cases.

### Token Bucket
The most burst-friendly algorithm. A bucket holds N tokens, refilling at R tokens/second. Each request consumes one token. If the bucket is empty, the request is denied.
**Why it wins for multi-tenant APIs:**
- Natural burst absorption (idle tenants accumulate tokens)
- No edge collisions
- Easy to implement via Redis with `SET` + `TTL` for per-tenant buckets
**Cost:** Requires careful refill rate choice—too slow and small teams fail; too fast and bursts overwhelm the backend.

**Recommendation:** Use Token Bucket for throughput-sensitive endpoints (e.g., write operations) and Sliding Window Counter for read-heavy, low-latency endpoints where burst tolerance is lower priority.

## 3. Don’t Punish the Whole Tenant for One Noisy Integration

Enterprise tenants often have dozens of integrations—some well-behaved, some not. Blocking the entire tenant when one integration floods is a design failure.

**Solution: Two-Level Rate Limiting**

1. **Tenant-level limit:** Total requests per second across all API keys belonging to that tenant. This protects infrastructure from aggregate load.
2. **Integration-level limit (or API key-level limit):** One tenth (or one fifth) of the tenant limit per individual API key.

When integration A spikes:
- Integration A hits its per-key limit and receives 429s.
- Integration B (well-behaved) continues unaffected under the tenant-level ceiling.
- If integration A’s volume is small relative to the tenant limit, it may only breach its own key limit without ever touching the tenant ceiling.

**Critical design rule:** The sum of all per-key limits should exceed the tenant limit. This prevents a situation where every key can independently hit its cap and collectively exceed infrastructure capacity. For example: if tenant limit is 1000 req/s, set per-key limit to 400 req/s. Even with three noisy keys (1200 req/s), the tenant-level guardrail will block the excess.

## 4. Headers and Error Messages – The Engineering Contract

Clients must be told *why* they were limited and *when* they can retry. Return the following headers on every response:

```
X-RateLimit-Limit: 1000              # Tenant-level limit per window
X-RateLimit-Remaining: 235           # Remaining requests in this window
X-RateLimit-Reset: 1704067200        # Unix timestamp when limit resets
Retry-After: 30                      # Seconds to wait (for 429 responses)
```

For 429 errors, the body should return a structured JSON object:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Request rate exceeds the allowed limit for your tenant. Please reduce your request rate or contact support to increase your limit.",
  "retry_after_seconds": 30,
  "limits_applied": [
    {
      "scope": "tenant",
      "name": "requests_per_second",
      "limit": 1000,
      "remaining": 0,
      "reset_at": 1704067200
    }
  ]
}
```

**Differentiate from authorization errors:**
- 401 Unauthorized → bad authentication
- 403 Forbidden → valid auth but insufficient permissions
- 429 Too Many Requests → valid auth, valid permissions, but too fast

Never return 429 for authentication or authorization failures—that leaks information about valid API keys and confuses clients.

## 5. Observability – Proving the System Works Without Blocking Legitimate Use

Rate limiting becomes a black hole of developer frustration if you cannot answer: *"Was the 429 legitimate, or did your stupid algorithm break my deployment?"*

### Metrics (for dashboards)
- **`rate_limit.requests_total`** by tenant tier, API key, endpoint, and HTTP method
- **`rate_limit.requests_blocked_total`** by reason (tenant limit, per-key limit)
- **`rate_limit.current_utilization`** – histogram of how close tenants are to their limit (95th, 99th percentile)
- **`rate_limit.bucket_fullness`** – for token bucket, current token count as a fraction of capacity
- **`rate_limit.retry_after_distribution`** – to detect clients aggressively retrying after 30 seconds

### Logs (for debugging)
Every 429 must produce a structured log with:
- tenant_id, api_key_id, endpoint, timestamp, retry_after, limit_type
- request IP (for spotting distributed attacks from a single tenant)
- current tenant-level and per-key utilization at the moment of rejection

### Alerts (for operational sanity)
- **Pager (high urgency):** `rate_limit.requests_blocked_total` for the entire system increases >200% in 5 minutes (possible DDoS or batching failure)
- **Dashboard (medium):** Any single tenant hits their limit more than 10 times in an hour (possible misconfigured client, flag for support outreach)
- **Report (weekly):** Top 10 blocked requests by tenant – filter out known bad actors, investigate unknowns

### The “False Positive” Signal
Track `rate_limit.server_error_429` – requests that were blocked but, when replayed manually, succeed. If this exceeds 0.1% of all 429s, your rate limit algorithm has a bug (e.g., clock skew, stale counters, inconsistent bucket refill rates).

## 6. Recommended Baseline Design

For a multi-tenant API supporting teams of 5 to enterprises with thousands of employees, start here:

- **Algorithm:** Token Bucket with a 5-second refill window (burst capacity = 1.5x steady-state limit)
- **Limits:**
  - Small teams: 100 req/s tenant, 40 req/s per API key
  - Mid-tier: 500 req/s tenant, 150 req/s per API key
  - Enterprise: 2000 req/s tenant, 600 req/s per API key, custom config negotiable
- **Implementation:** In-memory with Redis backend for distributed workers; TTL on bucket keys (e.g., 60 seconds idle eviction)
- **Headers:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`
- **Fail-open behavior:** If Redis is unreachable, allow requests (set a circuit breaker: 5 seconds of failures → permit all until Redis recovers)
- **Observability:** Prometheus metrics + structured JSON logging + weekly false-positive review

This design balances fairness (per-key isolation), predictability (token bucket burst absorption), and debuggability (clear headers and logs). Adjust the refill rate and bursting ratio based on your backend’s actual latency at P99 CPU—measure, don’t guess.
````
