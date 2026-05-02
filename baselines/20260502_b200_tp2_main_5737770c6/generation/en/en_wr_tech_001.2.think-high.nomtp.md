# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 16.595339
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2196, "completion_tokens": 2044, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2044
- Total tokens: 2196

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
# Designing Rate Limits for Multi-Tenant API Backends: Balancing Team Turbos and Enterprise Tanks

## 1. Clearing the Fog: Auth, Authorization, Quotas, and Rate Limits

Before designing any limiter, every engineer must internalize four distinct concepts that teams routinely conflate:

- **Authentication** – *Who are you?* Verifies identity via API keys, OAuth tokens, or mTLS. A gateway authenticates every request before any further processing.
- **Authorization** – *What are you allowed to do?* Determines access to specific endpoints, resources, or operations (e.g., read vs. write scopes). Usually evaluated after authentication.
- **Quota** – *How much total work are you allowed over a long period?* A quota is an absolute cap on usage per billing cycle or per day. Exceeding a quota blocks further requests until the window resets or the tenant upgrades. Example: 10,000 API calls per month.
- **Rate Limit** – *How fast are you allowed to work?* A rate limit throttles short-term burstiness to protect system resources. It answers: “Can you send this request *right now*?” Example: 100 requests per second.

**Why this matters for multi-tenant design:** Small teams often burst hard but have low total usage; enterprises have high total usage but expect predictable latency. Rate limits protect reliability; quotas protect revenue and fair resource allocation. Use both, but never confuse them.

## 2. Algorithm Shootout: Token Bucket, Fixed Window, Sliding Window

Each algorithm trades off between accuracy, memory, and operational complexity. Here is the practical truth:

### Fixed Window
- **Mechanism:** Count requests in a 1-second (or 1-minute) bucket. Reset bucket every interval.
- **Pitfall:** At the edge of two windows, a client can send double the allowed rate in a short burst (e.g., 100 requests at second 0.999, then 100 requests at second 1.001 = 200 requests in 2 ms).
- **Best for:** Coarse per-tenant limits where occasional bursts are acceptable. Very cheap to implement with Redis TTL counters.

### Sliding Window (Log or Counter)
- **Mechanism:** Maintain a timestamped log of recent requests, or use a moving counter by weighting overlapping windows.
- **Pitfall:** Sliding window logs consume memory proportional to request rate. Sliding window counters (e.g., Redis sorted sets) require O(log n) operations per request.
- **Best for:** Enterprise tenants who demand strict, fair throttling. Avoids the double-burst issue entirely.

### Token Bucket
- **Mechanism:** A bucket holds tokens refilled at a fixed rate (e.g., 100 tokens/sec). Each request consumes one token. If bucket is empty, request is denied. Bursts are allowed up to bucket capacity.
- **Pitfall:** Long idle periods accumulate full capacity → a sudden burst of 100 requests is allowed, then back to steady state. For very low capacity buckets, this can still overwhelm.
- **Best for:** APIs where occasional natural bursts are acceptable (e.g., batch imports, search indexing). Most intuitive model: “You get X tokens per second, with a Y token burst.”

**Recommendation:** Use **Token Bucket per tenant + per API key** for most multi-tenant backends. It handles bursts gracefully and maps to user mental models. Fall back to sliding window for premium enterprise tiers that pay for exact fairness.

## 3. Avoiding Tenant-Level Punishment from a Noisy Integration

One misbehaving webhook client inside a large enterprise tenant should not throttle the entire tenant’s engineering team. Two isolation strategies:

### A. Per-API-Key (or Per-Integration) Limits
- Assign each API key its own rate limit bucket. A noisy webhook key exhausts only its own tokens.
- **Hard part:** An enterprise might have 50 keys; the system must store and check 50 independent token buckets per second. Use Redis hashes with keyed TTLs, not one monolithic counter.

### B. Hierarchical Limits
- **Level 1:** Per-key limit (e.g., 50 req/s per API key).
- **Level 2:** Tenant aggregate limit (e.g., 1000 req/s across all keys).
- **Behavior:** A noisy key hits its own limit first; if it still consumes tenant capacity, the tenant-level bucket drains. The other keys remain unblocked until the tenant bucket is empty.
- **Implementation:** Check per-key bucket first. Deduct from tenant bucket second. Reject if either is empty. Requires two atomic operations per request—acceptable with Redis Lua scripting.

