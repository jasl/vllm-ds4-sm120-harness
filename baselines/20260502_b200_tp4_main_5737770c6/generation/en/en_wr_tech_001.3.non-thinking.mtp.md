# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 9.520471
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2172, "completion_tokens": 2020, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2020
- Total tokens: 2172

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
# Designing Rate Limiting for a Multi-Tenant API: Balancing Fairness and Reliability

## 1. Foundational Distinctions

Before architecting any throttling mechanism, we must clarify four concepts that engineers frequently conflate:

**Authentication** verifies *who* you are. It answers “Is this request presenting valid credentials?” – typically via API keys, OAuth tokens, or mTLS certificates.

**Authorization** determines *what you are allowed to do*. It answers “Does this authenticated identity have permission to access this specific resource or perform this action?”

**Quotas** define *how much you can use over a long period* (e.g., 10,000 requests per month, 1 TB egress per billing cycle). They are enforced periodically, often after the fact.

**Rate limits** control *how fast you can send requests* (e.g., 100 requests per second). They protect system stability by preventing short bursts from overwhelming shared resources.

For a multi-tenant API serving both small teams and enterprise customers, authentication and authorization are prerequisites, quotas govern contractual usage, and rate limits serve as a real-time safety valve.

## 2. Practical Algorithm Comparison

Three common rate-limiting algorithms each present tradeoffs for multi-tenant systems.

**Token Bucket** – A bucket holds N tokens that refill at R tokens/second. Each request consumes one token. Empty bucket means rejection. It naturally allows bursts up to bucket size while maintaining long-term average rate. This is ideal for APIs where brief spikes are acceptable (e.g., a CI/CD pipeline that sends 50 rapid build requests then goes silent). The downside: tracking per-tenant buckets in distributed systems requires care to avoid race conditions.

**Fixed Window** – Count requests in discrete time intervals (e.g., 100 requests per minute, resetting at the top of each minute). Simple to implement with atomic counters, but suffers from **edge-of-window bursts**: a tenant could send 100 requests at 00:59 and another 100 at 01:01, effectively achieving double the intended rate while technically complying. For enterprise SLAs, this can cause cascading failures.

**Sliding Window Log** – Maintains a timestamped log of each request within the window (e.g., last 60 seconds). Every request checks the log for total count. It eliminates the burst problem but increases storage and lookup cost – problematic at high throughput for thousands of tenants.

**Sliding Window Counter** – A hybrid: track counts for current and previous fixed windows, then estimate the number of requests in the rolling window using weighted interpolation. Example: “0.4 × previous minute count + current minute count must be ≤ limit.” This approximates sliding window accuracy with O(1) cost, making it the pragmatic choice for most production systems.

## 3. Isolating Noisy Tenants, Not Punishing Everyone

A common failure pattern: a single misconfigured `cron` job in a tenant’s integration consumes 80% of shared proxy capacity, causing the system to rate-limit *all* tenants behind the same key. The solution is **per-tenant granularity with hierarchical isolation**.

Design a three-level hierarchy:
- **Global limit** – maximum total throughput for the entire system (protects upstreams)
- **Tenant limit** – per-tenant cap based on plan (e.g., Silver: 500 rpm, Gold: 5,000 rpm, Platinum: 50,000 rpm)
- **Integration-key limit** – per-client-ID within a tenant (where each integration gets its own API key)

When tenant A’s integration `cron-worker` goes wild, only that integration gets throttled at its own limit – while the tenant’s other integrations (e.g., a webhook receiver) remain unaffected. If the noisy integration exhausts the tenant’s overall cap, only then do other integrations within that tenant get blocked, but this is a contractual consequence, not a system-wide collateral.

Implementation pattern: store rate-limiter state in a high-speed data store (Redis or Memcached) keyed as `rrl:<tenant_id>:<integration_id>`. Check the integration-level bucket first, then the tenant-level bucket. This prevents one misbehaving script from harming neighbors.

## 4. API Client Feedback

Clients must receive actionable information when they hit limits. Return:

