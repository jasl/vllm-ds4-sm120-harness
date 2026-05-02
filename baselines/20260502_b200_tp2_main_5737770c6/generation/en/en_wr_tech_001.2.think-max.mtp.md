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
- Elapsed seconds: 10.516376
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2429, "completion_tokens": 2277, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2277
- Total tokens: 2429

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
# Designing Rate Limiting for Multi-Tenant APIs: Balancing Team Agility with Enterprise Reliability

## 1. Core Definitions: Authentication, Authorization, Quotas, and Rate Limits

Before designing any limiting mechanism, we must distinguish four concepts that engineers frequently conflate.

**Authentication** verifies *who* the client is (e.g., API key validation, OAuth token inspection). It is a gate: either the request passes or it fails with 401.

**Authorization** determines *what* the authenticated client is allowed to do (e.g., read vs. write permissions, scope validation). Failure yields 403.

**Quotas** are *hard, long-term limits* on resource consumption—typically measured over hours, days, or billing cycles. “Your team may create 1,000 records per month” is a quota. Exceeding it blocks further action until the reset window, often requiring a plan upgrade.

**Rate limits** are *soft, short-term controls* on request velocity—measured in seconds or minutes. “Your API key may send 100 requests per second” is a rate limit. Exceeding it triggers a brief backoff (e.g., 429 retry-after=1 second), after which normal traffic resumes. Rate limits protect system stability; quotas protect business models.

A multi-tenant system must handle all four, but this article focuses on rate limits—the real-time guardian of shared infrastructure.

## 2. Algorithm Selection: Token Bucket, Fixed Window, Sliding Window

### Fixed Window (Simplest, Most Problematic)
Divide time into uniform intervals (e.g., 60 seconds). Count requests per tenant per window. If count exceeds limit, reject until next window.
**Practical problem:** Burst at window boundary. If a tenant sends 100 requests at t=59.9s and another 100 at t=60.1s, the system sees 200 requests in a 0.2s span—defeating the purpose. Also, naive implementations allow a tenant to “max out” a window, then immediately do the same in the next, effectively doubling throughput.

### Sliding Window (Better, More Complex)
Maintain a rolling time window (e.g., last 60 seconds). Track request timestamps per tenant (or use a log-based counter). Reject if the count in the sliding window exceeds the limit.
**Practical advantage:** Smooths boundary spikes. No double-burst gap.
**Practical cost:** Higher memory/storage per tenant (storing timestamps) and computational overhead for pruning old entries. In Redis, a Sorted Set per key works but can grow large for high-throughput tenants.

### Token Bucket (Recommended for Multi-Tenant APIs)
Concept: a bucket holds up to `B` tokens. Tokens are added at rate `R` per second (up to capacity). Each request consumes one token. If no tokens remain, the request is queued or rejected.
**Practical advantage:** Naturally handles bursts up to `B` (e.g., a team publishing a batch of updates during off-hours) while enforcing long-term average rate `R`. No window-boundary spikes.
**Practical nuance for multi-tenancy:** Each tenant gets its own bucket. But token buckets are stateful; you must persist the token count and last refill timestamp. In distributed systems, use atomic operations (e.g., Lua script in Redis) to avoid race conditions.
**Why it wins:** Predictable burst tolerance aligns with real-world API usage—small teams occasionally spike, enterprises need sustained throughput.

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

The cardinal sin: a single internal microservice, misconfigured webhook, or buggy client spikes request volume, and you throttle *all* requests from that tenant—including critical operations from other integrations or human users.

**Solution: Hierarchical rate limiting (double-bucket pattern).**
- **Tenant-level bucket:** Controls total requests from the tenant (e.g., 500 req/s). Applies to the API key or authentication identity.
- **Endpoint/resource-level bucket:** Within the tenant, each distinct integration path (URL pattern, user-agent, source IP, or consumer ID) gets its own smaller bucket. For example, `/reports/generate` might be limited to 10 req/s per integration, even if the tenant limit is 500 req/s.

**Practical implementation:**
1. First, check the endpoint-specific bucket. If it’s empty, reject with a clear message: “This integration exceeded its per-endpoint rate limit.”
2. Then, check the tenant-level bucket. If that’s empty but the endpoint bucket had capacity, you still enforce the global tenant cap.
3. Both must pass for the request to proceed.

**Fallback: Per-source quota.** If you can’t implement hierarchical buckets, annotate each API key or token with an optional “max burst per IP/agent” override. This is coarser but better than nothing.

**Result:** A misbehaving script hammering `POST /import` throttles itself, while other endpoints (`GET /users`, `POST /login`) remain unaffected for that tenant.

## 4. Headers and Error Messages

