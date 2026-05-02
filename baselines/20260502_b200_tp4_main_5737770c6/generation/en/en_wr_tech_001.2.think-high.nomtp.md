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
- Elapsed seconds: 14.453008
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2189, "completion_tokens": 2037, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2037
- Total tokens: 2189

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
# Designing Rate Limiting for a Multi-Tenant API: Protecting Teams Without Punishing Them

For backend engineers building APIs that serve both small teams and enterprise customers, rate limiting is often treated as a simple afterthought—a Redis counter, a 429 status, and a hope that users behave. But when a single noisy integration can degrade service for thousands of paying customers, that approach fails. This article walks through the architectural decisions, algorithmic trade-offs, and operational safeguards needed for a multi-tenant rate limiter that protects reliability without punishing legitimate use.

## 1. Foundational Definitions: What We’re Actually Building

Before designing, we must distinguish four concepts that are frequently conflated:

- **Authentication** confirms *who* a client is (e.g., API key validation, OAuth token). It answers: “Are you known to the system?”
- **Authorization** determines *what* a client can do (e.g., read-only vs. write access, endpoint permissions). It answers: “Are you allowed to perform this action?”
- **Quota** is a hard, pre-agreed ceiling on total consumption over a billing period (e.g., 10,000 requests per month). Exceeding a quota typically blocks access until the period resets or the customer upgrades.
- **Rate limit** is a shorter-term, more granular constraint (e.g., 100 requests per second). Its purpose is not to meter usage but to prevent a single client from overwhelming shared infrastructure.

In a multi-tenant system, rate limits are a *safety mechanism*; quotas are a *business constraint*. Confusing them leads to design errors—like blocking a customer’s entire month because they burst for ten seconds.

## 2. Algorithm Selection: Token Bucket, Fixed Window, and Sliding Window

Each algorithm makes a different trade-off between fairness, burstiness, and memory cost.

### Fixed Window
Every clock minute (or second), the counter resets. If a tenant makes 100 requests at 0:00:59 and 100 at 0:01:01, they effectively get 200 requests across the boundary. Fixed window is simple but allows “burst at edges” that punish other tenants. It also creates a thundering herd problem: all tenants resume at the top of the minute.

### Sliding Window Log
Stores a timestamp for every request within the window (typically the last 60 seconds). On each request, it evicts timestamps older than the window and checks the count. This gives precise enforcement but requires O(n) memory per tenant, where n is the number of requests in the window. For a high-throughput enterprise tenant, this can become expensive in distributed caches.

### Token Bucket
A bucket holds a configurable number of tokens and refills at a steady rate (e.g., 100 tokens per second, maximum bucket of 200). Each request consumes one token. Short bursts (up to bucket size) are allowed, but sustained rate is strictly limited. Token bucket is the most natural fit for API traffic: it absorbs spikes without punishing small teams, while preventing any tenant from saturating the infrastructure for more than a few seconds.

**Practical verdict**: Use token bucket for per-tenant rate limits. It is memory-efficient (store only token count and last refill timestamp per tenant), handles bursts gracefully, and does not require storing a full request log.

## 3. Avoiding Tenant-Wide Punishment for One Noisy Integration

Enterprise tenants often have multiple integrations—a CI pipeline, a mobile app, a backend service—all sharing the same API key. A buggy CI script can consume the entire tenant’s rate limit, starving the production app. The solution is **hierarchical rate limiting** with sub-tenant keys.

- **Tenant-level bucket**: Enforces the overall limit (e.g., 1000 req/s).
- **Integration-level bucket**: Each distinct integration (identified by API key + `User-Agent` or a `X-Integration-Id` header) gets its own small bucket, e.g., 100 req/s.

When a request arrives:
1. Deduct from the integration bucket first.
2. If the integration bucket is exhausted, return 429 but *do not* touch the tenant bucket.
3. If the integration bucket has tokens, deducy from the tenant bucket. If the tenant bucket is empty, the integration—even if it still has its own tokens—is rejected.

This ensures that one misbehaving integration cannot consume the tenant’s shared allocation. The tenant can contact support, identify the integration from logs, and fix it without impacting other integrations.

## 4. HTTP Headers and Error Messages