**429 Too Many Requests** with this body or header structure:
```
Retry-After: 45
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1623456789
X-RateLimit-Retryable: true
```
- `Retry-After` – seconds until next request should be attempted (essential for `scheduled` retry logic)
- `X-RateLimit-Limit` – the maximum requests allowed in the window
- `X-RateLimit-Remaining` – how many you can still send (useful for proactive backoff)
- `X-RateLimit-Reset` – Unix timestamp when the window resets (avoids clock-sync issues)
- `X-RateLimit-Retryable` – boolean indicating whether the limit is temporary (true) versus a permanent quota hard stop (false)

For non-429 responses, always include `X-RateLimit-Remaining` so clients can slow down before hitting a hard block. This is especially critical for enterprise batch processors that poll aggressively.

Error messages should be machine-parseable, with a code like `RATE_LIMIT_EXCEEDED` and a human-readable explanation: `“Your integration ‘deploy-svc’ has exceeded 100 req/s. Limit resets in 32 seconds. Consider adding jitter to your retry logic.”` Avoid revealing internal details like bucket sizes or which other tenants are affected.

## 5. Observability: Proving Limits Work

Monitoring must answer: “Are we blocking bad actors or good users?”

**Metrics to collect (by tenant and integration, aggregated globally):**
- `rate_limiter_requests_total` – count of all requests evaluated
- `rate_limiter_throttled_total` – count of requests blocked
- `rate_limiter_bucket_empty_seconds` – how long a tenant was fully blocked (indicator of chronic overuse)
- `rate_limiter_limit_exceeded_by_integration` – blocked at integration level vs. tenant level (see isolation point above)
- P50/P99 latency impact of the rate-limiter itself (should be <2ms)

**Alerts:**
- If any tenant gets blocked for >60% of a sliding hour → investigate noisy integration or bot traffic
- If global throttling rate exceeds 5% of total requests → possible DDoS or upstream degradation
- If `rate_limiter_bucket_empty_seconds` spikes for a platinum tenant → review their plan appropriateness
- No alerts for individual integration throttles (expected behavior) unless they persist for >24h

**Logs:**
- Log every throttle event with `tenant_id`, `integration_id`, `consumer_ip`, `reason` (e.g., “integration limit exceeded”), and `retry_after_seconds`
- Do not log every non-throttled request (too noisy). Sample at 1:1000 for latency tracing.
- Structured logs (JSON) with a `rate_limited: true` field for easy querying.

**Dashboards:**
- Heatmap of throttled requests by tenant (rows) over time (columns) – spot anomalies instantly
- “Top 10 blocked integrations” – sorted by throttle count, linked to tenant name
- Time series of `X-RateLimit-Remaining` percentiles – if most tenants hover near zero, limits may be too aggressive
- Comparison of plan limit vs. actual peak usage per tenant – support capacity planning

Without this observability, you are flying blind. Enterprise customers will escalate quickly if their legitimate batch jobs get throttled, and you’ll have no data to defend your decision.

## Recommended Baseline Design

For a multi-tenant API serving both small teams and enterprise customers:

1. **Algorithm**: Sliding window counter per integration key and per tenant key (stored in Redis using sorted sets or Lua scripts for atomicity). This balances accuracy and cost at scale.

2. **Hierarchy**: Three-tier enforcement:
   - Global limit (e.g., 100,000 rpm for the entire proxy fleet)
   - Tenant limit (variable by plan)
   - Integration limit (default: 20% of tenant limit, configurable per integration)

3. **Burst handling**: Allow integration sub-limits to burst to 150% for 5 seconds before hardening, to accommodate legitimate CI/CD spikes. Notify the affected integration via the `Retry-After` header when hardened.

4. **Client feedback**: Always return `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After` on 429s. Use structured error codes.

5. **Observability**: Prometheus-style metrics per tenant/integration, alert on chronic tenant throttling (not ephemeral integration throttling), and log only blocked events.

6. **Grace period for enterprises**: Offer a “burst pool” of 10% extra capacity that can be used once per hour without penalty, allowing small spikes from otherwise steady workloads. Expose this via a dedicated header `X-RateLimit-Burst-Remaining`.

This design protects reliability while acknowledging that small teams sometimes need to run a quick deployment, and enterprises need predictable, measurable throughput. The key is isolating at the integration level, communicating transparently to clients, and monitoring impacts rather than just limits.
````
