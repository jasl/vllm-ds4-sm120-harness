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
- Elapsed seconds: 36.748723
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2503, "completion_tokens": 2351, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2351
- Total tokens: 2503

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
# Rate Limiting for Multi-Tenant APIs: Balancing Protection and Fairness Across Small Teams and Enterprises

## 1. Foundational Concepts: Authentication, Authorization, Quotas, and Rate Limits

Before designing any rate-limiting system, we must disambiguate four distinct but often conflated concepts:

- **Authentication** answers "Who are you?" – verifying identity via API keys, OAuth tokens, or mTLS certificates. It is a prerequisite for all subsequent checks.
- **Authorization** answers "What are you allowed to do?" – controlling access to specific resources or actions (e.g., "Can this tenant read financial reports?"). Authorization does not constrain *how many* requests.
- **Quotas** are long-term capacity entitlements, typically measured over a billing cycle (e.g., 100,000 API calls per month). They govern *total usage* and are often enforced via periodic resets. Quotas are contractual; exceeding them usually results in billing overage or feature degradation.
- **Rate limits** are short-term *velocity* controls, measured in requests per second, minute, or hour. They protect infrastructure from traffic spikes, prevent abuse, and ensure system stability. Unlike quotas, rate limits reset quickly and are about *instantaneous load*, not cumulative usage.

The critical insight: **authentication occurs first, then authorization, then rate limiting, then quota enforcement.** Rate limiting should never be a substitute for authorization, and quotas should never be used to prevent a DDoS. They are complementary layers.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window: Practical Trade-offs

### Fixed Window
Divide time into discrete buckets (e.g., 60-second windows). Count requests per window. When the counter hits the limit, reject further requests until the next window.

- **Pros**: Extremely simple to implement and reason about; low memory overhead (one counter per key).
- **Cons**: **The "burst at the edge" problem.** If a tenant sends 100 requests at the last millisecond of window N, then 100 more at the first millisecond of window N+1, they delivered 200 requests in two milliseconds—effectively doubling allowed throughput. This is catastrophic for downstream services.
- **Best for**: Mock or debugging endpoints where precision is irrelevant.

### Sliding Window Log
Maintain a sorted list of timestamps for each tenant. Every request adds a timestamp and removes timestamps older than the window duration. If the list size exceeds the limit, reject.

- **Pros**: Smooth, exact enforcement—no edge bursts.
- **Cons**: Memory and time complexity O(n) per request in naive implementations. Even with binary search and pruning, large tenants with high throughput force pathological storage growth.
- **Best for**: Low-traffic APIs or tenants with very small limits.

### Sliding Window Counter
A hybrid approach: track the current window's count and the previous window's count. Estimate the rate at any point as:
`previous_count * (1 - elapsed_fraction) + current_count`.
Reject if the estimate exceeds the limit.

- **Pros**: Low memory (two counters per key), O(1) per request, eliminates the edge burst problem (within reasonable approximation).
- **Cons**: Not exact—a burst exactly at a window boundary can exceed the limit by up to one request. Usually acceptable.
- **Best for**: General-purpose production systems requiring both accuracy and efficiency.

### Token Bucket
Maintain a bucket of capacity tokens that refill at a constant rate (e.g., 10 tokens per second). Each request consumes one token. If the bucket is empty, reject.

- **Pros**: Smooth rate enforcement; allows natural bursts up to bucket depth (e.g., 100 tokens permits a 100-request burst at T=0). Simple to reason about with traffic shaping.
- **Cons**: Requires careful configuration of bucket depth and refill rate. If depth is too large, one noisy tenant can still overwhelm shared resources.
- **Best for**: APIs where controlled bursting is a feature (e.g., webhook callbacks) or where traffic patterns are irregular.

**Practical recommendation**: Use **sliding window counter** for most endpoints—it is a pragmatic compromise. Use **token bucket** only for specific "burst-friendly" endpoints (e.g., batch POST endpoints) where you explicitly want to allow spikes drawn from a credit bank.

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

A multi-tenant API serves thousands of integrations within a single tenant: third-party webhooks, internal services, cron jobs, developer tools, etc. If rate limits are applied exclusively at the tenant level, a single misconfigured script can saturate the entire tenant's allowance—blocking billing, reporting, and critical customer workflows.

**Solution: Hierarchical rate limiting with shared and per-integration buckets.**

- **Per-tenant global limit** (e.g., 100 req/s): enforced at a coarse granularity using a sliding window counter. This protects your infrastructure.
- **Per-integration sub-limit** (e.g., 20 req/s per API key or per application identifier): enforced using the same algorithm but keyed by a finer identifier (e.g., API key hash + path prefix). This isolates noisy actors.
- **Hierarchical admission**: Allow a request only if *both* the per-integration bucket and the per-tenant bucket have capacity. This ensures no single integration can exhaust the tenant's global allocation, while still capping total tenant load.

