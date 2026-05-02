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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.561831
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2276, "completion_tokens": 2124, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2124
- Total tokens: 2276

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
# Designing Rate Limiting for a Multi-Tenant API: Balancing Small Teams and Enterprise Needs

## 1. Foundational Concepts: Authentication, Authorization, Quotas, and Rate Limits

Before designing a rate limiting system, it is critical to distinguish between four often-confused concepts.

- **Authentication** confirms *who* the caller is (e.g., via API keys, OAuth tokens).
- **Authorization** determines *what* the caller is allowed to do (e.g., read vs. write access, resource scopes).
- **Quotas** define *how much* a tenant can consume over a long period (e.g., 10,000 requests per month, 100 GB of storage). Quotas are billing or contract boundaries, not real-time protections.
- **Rate limits** control *how fast* requests arrive (e.g., 100 requests per second). Their purpose is to protect system stability, not to enforce long-term consumption.

A multi-tenant API must apply all four, but rate limiting is unique because it must react in milliseconds, not hours or days.

## 2. Algorithm Comparison: Token Bucket, Fixed Window, and Sliding Window

### Fixed Window
The simplest model: count requests per tenant in a discrete time window (e.g., one minute). At the start of each minute, the counter resets.
**Pros**: Very low memory and CPU overhead. Easy to reason about.
**Cons**: Burst behavior at window boundaries. If a tenant sends 100 requests at 00:59 and 100 requests at 01:00, they effectively get 200 requests in two seconds. This defeats the purpose of rate limiting for reliability.

### Sliding Window
Instead of resetting at hard boundaries, the sliding window tracks request timestamps over a rolling period (e.g., the last 60 seconds).
**Pros**: Eliminates boundary bursts. Accurate reflection of recent traffic.
**Cons**: Higher memory cost (must store timestamps or a log of recent requests). Implementation complexity increases for high-throughput tenants.

### Token Bucket
The token bucket maintains a bucket of N tokens that refill at a steady rate (e.g., 100 tokens per second). Each request consumes one token. Unused tokens accumulate up to a burst capacity.
**Pros**: Naturally allows bursts within constraints. No window-boundary anomalies. Stateless-friendly if tokens are stored in a distributed cache with TTL.
**Cons**: Burst capacity must be set carefully—too high and it defeats protection; too low and it penalizes legitimate spikes.

**Practical recommendation for multi-tenant**: Use a token bucket per tenant, with a burst capacity equal to the allowed rate per second multiplied by a small factor (e.g., 2x). This handles typical request patterns (e.g., a team’s CI/CD pipeline firing 50 requests on deploy) without risking system overload.

## 3. Avoiding Collective Punishment: Per-Integration and Hierarchical Limits

A common mistake is to apply a single rate limit per tenant. If one noisy integration (e.g., a misconfigured webhook or a buggy client) exhausts the tenant’s bucket, *all* other integrations under that tenant—including your own dashboard—are blocked. This is unacceptable for enterprise customers who run dozens of microservices against your API.

### Design Principles

- **Per-credential rate limits**: Assign a unique API key to each integration, not to the tenant as a whole. Each key gets its own token bucket. The tenant’s total capacity is the sum of all key-level buckets, but a single key cannot starve the others.
- **Hierarchical limits**: Implement a two-tier system. Each key has a per-key bucket (e.g., 50 req/s). The tenant also has a global bucket (e.g., 500 req/s). A request is allowed only if both the key bucket and tenant bucket have tokens. This prevents a single misbehaving key from taking the tenant over its agreed ceiling, while still containing the impact within that key.
- **Dead-lettering for client errors**: If a key sends malformed requests, increase its backoff multiplier (through a per-key penalty factor) rather than consuming tenant tokens. A simple mechanism: detach the key’s bucket from the tenant’s bucket after N consecutive 4xx responses, redirecting its traffic to a slow queue.

## 4. Client-Facing Headers and Error Messages

Clients must be able to introspect their limits and back off intelligently. Return the following headers on every response:

