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
- Elapsed seconds: 10.138424
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2318, "completion_tokens": 2166, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2166
- Total tokens: 2318

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
# Designing Rate Limiting for Multi-Tenant APIs: Balancing Fairness and Reliability

## 1. Laying the Groundwork: Authentication, Authorization, Quotas, and Rate Limits

Before designing a rate limiting system, we must distinguish four related but distinct concepts that often get conflated.

**Authentication** answers *who you are* – verifying identity via API keys, OAuth tokens, or mutual TLS. **Authorization** answers *what you are allowed to do* – typically role-based or scope-based permissions (e.g., read-only vs. admin). **Quotas** define *how much you can consume over a long period* (e.g., 10,000 requests per month, 5 GB of storage). Quotas are often enforced during billing cycles and are about capacity planning, not real-time protection.

**Rate limits** are about *how fast you can consume* – they control request velocity over short windows (seconds to minutes). Their primary purpose is to protect system stability from traffic spikes, abusive clients, or misconfigured integrations. Unlike quotas, rate limits are enforced aggressively and in real time.

For a multi-tenant API, rate limits must operate at multiple levels: global (protect the entire service), tenant (isolate one customer’s traffic from another), and sometimes per-endpoint or per-key. The design challenge is ensuring that one small team’s misbehaving integration doesn’t degrade service for an enterprise tenant – or vice versa.

## 2. Algorithm Choices: Token Bucket, Fixed Window, and Sliding Window

At the practical level, three algorithms dominate production systems. Each has distinct trade-offs for multi-tenant use.

**Fixed Window** divides time into discrete intervals (e.g., one minute). A counter resets at the start of each window. *Pro*: Simple, low memory, easy to reason about. *Con*: Burst behavior at window boundaries – a client can send 500 requests at the end of minute 1 and 500 more at the start of minute 2, effectively doubling throughput. This “boundary burst” can cause cascading failures in downstream services. For multi-tenant, this is especially dangerous: one tenant can spike at a boundary and exhaust shared connection pools.

**Sliding Window Log** tracks timestamps for each request within a moving window. *Pro*: Most accurate – no boundary bursts. *Con*: High memory overhead; each request requires a timestamp entry in a sorted set (often Redis). For enterprise tenants with millions of requests per day, this can consume significant storage. Not practical for high-throughput, multi-tenant scenarios without aggressive cleanup.

**Sliding Window Counter** (also called *sliding window with a smoothed counter*) is the pragmatic middle ground. It uses two fixed window counters (current and previous) and interpolates the count based on how far into the current window the request arrives. *Pro*: Near-accurate without storing per-request timestamps. *Con*: Slightly more complex to implement, but memory-efficient. This is the default choice for most multi-tenant API gateways today.

**Token Bucket** allows fixed bursts up to a “bucket capacity” and then refills at a steady rate. *Pro*: Excellent for handling short-term spikes – a team that suddenly pushes 100 queries after 10 minutes of silence gets through immediately. *Con*: Does not naturally handle long-term “average” caps; a tenant with a large bucket can consume intense bursts repeatedly as long as the bucket refills. For multi-tenant, this is often preferable because small teams need bursts for CI/CD or batch jobs, while enterprises can afford larger buckets.

*Recommendation*: Use **sliding window counter** for hard rate limits (strict per-second caps) and **token bucket** for soft limits that allow elastic bursts. Many systems combine both: token bucket for peak smoothing, sliding window for absolute ceilings.

## 3. Avoiding Tenant Punishment from Noisy Integrations

The classic anti-pattern is enforcing a single rate limit keyed by tenant ID. When one integration (a misconfigured webhook, a buggy script, a rogue SDK) exhausts the tenant’s limit, *all* APIs for that tenant are blocked. Legitimate users of the same tenant – or even the same team’s other integrations – suffer.

**Solution: Hierarchical Rate Limiting with Isolation Dimensions**

Implement a three-tier hierarchy:

1. **Global limit**: Protects the entire infrastructure (e.g., 100,000 requests/second across all tenants). This should be extremely high and only triggered by DDoS or cascading failures.
2. **Per-tenant limit**: Protects one customer’s traffic from others (e.g., 5,000 requests/second per tenant). This prevents one enterprise from starving small teams.
3. **Per-key or per-integration limit**: Inside each tenant, allocate limits to individual API keys. A noisy integration’s key hits its cap and is blocked, while other integrations under the same tenant continue unaffected.

