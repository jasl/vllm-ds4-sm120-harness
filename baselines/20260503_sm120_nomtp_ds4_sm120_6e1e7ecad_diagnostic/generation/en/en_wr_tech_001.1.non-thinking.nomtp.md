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
- Elapsed seconds: 30.67292
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2118, "completion_tokens": 1966, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 1966
- Total tokens: 2118

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
# Rate Limiting for Multi-Tenant APIs: Balancing Fairness and Reliability

## Introduction

Designing a rate limiting system for a multi-tenant API serving both small teams and enterprise customers is fundamentally different from single-tenant or homogeneous SaaS products. The challenge is not merely throttling requests—it is allocating finite server capacity across tenants with wildly different traffic patterns, business priorities, and fault tolerances. A poorly designed system punishes small teams with unnecessary friction while failing to protect infrastructure from noisy enterprise integrations.

This article covers the architectural principles and practical tradeoffs for backend engineers building such a system.

## 1. Authentication, Authorization, Quotas, and Rate Limits

These four concepts are often conflated, but they serve distinct purposes:

- **Authentication** verifies *who* the client is (e.g., API key, OAuth token). It is a gate: if you cannot authenticate, you receive no response.
- **Authorization** determines *what* the authenticated client is allowed to do (e.g., read vs. write, access to specific endpoints).
- **Quotas** define a *hard cap* on resource usage over a billing or administrative period (e.g., 10,000 requests per month). Exceeding a quota normally blocks further requests until the period resets or the customer upgrades.
- **Rate limits** control *how fast* requests can be made *within* a short time window (e.g., 100 requests per second). They protect infrastructure from traffic spikes, not from gradual overuse.

In a multi-tenant system, quotas are business contracts; rate limits are operational safeguards. A single noisy integration can saturate a database connection pool even if the tenant is within monthly quota—rate limits prevent that.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window

### Fixed Window
The simplest approach: count requests in discrete time slots (e.g., 1-minute windows). A request is accepted if the count for the current window is below the limit.

**Practical drawbacks:** At the boundary between windows, a burst of requests right before midnight and another right after midnight can double throughput relative to the intended limit. This creates “edge-of-window” spikes that are hard to debug and unfair to tenants who follow the rules.

### Sliding Window Log
Maintains a timestamp for each request, and counts requests within a moving window (e.g., last 60 seconds). It is accurate but memory-intensive for high-throughput tenants—storing millions of timestamps in memory is expensive.

### Token Bucket
A bucket holds *tokens* that refill at a fixed rate (e.g., 10 tokens per second). Each request consumes one token. If the bucket is empty, the request is denied.

**Practical advantages:** It naturally bursts: if a tenant is idle for a minute, the bucket fills to capacity, so they can burst up to that capacity in a short burst. Enterprise tenants often have legitimate burst patterns (e.g., syncing after a network outage). Token bucket handles this gracefully without penalizing the rest of the system.

**Recommendation for multi-tenant APIs:** Use a **token bucket with per-tenant keys**. Scale the bucket capacity and refill rate by tenant tier (small team: 50 tokens/s, enterprise: 500 tokens/s). Keep the bucket size equal to the refill rate to avoid unbounded bursts.

## 3. Avoiding Global Tenant Punishment for One Noisy Integration

The most common mistake is applying a single global rate limit per tenant. A single noisy integration (e.g., a misconfigured polling script) can exhaust the tenant’s entire budget, blocking their legitimate traffic.

### Key design patterns:

- **Per-key or per-client limits:** Within a tenant, issue different API keys for different integrations or services. Apply separate rate limits per key. This ensures that one misbehaving script only blocks itself, not the tenant’s user-facing application.
- **Hierarchical limits:** A tenant has a top-level limit (e.g., 500 requests/s), and each key has a sub-limit (e.g., 50 requests/s). A key that exceeds its sub-limit is throttled; other keys within the same tenant continue normally. The top-level limit still protects infrastructure: if the sum of all keys exceeds 500 requests/s, the excess is blocked regardless.
- **Dynamic pools:** For enterprise tenants, allocate a reserved capacity pool (e.g., a fixed number of concurrent request slots). A noisy integration consumes its own share of that pool and cannot starve other integrations within the same tenant.