**Critical rule:** Never allow one key to consume 100% of tenant capacity unless the tenant has explicitly configured it. Default to “per-key limits protect tenant from one bad actor.”

## 4. Headers and Error Messages: The Client Developer’s Compass

Returning the right headers reduces support tickets and client frustration. Adopt the **HTTP RateLimit standard** (draft) or build this minimal set:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 47
X-RateLimit-Reset: 1712345678
Retry-After: 3
```

- `X-RateLimit-Limit`: The maximum requests allowed in the current window.
- `X-RateLimit-Remaining`: How many requests left before hitting the limit.
- `X-RateLimit-Reset`: Unix timestamp when the bucket refills or window resets.
- `Retry-After`: Seconds the client must wait (only sent on 429).

**Error body (429 Too Many Requests):**
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "API rate limit exceeded. You have sent 100 requests in 60 seconds.",
    "retry_after_seconds": 3,
    "type": "per_key"
  }
}
```
- `type` tells the client if this is a per-key, per-tenant, or per-endpoint limit. Log this server-side for debugging.

**Important:** Never return `403 Forbidden` for rate limits. 403 means authorization failure—confuse clients and they’ll waste time debugging permissions.

## 5. Observability: Are Limits Protecting or Punishing?

Without instrumentation, you’re flying blind. Monitor these three categories:

### Metrics (use counters, histograms, and gauges)
- **Per-tenant throttle rate:** Requests rejected vs. accepted (should be < 5% in healthy system).
- **Token bucket fill level:** Gauge showing how close tenants are to limit (alarm at 95% avg over 1 minute).
- **Per-key remaining distribution:** Histogram of `X-RateLimit-Remaining` values. If most requests see <10 tokens left, limits are too tight.
- **Latency impact:** P99 latency for requests just before vs. just after a bucket refill. Spikes indicate your rate limit check is a bottleneck.

### Logs (structured, sampled)
- Log only **throttled requests** at WARN level (not every request—that’s expensive).
- Include `tenant_id`, `api_key_suffix`, `limit_type`, `remaining`, `latency_ms_of_check`.
- Sample 1% of accepted requests at INFO level to track “near-miss” scenarios (remaining < 5).

### Alerts (actionable, not noisy)
- **Alert: “Per-tenant throttle rate > 10% for 5 minutes”** → Investigate if a tenant’s usage pattern changed or if your limits are misconfigured.
- **Alert: “Rate limit check latency > 50ms P99”** → Your Redis cluster is overloaded. Scale read replicas or batch limit checks.
- **Alert: “No throttling ever on any tenant”** → Limits are set too high; you are not protecting reliability. Tighter limits needed.
- **Dashboard: “Top 5 tenants by throttle count”** → Shows which tenants need capacity planning discussions.

## 6. Recommended Baseline Design

For a backend serving small teams and enterprise customers, start here:

1. **Algorithm:** Per-key Token Bucket (capacity = 2× refill rate) + hierarchical Tenant Token Bucket (capacity = 4× enterprise refill rate). Use Redis Lua scripts for atomic updates.
2. **Tiers:**
   - Small team: 100 req/min per key, 500 req/min tenant aggregate.
   - Enterprise: 1000 req/min per key, 10,000 req/min tenant aggregate.
3. **Headers:** Always return `X-RateLimit-*` and `Retry-After`. Return `type: "per_key"` or `type: "tenant"` in 429 body.
4. **Isolation:** Never share a token bucket across API keys. Document that each integration needs its own key.
5. **Observability:** Emit metrics to Prometheus (or equivalent). Log 429s with tenant and key prefix. Alert on throttle rate > 10% over 5 minutes.
6. **Fallback:** If Redis is unreachable, allow requests through (fail open) but log a critical alert. Cache last-known limits in-memory with a 10-second TTL to handle brief blips.

**Final note:** Rate limiting is a *negotiation* with clients, not a wall. Good limits feel like a firm but fair bouncer. Bad limits feel like a locked door with no sign. Your headers, error messages, and observability are that sign—write them clearly.
````