Every rate-limited API must communicate limits, usage, and recovery time in a machine-readable way. Follow the HTTP `429 Too Many Requests` standard, enriched with headers.

### Response Headers (Required for All 2xx and 429 Responses)
```
X-RateLimit-Limit: 500           # Maximum requests per window (or tokens per second)
X-RateLimit-Remaining: 123       # Remaining requests in current window/bucket
X-RateLimit-Reset: 1694680000    # Unix timestamp when the limit resets (or bucket refills to capacity)
Retry-After: 2                   # Seconds client must wait (only on 429)
```

### 429 Response Body
Return a JSON object with:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "You have exceeded the rate limit. Retry after 2 seconds.",
    "retry_after_seconds": 2,
    "limit_type": "per_endpoint",    // Indicates which bucket was hit
    "tenant_id": "acme-corp",
    "integration": "webhook-orders"  // Optional, for debugging
  }
}
```

**Why this matters:** Clients (especially enterprise SREs) need to programmatically parse the error to implement exponential backoff. The `retry_after_seconds` field must match the `Retry-After` header. Include `limit_type` so the client knows whether to throttle a specific integration or the entire account.

### Important: No Ambiguity
Never return 429 with a body saying “try again later” but omit headers. This forces human debugging and breaks automated retry logic.

## 5. Observability: Protecting Reliability Without Blocking Legitimate Use

Rate limits are a safety valve. If you can’t see whether they’re working, you’ll either throttle too aggressively (losing revenue) or too leniently (causing outages).

### Key Metrics
- **Requests throttled (by tenant, by endpoint, by hour):** A sudden spike in throttling at a specific endpoint signals a noisy integration. Investigate before it escalates.
- **Token bucket depth (p50, p99):** Are most tenants operating at 20% capacity, or hovering near empty? Frequent near-empty states imply your limits are too low for normal patterns.
- **Retry rate after 429:** If clients ignore 429s and retry immediately, your limits aren’t being respected. Monitor `Retry-After` compliance using user-agent analysis.
- **Error budget consumption:** Define a reliability target (e.g., 99.9% successful requests). Track how much of that budget is consumed by throttled vs. genuine errors. If throttled requests exceed 1% of total traffic, your limits may be too aggressive.

### Logging
- Log every 429 with tenant ID, endpoint, source IP (hashed for privacy), and the `limit_type` bucket.
- Do **not** log full request bodies (PII risk). Log the request path, headers, and error code.
- Use structured logging (JSON) with fields: `throttled`, `tenant_id`, `endpoint`, `bucket_type`, `original_limit`, `current_usage`, `retry_after_seconds`.

### Alerts
- **High throttle rate for a single tenant:** Pager if a tenant exceeds 100 throttled requests per minute. This may indicate an integration bug or an attack.
- **Global throttle rate spike:** If overall throttled requests jump 3x in 5 minutes, check for widespread misconfiguration (e.g., an SDK update broke retry logic).
- **Enforcement latency increase:** If rate limit checks take >10ms (including Redis calls), you’re adding noticeable overhead. Alert on p99 latency of the rate limiter middleware.
- **Empty token buckets across multiple tenants during low-traffic periods:** Suggests your token refill rate is too low for idle-but-necessary periodic calls (e.g., health checks).

### Dashboard
Build a real-time view showing:
- Top 10 tenants by throttled requests.
- Endpoints with highest throttle rates.
- Average token bucket depth per tenant tier (small team vs. enterprise).
- Retry-after compliance distribution.

## 6. Recommended Baseline Design

For a multi-tenant API serving teams and enterprises, implement **two-tier token buckets** stored in Redis (or equivalent in-memory store) with Lua scripting for atomic operations.

**Tenant bucket:** capacity = `500`, refill rate = `50/second` for small teams; scale to `5000` capacity / `500/sec` for enterprise plans.

**Endpoint bucket for each integration:** capacity = `20`, refill rate = `2/second`. Adjust based on endpoint criticality.

**Algorithm:** Token bucket (not window). Use sliding window only if your data store doesn’t support token bucket’s atomic refill.

**Headers:** Always return `X-RateLimit-Limit`, `Remaining`, `Reset`, and `Retry-After` on 429.

**Observability:** Instrument rate limiter as a middleware that emits gauge metrics for bucket depth, counter for throttled requests (with tenant and endpoint labels), and histogram for enforcement latency. Alert at 3x normal throttle rate.

**Final thought:** Rate limiting is not a security feature—it’s a mutual contract between your API and its consumers. Design it to be transparent, fair, and observable. Your enterprise customers’ SRE teams will thank you when they can sleep through the night, and your small teams will appreciate that their occasional batch job doesn’t get unfairly punished.
````
