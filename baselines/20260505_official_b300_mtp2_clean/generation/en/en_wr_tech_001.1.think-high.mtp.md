# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 13.117071
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2375, "completion_tokens": 2223, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2223
- Total tokens: 2375

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

## 1. Foundational Concepts: Authentication vs. Authorization vs. Quotas vs. Rate Limits

Before designing a rate-limiting system, we must disambiguate four concepts that engineers often conflate.

**Authentication** is the act of verifying *who* a client is—typically via API keys, OAuth tokens, or mutual TLS. A rate limiter does not authenticate; it assumes the caller is already identified.

**Authorization** determines *what* a client may do—scope boundaries like `read:orders` or `write:invoices`. Rate limits operate *after* authorization; denying a request due to rate limit exhaustion is not an authorization failure (it returns 429, not 403).

**Quotas** are hard caps on resource usage over a long period (e.g., 10,000 API calls per month). They enforce contractual limits and are typically reset monthly or billing-cycle based. Quotas are enforced asynchronously—often reconciled after the request completes.

**Rate limits** control the *rate* of requests—how many per second, minute, or hour. They protect system health in real time. A rate limit might allow 100 requests per second, while a quota allows 1,000,000 per month. Rate limits are enforced synchronously; if a client bursts past the limit, the request is rejected instantly.

In multi-tenant systems, tenants are rarely uniform: a small team might have a generous per-second limit but a low monthly quota, while an enterprise customer may have the opposite. Rate limits should be per-tenant, but also per-endpoint and per-user within a tenant.

## 2. Practical Comparison: Token Bucket, Fixed Window, Sliding Window

### Token Bucket
The most versatile algorithm for API rate limiting. A bucket holds tokens (e.g., 100), refilled at a steady rate (e.g., 10 per second). Each request consumes one token. If the bucket is empty, the request is rejected.

*Practical advantage*: Allows short bursts (up to bucket capacity) while enforcing a long-term average. Ideal for small teams that occasionally spike during deployments, and for enterprise customers who have predictable daily peaks.

*Practical disadvantage*: Stateful—requires storing token count and last refill timestamp per key. Memory cost is linear with distinct limit keys.

### Fixed Window
Divide time into windows of N seconds (e.g., 60-second windows). Count requests in the current window. If the count exceeds the limit, reject subsequent requests until the next window.

*Practical advantage*: Extremely cheap to implement (one counter per key, resets on a timer).

*Practical disadvantage*: "Boundary problem"—at the edge of a window, requests can spike to 2x the limit. A client could send 99 requests at second 59, then 99 more at second 61, achieving 198 requests in two contiguous seconds, while the intended limit was 100 per minute. This hurts reliability when many tenants coordinate bursts (e.g., at the top of the hour).

### Sliding Window Log
Track timestamps of recent requests. At each request, remove timestamps older than the window duration, then check if the remaining count is under the limit.

*Practical advantage*: Smoothly enforces the limit with no boundary spikes. Accurately represents "requests in the last N seconds."

*Practical disadvantage*: High memory and compute cost—each request requires storing and scanning a list of timestamps. Not practical for high-throughput endpoints without aggressive pruning.

### Sliding Window Counter (Recommended)
A hybrid: maintain two fixed-window counters (current and previous), and compute a weighted value: `previous_window_count * (1 - elapsed_ratio) + current_window_count`. This approximates a true sliding window with O(1) memory per key and no timestamp storage. Widely used in production systems (e.g., Redis Sorted Set + Lua, though we avoid vendor specifics). The approximation is accurate enough for rate limiting—unlikely to allow a meaningful burst past 1.01x the limit.

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

In multi-tenant APIs, a single misbehaving integration (e.g., a retry storm from a buggy client) can saturate the tenant’s rate limit, blocking all other users and integrations within that tenant. This is unacceptable for enterprise customers who may have dozens of services sharing one API key.

**Solution: Layered Rate Limiting**

Implement limits at multiple granularities:

- **Tenant-level** limit: total requests per second across all integrations. This protects your infrastructure from a single tenant consuming all capacity.
- **Integration-level** limit: per API key (or per OAuth client). A noisy integration exhausts only its own sub-limit.
- **User-level** limit (if applicable): per authenticated user within a tenant. Important for B2C-style multi-user tenants.

When a request arrives, evaluate the most restrictive applicable limit. If the integration’s window is empty but the tenant’s is not, the request fails. The noisy integration is blocked, while other integrations continue.