### Implementation consideration:
Store per-key limits in a shared cache (e.g., Redis with TTL) with key structure like `rate_limit:{tenant_id}:{key_id}`. The hierarchical limit check is a two-step read: first check the key-level bucket, then the tenant-level bucket. If either is empty, reject.

## 4. Headers and Error Messages

Clients must receive clear, actionable feedback. Minimal headers:

- `X-RateLimit-Limit`: the maximum request rate for the client’s tier (e.g., 500).
- `X-RateLimit-Remaining`: how many requests the client can still make in the current window or bucket.
- `X-RateLimit-Reset`: Unix timestamp (or seconds) when the rate limit will reset / bucket will refill.

For multi-tenant systems, **always identify which limit was hit**:
- If a per-key limit is hit, return `429 Too Many Requests` with a JSON body:
  ```json
  {
    "error": "rate_limit_exceeded",
    "detail": "Key-level rate limit exceeded. Retry after 12 seconds.",
    "scope": "api_key",
    "retry_after_seconds": 12
  }
  ```
- If a tenant-level limit is hit:
  ```json
  {
    "error": "rate_limit_exceeded",
    "detail": "Team-level rate limit exceeded. Other keys for this team are unaffected.",
    "scope": "tenant",
    "retry_after_seconds": 15
  }
  ```

This transparency prevents confusion: a client knows whether the problem is on their key or the entire tenant. Without scope information, support teams waste time escalating false positives.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting exists to protect reliability, but it must not silently block legitimate use. Observability is the feedback loop that validates your thresholds.

### Metrics (captured at the middleware layer):
- `rate_limit_requests_total`: tagged by `tenant_id`, `key_id`, `status` (allowed vs. blocked), and `scope` (key vs. tenant).
- `rate_limit_current_usage_gauge`: current bucket fill level per tenant or per key. Allows dashboards showing how close each tenant is to the limit.
- `rate_limit_throttle_duration_seconds`: how long blocked requests are told to wait. High values indicate a tenant is persistently over limit.

### Logs:
- Log every rate-limit enforcement event with tenant ID, key ID, resource path, and reason (key over limit, tenant over limit). Include the `retry_after` value.
- For allowed requests, log aggregate counters but not individual events—high-cardinality logging is expensive. Use sampled logs (1 in 1000) for allowed requests to detect anomalies.

### Alerts:
- **Critical alert:** Total blocked requests > 1% of all requests for any enterprise tenant for 5 minutes. This may indicate a misconfiguration or an attack.
- **Warning alert:** A single tenant’s throttle rate (blocked / total) exceeds 10% for 10 minutes. Investigate whether a noisy integration is causing collateral damage.
- **Health check:** The rate limit system itself must be monitored for latency and availability. If the cache backing the token bucket goes down, fall back to a local sliding-window approximation (less accurate but better than no limiting) and alert.

## Recommended Baseline Design

For a production multi-tenant API serving teams and enterprises:

1. **Authentication → Authorization → Rate Limiting** as a middleware chain. Rate limiting runs after authentication (to identify the tenant) but before the request handler.
2. **Token bucket per tenant key** with two tiers: key-level and tenant-level. Bucket capacity = refill rate. For enterprises, a separate burst pool (e.g., double the refill rate) to handle legitimate spikes.
3. **Store buckets in a distributed cache** with TTL equal to the refill period. Use atomic operations (e.g., `DECR` with check) to avoid race conditions.
4. **Return `X-RateLimit-*` headers and a JSON body** with `scope` and `retry_after` on 429 responses. Never return a 503 or generic error.
5. **Alert when a single key accounts for >80% of a tenant’s throttled requests**—this is the canonical sign of a noisy integration that should be isolated at the key level.
6. **Start conservative:** Under-allocate limits by 20% of estimated capacity. Monitor the `throttle_duration` metric. Increase limits only after observing that the system handles the current load without saturation.

Rate limiting is not a set-and-forget feature. It requires ongoing tuning based on real traffic patterns. The design above gives you the levers to adjust fairness without sacrificing reliability.
````
