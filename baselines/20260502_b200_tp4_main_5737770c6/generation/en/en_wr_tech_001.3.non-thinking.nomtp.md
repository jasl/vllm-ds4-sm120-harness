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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 14.411404
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2175, "completion_tokens": 2023, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2023
- Total tokens: 2175

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
# Designing Rate Limiting for a Multi-Tenant API: Balancing Small Teams and Enterprise Customers

## 1. Foundational Concepts: Authentication, Authorization, Quotas, and Rate Limits

Before designing any rate-limiting system, we must distinguish four related but distinct concepts that often get conflated.

**Authentication** answers "Who is this client?" It verifies identity via API keys, OAuth tokens, or mTLS certificates. A request that fails authentication should be rejected outright, never evaluated against limits.

**Authorization** answers "What is this client allowed to do?" It checks permissions—can this user read sensitive data? Can they write to production? Authorization failures return 403 Forbidden, distinct from rate-limit responses.

**Quotas** are long-term, often monetary or contractual limits: "10,000 API calls per month" or "50 GB of storage." Quotas reset on billing cycles, not rolling windows. They are enforced periodically, and clients are often notified before hard enforcement.

**Rate limits** are short-term, high-frequency controls: "100 requests per second" or "10,000 requests per hour." They protect system stability, not just billing. Rate limits are the focus of this article.

A common mistake is using rate limits to enforce quotas. This punishes a bursty client that stays within monthly quota but temporarily exceeds a per-second limit. Quota enforcement belongs in a separate accounting layer, ideally asynchronous.

## 2. Algorithm Comparison: Token Bucket, Fixed Window, and Sliding Window

### Fixed Window
Categorizes requests into buckets of time (e.g., 100 requests per minute starting at :00). Simple to implement—a counter per tenant per window. However, near window boundaries, clients can burst to 2x the limit. For example, at :59.999, 100 requests; at :00.000, another 100 requests. This creates traffic spikes that defeat the purpose of rate limiting.

### Sliding Window Log
Maintains a timestamp log of requests per tenant. When a request arrives, it removes timestamps older than the window, then counts remaining. Accurate but memory-intensive for high-throughput tenants with many requests per window. Also requires non-trivial eviction logic.

### Token Bucket
The most practical algorithm for multi-tenant APIs. Two parameters: *refill rate* (tokens per second) and *bucket capacity* (max burst). Tokens accumulate at the refill rate up to the bucket capacity. Each request consumes one token. A request with insufficient tokens is denied.

**Why token bucket wins for multi-tenant:** It naturally separates *sustained rate* from *burst capacity*. An enterprise customer with a 1000 req/s rate limit and 2000 burst can handle a sudden spike—perfect for CI/CD pipelines or report generation. At the same time, sustained traffic above 1000 req/s is blocked. The bucket empties during bursts, then refills gradually, preventing indefinite high-rate abuse.

Fixed window does not allow controlled bursts; sliding window does not distinguish burst from sustained rate. Token bucket is the industry standard (used by AWS, Stripe, GitHub) for good reason.

## 3. Avoiding Tenant-Wide Punishment from One Noisy Integration

A single misbehaving integration (e.g., a polling script with an infinite retry loop) should not block all other users within the same tenant. This is the "noisy neighbor" problem.

**Solution: Two-tier or three-tier rate limiting.**

- **Tier 1: Tenant-level limit.** Applies to all requests bearing that tenant's API key. This is the contractual limit (e.g., 5000 req/s for enterprise).
- **Tier 2: Integration-level limit.** Each API key or credential within a tenant gets its own sub-limit. If a team has five integrations, each integration should have a lower limit (e.g., 1000 req/s), and the sum of all integrations should not exceed the tenant limit.
- **Tier 3 (optional): Endpoint-level limit.** If a specific endpoint (e.g., `/reports/generate`) is expensive, apply a separate, smaller token bucket even if the integration is within its limit.

Implementation: Maintain a separate token bucket for each (tenant_id, api_key) pair. When an integration exhausts its bucket, only that API key is blocked. Other integrations using different API keys under the same tenant remain unblocked. The tenant-level bucket acts as a parent: if it is exhausted, all integrations are blocked, but only after each integration has consumed its own allowance.