**Fallback: Shedding with Shared State**

Beyond layered limits, implement a *leaky bucket* on the tenant-level key with a high capacity but a low refill rate. This ensures that even if multiple integrations behave badly, the tenant’s overall throughput degrades gracefully rather than dropping to zero. The leaky bucket allows a small burst to drain slowly, buying time for backpressure to propagate.

**Detection and Alerting**

Expose per-integration metrics (see Observability section below) so that operations teams can identify the noisy client *before* it affects the tenant’s other users.

## 4. Headers and Error Messages for API Clients

Clients need clear, machine-readable feedback to adapt their behavior. Return the following headers on *every* response:

- `X-RateLimit-Limit`: The maximum allowed requests per window (e.g., `100`).
- `X-RateLimit-Remaining`: How many requests are left in the current window (e.g., `42`).
- `X-RateLimit-Reset`: Unix timestamp (or ISO 8601) when the window resets. This allows clients to schedule retries precisely.

On rejection (HTTP 429 Too Many Requests), additionally include:

- `Retry-After`: Seconds until the client may retry. Use the actual retry interval rather than a fixed value (e.g., `27`).
- Error body (JSON):
  ```json
  {
    "error": "rate_limit_exceeded",
    "message": "Too many requests. Limit: 100 per minute. Reset at 1700000000. Retry after 27 seconds.",
    "retry_after_seconds": 27
  }
  ```
- Do not reveal the specific limit key (e.g., tenant ID) in error messages, to avoid leaking internal topology.

**For enterprise customers** consuming via a dedicated support channel, consider a separate `X-RateLimit-Limit-Tenant` header (returned only with special scope) to help them monitor their own consumption.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting is a safety valve, not a black box. You must know *why* it triggered and whether it’s effective.

### Metrics (Counters and Histograms)

- `rate_limit.hits_total` per limit key (tenant, integration, endpoint): count of requests accepted.
- `rate_limit.blocked_total` per limit key: count of requests rejected.
- `rate_limit.current_usage` per limit key: gauge of current token count (or window count).
- `rate_limit.blocked_percent_tenant` – aggregated across all limits for that tenant: if blocked % exceeds 5%, something is wrong (either a noisy client or a limit set too low).
- `rate_limit.latency_seconds` – the time spent evaluating the rate limiter itself. Should be <5ms.

### Logs

Log every rejection with sufficient context, but at a reduced rate (e.g., sample 1 in 10) to avoid flooding. Include:

- Tenant ID, integration ID (pseudonymized).
- Endpoint, HTTP method.
- Reason: "tenant_limit_exceeded" vs "integration_limit_exceeded".
- Current usage vs limit.
- Time since last refill (for token bucket).

### Alerts

- **High rejection rate per tenant**: If >10% of a tenant’s requests are rejected, alert. The tenant may need higher limits, or may have a client bug.
- **Burst spikes**: If the rate of `rate_limit.blocked_total` jumps by >200% in 5 minutes, investigate infrastructure (e.g., DDoS, misconfigured client).
- **Global capacity pressure**: If aggregate blocked requests across all tenants exceed a threshold (e.g., 1% of total requests), your system is nearing saturation and limits are doing their job—but you need to scale.
- **Stale metrics**: If per-tenant rate-limit metrics have not been updated for >10 minutes, the rate limiter may be failing open (allowing through).

## Recommended Baseline Design

For a multi-tenant API serving both small teams and enterprise customers, start with this architecture:

1. **Use the token bucket algorithm** at every limit layer. Short bursts are normal, and token bucket handles them fairly. If memory is a concern, use sliding window counter as a near-equivalent.

2. **Enforce three layers of limits:**
   - **Endpoint-level** (e.g., `POST /orders`): 10 req/s, bucket size 20.
   - **Integration-level** (per API key): 50 req/s, bucket size 100.
   - **Tenant-level**: 200 req/s, bucket size 500.

3. **Configure limits per tenant tier** in a config file or admin panel. Small teams get endpoint-level limits; enterprise customers get higher integration and tenant limits, plus the ability to request bursts.

4. **Return full rate-limit headers** on every response. Include `Retry-After` on 429s.

5. **Track metrics per integration** immediately—do not wait for incidents. Log only sampled rejections.

6. **Alert on per-tenant rejection rate >10%** and on global rejection rate >1%. Investigate promptly.

This baseline design scales from a single-node implementation to a distributed system (using a shared atomic store) without changing the algorithm or the client-facing contract.
````