Additionally, implement **priority queuing** for enterprise tenants. If a resource is contested, enterprise requests can preempt non-critical traffic from free-tier tenants. This doesn’t replace rate limits but ensures fairness when limits are approached.

Finally, allow tenants to **configure per-key limits** via a dashboard. A small team might set generous limits for their production key and strict limits for a staging key that has a defect. This shifts responsibility to the customer while giving them control.

## 4. Headers and Error Messages: What Clients Need to See

Clients need three things to self-regulate: the current limit, remaining capacity, and the time to wait. Use standard HTTP headers (RFC 6585 style) consistent across all endpoints.

**Response headers on success** (every request, not just throttled ones):

- `X-RateLimit-Limit`: The maximum requests allowed in the current window (e.g., 5000).
- `X-RateLimit-Remaining`: The remaining count for the current window.
- `X-RateLimit-Reset`: Unix timestamp (or ISO 8601) when the window resets.

**When throttled** (HTTP 429 Too Many Requests), additionally include:

- `Retry-After`: Seconds to wait before retrying (e.g., `30`). This is crucial for clients that don’t parse custom headers.
- A JSON error body with structured fields:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Request rate limit exceeded for API key xyz. Resets in 30 seconds.",
    "retry_after": 30,
    "limit_type": "per_key",
    "tenant_id": "acme-corp"
  }
}
```

For **quota limits** (monthly), use a different HTTP status code (`403 Forbidden`) to distinguish from rate limits, with a message like “Subscription quota exhausted. Upgrade or wait for next billing cycle.” This prevents clients from writing retry logic for a problem that won’t resolve in seconds.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting is not “set and forget.” You need to continuously verify that limits protect the system without blocking legitimate traffic.

**Key metrics** (exposed as Prometheus counters/histograms or similar):

- `rate_limit_total` (counter) tagged by tenant_id, endpoint, limit_type (global/tenant/key), and status (allowed/blocked). This shows which tenants are being throttled.
- `rate_limit_current_usage` (gauge) per tenant – current requests in the window. Helps detect tenants approaching limits.
- `http_request_duration_seconds` histogram – scatter latency by tenant. If a tenant’s latency suddenly drops while others spike, rate limiting may be *overly aggressive* (false positives).
- `rate_limit_retry_after` distribution – how often clients receive 429s and for how long. A high rate of 429s on a single key indicates a misconfigured integration that needs customer attention.

**Logs**: Every 429 should log the tenant ID, API key prefix, endpoint, and rate limit key. Aggregate these into a dashboard for customer support to quickly see “Is Acme Corp’s integration broken?” without digging through raw logs.

**Alerts**:

- *Noisy neighbor alert*: Per-tenant rate limit hit >10% of requests for 5 minutes. This triggers investigation: is the tenant under attack, or is our limit too low?
- *Global capacity alert*: Global rate limit usage >80% for 1 minute. Suggests need to scale horizontally or increase global limit.
- *False positive alert*: Sudden drop in 429s concurrent with increase in 5xx errors from downstream services. This may indicate rate limiting is too permissive and the backend is being overwhelmed.

## 6. Recommended Baseline Design

For a new multi-tenant API serving both small teams and enterprises:

- **Algorithm**: Sliding window counter (for strict per-second enforcement) combined with token bucket (for burst allowance). Implement at a centralized gateway layer (e.g., a sidecar proxy or reverse proxy) to avoid coupling with application logic.
- **Tiers**: Global → Tenant → API Key, each with configurable limits. Defaults: Global = 100k req/s, Tenant = 5k req/s, Key = 500 req/s.
- **Storage**: Use an in-memory data store (Redis) with sliding window keys like `rate_limit:tenant:<id>:window:<timestamp>` and TTL equal to the window duration + 1 second to avoid stale counters. For token buckets, use sorted sets with Lua scripts for atomic bucket operations.
- **Headers**: Implement `X-RateLimit-Limit`, `Remaining`, `Reset` on all 2xx responses, and `Retry-After` plus structured JSON on 429s.
- **Observability**: Export per-tenant counters to Prometheus, log every throttled request with tenant + key prefix, and alert on high 429 rates or near-capacity global usage.

This design provides hard isolation between tenants, burst capability for small teams, and clear feedback to clients. It avoids punishing an entire tenant for one noisy integration while keeping the architecture simple enough to maintain as you grow from 10 to 10,000 customers.
````