Additionally, implement **minimum guaranteed capacity** for critical endpoints (e.g., billing, health checks). Reserve a small "emergency quota" at the tenant level that bypasses per-integration limits—but never at the infrastructure level.

**Example scenario**: Tenant A has 10 integrations, each independently limited to 10 req/s. Integration X goes rogue and hits 10 req/s continuously. Integration Y can still operate at its own 10 req/s because per-integration limits are independent. However, if 50 integrations all reach 10 req/s simultaneously, the per-tenant limit of 100 req/s will block them—protecting your backend from 500 req/s.

## 4. Headers and Error Messages to Return

Clear, standardised feedback is essential for client-side developers to handle throttling gracefully. Use HTTP headers consistent with the IETF standard (RFC 6585) and common industry practices:

### Response Headers (on every request)
- `X-RateLimit-Limit`: The maximum number of requests allowed per window (e.g., `100`).
- `X-RateLimit-Remaining`: The number of requests remaining in the current window (e.g., `87`).
- `X-RateLimit-Reset`: The UTC epoch time (seconds) when the current window resets. Helps clients compute backoff precisely.

### When Rejected (HTTP 429 Too Many Requests)
- `Retry-After`: Seconds the client should wait before retrying (e.g., `3`). Use an integer; do not return fractional seconds.

### Error Body (JSON)
Return a consistent structure:
```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit. Please retry after the specified time.",
  "retry_after_seconds": 3,
  "limit": 100,
  "remaining": 0,
  "reset_at": 1699826400
}
```

**Crucial detail**: For multi-tenant isolation, include which scope was exceeded (`tenant` vs `integration`) in the error body:
```json
"scope": "integration",
"integration_id": "key-abc123"
```
This avoids confusion when a tenant's global limit has capacity but their individual key is blocked.

Do **not** return stack traces, internal configuration details, or "credit" information that reveals your underlying algorithm. Keep the interface stable even if you change the implementation.

## 5. Observability: Metrics, Logs, and Alerts

Rate limits are only useful if you know they are working as intended. Observability must answer: *Are we rejecting legitimate traffic? Are we protecting downstream services?*

### Key Metrics (exposed via your monitoring platform)
- **`rate_limit.hits{scope="tenant", decision="allowed"}`**: Count all accepted requests, tagged by tenant tier, integration ID, and endpoint.
- **`rate_limit.hits{scope="integration", decision="rejected"}`**: Count rejected requests per integration. Spike = noisy actor.
- **`rate_limit.hits{scope="tenant", decision="rejected"}`**: Count tenant-level rejections. This should be rare; a spike indicates a badly distributed sub-limit configuration.
- **`downstream.latency_p99`**: Critical—if latency increases while rejection rates are low, your rate limits may be too generous.
- **`rate_limit.bucket_depth_remaining`**: Track average remaining capacity per tenant over time. Persistent near-zero values suggest you are operating at the edge of capacity.

### Logs
Log every rate-limited request with structured fields: `tenant_id`, `integration_id`, `route`, `limit_type` (tenant vs. integration), `limit_value`, `retry_after`. Do not log successful requests by default to avoid explosion.

### Alerts
- **P1**: Rate limit rejections exceed 5% of all requests for 5 minutes → indicates either an attack or misconfigured limits.
- **P2**: Any single tenant is responsible for >50% of all rejections → investigate for runaway integration.
- **P3**: Average `retry_after` for rejected requests exceeds 30 seconds → clients are retrying too aggressively; check your `Retry-After` accuracy.
- **P4**: Per-integration rejections persistently account for >90% of all rejections → your per-integration limits may be too aggressive; consider raising them.

## Recommended Baseline Design

For a mid-scale multi-tenant API (10,000 tenants, mixed small teams and enterprise), implement:

1. **Algorithm**: Sliding window counter for both tenant and integration limits. Use a fast in-memory store (e.g., sharded in-process map or external cache) for low-latency decision-making.
2. **Hierarchy**:
   - Tenant global limit: 5x the sum of per-integration limits to allow some natural headroom.
   - Per-integration limit: 20% of tenant global limit, with a minimum floor of 5 req/s.
3. **Capacity reservation**: Reserve 10% of tenant capacity for a priority endpoint (e.g., `/health`, `/billing`). This is implemented as a second per-tenant bucket that is checked before the general bucket, with its own sub-limit.
4. **Headers**: Include all three `X-RateLimit-*` headers plus `Retry-After` on 429s. Return JSON error bodies with `scope` field.
5. **Observability**: Emit metrics for allowed/rejected counts at both scopes, track downstream latency, and alert on rejection rate >5% or single-tenant domination.

This baseline avoids punishing entire tenants for one noisy integration while providing sharp visibility into traffic patterns. Adjust limits based on actual observed capacity planning data—not theoretical maxima.
````