Consistent feedback turns a black-box denial into actionable information. Every rate-limited response should include:

### Headers on **every** request (success or failure)
- `X-RateLimit-Limit`: The maximum request rate per window (e.g., `1000`).
- `X-RateLimit-Remaining`: Tokens remaining in the tenant-level bucket (e.g., `342`).
- `X-RateLimit-Reset`: Unix timestamp when the bucket refills to full (or when the window resets). For token bucket, compute `now + (tokens_remaining / refill_rate)`.

### Headers on **429 Too Many Requests**
- `Retry-After`: Number of seconds to wait before retrying (e.g., `5`). This is critical for automated clients.
- `X-RateLimit-Scope`: Which bucket was exhausted (`tenant` or `integration`). This helps the client understand whether upgrading their plan (tenant) or fixing a specific integration is the answer.

### Error response body
```json
{
  "error": "rate_limit_exceeded",
  "message": "Your tenant has exceeded its rate limit. Retry after Sun, 12 Nov 2023 14:00:05 GMT. If you believe this is a bug, contact support with your integration ID.",
  "retry_after_seconds": 5,
  "scope": "tenant"
}
```

Avoid vague messages: “Too many requests” with no context forces the client to guess. The goal is to let a developer fix the issue in under 60 seconds.

## 5. Observability: Metrics, Logs, and Alerts

Rate limits succeed only if you can prove they are protecting reliability without blocking legitimate traffic. Instrument three layers:

### Metrics (aggregated, low-cardinality)
- `rate_limit_requests_total` with labels `tenant_id`, `integration_id`, `decision` (allowed | blocked), `scope` (tenant | integration). This reveals which tenants hit limits and whether it’s integration-level or tenant-level.
- `rate_limit_tokens_remaining` histogram per tenant. A tenant consistently hovering near zero tokens may have misconfigured limits.
- `http_request_duration_seconds` per tenant, sliced by `rate_limited=true/false`. If limited tenants’ latency drops significantly, the limiter is working.

### Logs (high-cardinality, sampled)
- Emit a structured log line **only on rate-limit rejections** (to avoid volume). Include `tenant_id`, `integration_id`, `route`, `time_since_first_request_of_burst`. This helps debugging: “Why did the CI pipeline get blocked?” → look at the logs for the integration ID.
- Also log **every time** a tenant’s token count drops below 10% of its bucket. This is a leading indicator of approaching limits.

### Alerts
- **Critical**: Any tenant blocked more than X% of its requests over 5 minutes (e.g., >5%). This means the limit is too tight—the tenant is being punished.
- **Warning**: Any integration blocked more than 50% of its requests while the tenant has abundant tokens. This suggests a buggy integration that the tenant may not know about.
- **Operational**: Rate limiter cache latency exceeds 10ms. The rate limiter should never be the bottleneck.
- **Silent**: No. Do not alert on aggregate global error_rate; spike it down to per-tenant. A single enterprise customer with 429s is a support issue, not a PagerDuty alert—unless it’s your own API key.

## 6. Recommended Baseline Design

For a multi-tenant API serving teams of 5 to enterprise deployments of 5,000:

- **Algorithm**: Token bucket per tenant and per integration, stored in a distributed cache (e.g., Redis or Memcached) with a TTL equal to the bucket’s refill period. Use a Lua script or atomic compare-and-swap to ensure correctness under concurrent requests.
- **Tenant limit**: Dynamic, based on plan tier. Small teams get a soft limit of 50 req/s (bucket size 150); enterprises get 1000 req/s (bucket size 3000). Integration-level bucket defaults to 10% of tenant limit, with a minimum of 10 req/s.
- **Exemptions**: Internal health checks and webhook retries from your own systems should use a separate, uncounted endpoint or a bypass via a different authentication scope.
- **Graceful degradation**: If the rate limiter backend is unreachable, allow requests but emit a high-priority alert and cache the failure. Never block traffic because your limiter is down.
- **Documentation**: Publish your algorithm (token bucket) and header semantics in public docs. Transparency reduces confusion and support tickets.

Rate limiting is not a security feature—it’s a trust contract. Design it to be fair, observable, and debuggable. When done right, neither a small team’s burst nor an enterprise’s forgotten cron job should ever knock your API offline for anyone else.
````