**Important:** Enforce from the top down. First check the tenant bucket. If it has tokens, proceed to check the integration bucket. If the integration bucket is empty, return 429 but only for that key. This prevents one key from draining the tenant's shared capacity.

## 4. Headers and Error Messages

Clients need clear, machine-readable feedback. Return these standard headers on every response:

```
X-RateLimit-Limit: 5000          # The limit for this tenant or endpoint per second
X-RateLimit-Remaining: 3421      # Tokens remaining in the current bucket
X-RateLimit-Reset: 1699000000    # Unix timestamp when the bucket will be full again (next token available)
Retry-After: 2                   # Seconds until client can retry (only on 429 responses)
```

On 429 Too Many Requests, the response body should include:

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit of 5000 requests per second. Please wait 2 seconds before retrying.",
  "scope": "integration",       // or "tenant" or "endpoint"
  "retry_after_seconds": 2,
  "limit": 5000,
  "current_usage": 5000
}
```

The `scope` field is critical. If the limit is integration-scoped, the client file a support ticket with their own API key. If tenant-scoped, the entire organization is blocked—this is a rare event that needs immediate escalation.

Never return 429 for permanent errors like invalid API keys (use 401) or insufficient permissions (use 403). That ensures monitoring systems don't confuse authentication failures with rate limiting.

## 5. Observability: Metrics, Logs, Alerts

Rate limiting requires observability that tells you whether the system is *protecting reliability* without *blocking legitimate use*.

### Key Metrics
Emit these as Prometheus counters/histograms, tagged by `tenant_id`, `client_id`, `endpoint`, and `limit_tier`:

- `rate_limit_requests_total` – All requests evaluated.
- `rate_limit_allowed_total` – Requests allowed.
- `rate_limit_denied_total` – Requests denied (429).
- `rate_limit_bucket_capacity` – Current tokens remaining per bucket (useful for dashboards).
- `rate_limit_latency_seconds` – Time spent in rate-limit middleware (should be <1ms).

### Dashboards
- **Heatmap of denied requests per tenant.** A sudden spike for one tenant indicates a misbehaving integration. Investigate.
- **P50/P99 of tokens remaining.** If most tenants are always near 0 tokens, limits are too tight or capacity is too low.
- **429 rate per endpoint.** Expensive endpoints should see occasional 429s; if never, limits may be too generous.

### Logs
Log every rate-limit decision at a structured log level (info, not debug). Include tenant_id, client_id, endpoint, tokens_remaining, denied_reason. Use a consistent schema across services.

### Alerts
- **P1:** Any tenant exceeding 95% of its limit for 5 minutes → auto-scale or edge-case investigation.
- **P2:** 429 error rate > 1% of total traffic for an endpoint → possible misconfigured client library.
- **P3:** Sudden drop in 429s for a previously throttled tenant → verify that limits were adjusted intentionally.

## 6. Recommended Baseline Design

For a multi-tenant API serving both small teams and enterprise customers:

1. **Algorithm:** Token bucket with separate parameters for sustained rate (refill per second) and burst capacity (bucket size). Default: 100 req/s refill, 200 burst for small teams; 5000 req/s refill, 10,000 burst for enterprise.

2. **Tiers:** Two levels—tenant-level (sum of all integrations) and integration-level (per API key). Enforce tenant first. If tenant is exhausted, return 429 with scope: "tenant". If only integration is exhausted, return 429 with scope: "integration".

3. **Headers:** Always include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After` on 429.

4. **Observability:** Emit per-tenant and per-integration metrics. Set alerts for sustained high usage and sudden 429 spikes.

5. **Configuration:** Store limits in a central config service or database, not hardcoded. Allow support to adjust limits per tenant without redeploying.

6. **Catch-all:** If the rate limiter itself fails or is unavailable, fall back to allowing the request but log a critical alert. Rate limiting should never be a single point of failure that blocks all traffic.

This design protects reliability, enforces fairness across noisy integrations, and gives clients clear feedback to self-correct. It works for a startup's first ten teams and scales to a thousand enterprise tenants.
````