- **`X-RateLimit-Limit`**: The maximum allowed requests per time window (e.g., per second or per minute). Should be the tenant’s global cap, not the key’s, so the client knows the boundary.
- **`X-RateLimit-Remaining`**: Tokens remaining at the moment the request was processed. For hierarchical limits, report the *minimum* remaining (i.e., the bottleneck).
- **`X-RateLimit-Reset`**: The Unix timestamp when the current bucket will reset (for token bucket, the time when tokens will refill to burst capacity; for window-based, the end of the window). Alternatively, use a `Retry-After` header in seconds for simplicity.

### Error Response Body

When a request is rejected with `429 Too Many Requests`, return a JSON body with:

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit for this API key. Please wait and retry.",
  "retry_after_seconds": 15,
  "detail": {
    "limit_type": "key",
    "limit": 50,
    "remaining": 0,
    "reset_at": "2025-04-11T12:00:30Z"
  }
}
```

The `detail` object helps client developers debug which limit was hit. Do *not* expose tenant-level limits in error messages for security reasons—enterprise customers may not want their internal team members to see global caps.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting should be transparent to operators. Instrument the following:

### Metrics (label or tag with tenant_id, key_id, and limit_tier)

- `rate_limit_allowed_total` – requests that passed all checks.
- `rate_limit_denied_total` – requests rejected by any tier, with a `reason` label (key_exceeded, tenant_exceeded, malformed).
- `rate_limit_remaining` – gauge of current remaining tokens per key and per tenant (sampled every few seconds, not per request).
- `rate_limit_token_refill_rate` – actual refill rate observed per tenant; helps detect misconfigurations.
- `requests_before_rate_limit` – latency percentiles for requests that were rate-limited (high p99 here may indicate the rate limiter itself is slowing down legitimate traffic).

### Logs

Log *only* rate-limited requests and unusual events (e.g., a tenant hitting 90% of its limit for >5 minutes). Avoid logging every allowed request. Include:
- Tenant ID, key ID, endpoint, HTTP method, and whether the limit was key or tenant tier.
- Current limit window timestamp (for correlation).
- Agent or user-agent string (to identify noisy clients).

### Alerts

- **High denial rate**: If `rate_limit_denied_total / rate_limit_allowed_total` exceeds a threshold (e.g., 5%) for a tenant, alert—this may indicate a misconfigured client or an attack.
- **Near-limit drift**: If a tenant consistently stays at 95% of its limit for >10 minutes, alert as a potential capacity planning issue.
- **Rate limiter latency**: If p99 of the rate limiting check exceeds 5ms, the implementation may be too slow (e.g., using a slow database instead of in-memory or Redis).

## 6. Recommended Baseline Design

Here is a concrete architecture that balances simplicity, fairness, and observability for multi-tenant APIs serving teams and enterprises.

### Limit Structure

- **Per API key**: Token bucket with rate = 50 req/s, burst = 100.
- **Per tenant (aggregate of all keys)**: Token bucket with rate = 500 req/s, burst = 1,000.
- **Soft cap**: When tenant-level tokens fall below 10%, return a `Warning` header: `299 "approaching rate limit"`.

### Request Path

1. Extract API key from `Authorization` header.
2. Look up key metadata (tenant ID, key-level bucket state) from a fast distributed cache (e.g., Redis with TTL of a few seconds).
3. Try to consume one token from both the key bucket and tenant bucket atomically.
4. If either bucket is empty, return 429 with `Retry-After` calculated from the bucket that would refill latest.
5. If both succeed, attach the three rate-limit headers and forward the request to the backend.

### Observability Stack

- Export metrics to Prometheus via a sidecar or middleware.
- Ship structured logs (JSON) with only rate-limited events to a central log aggregator.
- Set up two critical alerts: (a) denial rate > 5% for any tenant, (b) rate limiter response time > 5ms for more than 1% of requests.

### What This Design Achieves

- **No tenant-wide blackout**: A noisy key exhausts its own bucket, leaving other keys under the same tenant untouched.
- **Burst-friendly**: Token bucket handles legitimate spikes (e.g., team deploys).
- **Observable**: Metrics and alerts prevent silent failures.
- **Simple for clients**: Standard headers, clear error messages, and a `Retry-After` that a well-behaved client can follow without guessing.

Rate limiting is not merely a gate; it is a contract. A well-designed system protects your infrastructure while enabling the small team and the enterprise customer alike to use your API confidently.
````
