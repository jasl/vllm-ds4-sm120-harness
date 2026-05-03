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
- Elapsed seconds: 31.558351
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2174, "completion_tokens": 2022, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2022
- Total tokens: 2174

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

```markdown
# Designing Rate Limiting for Multi-Tenant APIs: Small Teams to Enterprise Customers

Rate limiting is one of those systems that seems simple until you have to do it right. For a multi-tenant API serving both small teams and enterprise customers, the stakes are higher: a poorly designed rate limiter can either let a noisy tenant degrade service for everyone, or block legitimate usage and frustrate paying customers. This article walks through the engineering decisions behind a fair, observable, and tenant-aware rate limiting design.

## 1. Authentication, Authorization, Quotas, and Rate Limits—Know the Difference

These four concepts are frequently conflated, but they serve distinct purposes.

**Authentication** verifies identity: “Who is making this request?” Usually via API keys, OAuth tokens, or JWTs.

**Authorization** determines permissions: “Is this identity allowed to perform this action?” It checks scopes, roles, and resource access.

**Quotas** enforce long-term usage limits: “How many requests can this tenant make per month?” Quotas are typically reset monthly or billing-cycle and are used for capacity planning and billing enforcement.

**Rate limits** control short-term request velocity: “How quickly can this tenant send requests?” They protect the API from bursts, abuse, and resource exhaustion. A tenant may have a 10,000 request/hour quota but a 100 requests/second rate limit—the quota ensures they don’t exceed their plan, the rate limit ensures they don’t flood the system.

In a multi-tenant API, both quotas and rate limits must be tenant-aware, but rate limits need finer granularity to prevent one noisy integration from affecting others.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window

Practical differences matter more than theoretical elegance.

**Fixed Window** is the simplest: count requests in a time window (e.g., 1 minute), reset at the end. Problem: a burst at the boundary of two windows can double the actual request rate. Example: 100 requests at second 59 and 100 more at second 61—the system sees 200 requests in ~2 seconds, violating the intended limit. This makes fixed window unpredictable for critical APIs.

**Sliding Window** (typically sliding window log or sliding window counter) solves the boundary problem by considering a rolling time frame. A sliding window log stores timestamps of recent requests; a sliding window counter uses a weighted sum of the current and previous window. It is more accurate but requires more memory and computation. If you have thousands of tenants, storing every timestamp for every key gets expensive.

**Token Bucket** is the practical middle ground. You maintain a bucket with a maximum number of tokens (burst capacity) that refills at a fixed rate (sustained rate). Each request consumes one token. If the bucket is empty, the request is rejected. The key advantage: it allows short bursts (up to the bucket size) while enforcing a long-term average rate. It also uses constant memory per tenant—just two values (current tokens, last refill timestamp). For multi-tenant APIs, token bucket is the recommended default: predictable, memory-efficient, and fair during bursts.

## 3. Avoid Punishing an Entire Tenant for One Noisy Integration

Enterprise tenants often have many integrations: CRM systems, internal dashboards, partner webhooks, automated scripts. One misbehaving integration should not block the entire tenant’s API access, nor should it degrade experience for other tenants.

**The solution: sub‑key rate limiting.** Instead of limiting only by tenant API key, include a sub‑key or integration identifier (e.g., a client ID, a source IP bucket, or a user-agent hash). Each integration gets its own rate limit bucket, nested under the tenant’s global limit. The global limit is the hard ceiling, but individual integrations are throttled independently.

Implement a two‑level hierarchy:
- **Tenant-level bucket**: enforces the overall plan limit (e.g., 500 requests/second).
- **Integration-level bucket**: enforces a per‑integration cap (e.g., 100 requests/second), preventing one integration from exhausting the tenant’s budget.

When an integration exceeds its sub-limit, only that integration is throttled. Other integrations under the same tenant continue to work. The tenant-level bucket still protects the overall API capacity—if the sum of all integrations exceeds the tenant limit, the global bucket rejects the excess, but it does so fairly across integrations.

Additionally, implement **queuing with backpressure** for non‑critical endpoints. Instead of immediate rejection, allow a short queue (e.g., 50ms) and drain it at the allowed rate. This absorbs micro‑bursts without dropping requests, and noisy integrations simply get queued more often.

## 4. Headers and Error Messages Clients Will Actually Use

Clients need clear, actionable information to self-mitigate. Return these headers on every API response:

- `X-RateLimit-Limit`: The maximum requests allowed per window (e.g., 500).
- `X-RateLimit-Remaining`: Requests left in the current window.
- `X-RateLimit-Reset`: Unix timestamp when the window resets (or when the bucket fully refills).
- `Retry-After`: Seconds the client should wait before retrying a rate-limited request.

When a request is rejected (HTTP 429 Too Many Requests), the response body should include:

- `error.code`: A machine-readable code (e.g., `RATE_LIMIT_EXCEEDED`).
- `error.message`: A human-readable explanation (e.g., “You have exceeded your rate limit. Please wait and retry.”).
- `error.scope`: Indicates whether the limit is tenant-level or integration-level (e.g., `"integration"` or `"tenant"`). This helps the client debug which part of their system is responsible.
- `error.retry_after_seconds`: Same as the header, but also in the body for clients that ignore headers.

For enterprise tenants, consider adding a `X-RateLimit-Integration-Id` header on rate-limited responses so their ops team can identify which client is causing the issue.

## 5. Observability: Know When Protection Works (or Doesn’t)

Without observability, rate limiting is a blind safety net. You need signals that show whether the system is protecting reliability without blocking legitimate traffic.

**Metrics** (aggregated, not per‑request):
- `rate_limit.requests_total` by tenant and integration.
- `rate_limit.throttled_total` by tenant and integration (count of 429s).
- `rate_limit.queue_depth` and `rate_limit.queue_wait_ms` for queued requests.
- `rate_limit.bucket_usage_percent` per tenant (how close they are to the limit).
- `rate_limit.tenant_level_throttled` vs `rate_limit.integration_level_throttled`—a high ratio of integration-level throttles indicates noisy internal clients; a high ratio of tenant-level throttles may indicate an undersized plan.

**Logs** (granular but sampled):
- Log every throttled request with tenant ID, integration ID, route, and limit that was hit.
- Log queue events (enqueue, dequeue, timeout).
- Sample successful requests at 1% to avoid log volume, but always log throttling events.

**Alerts**:
- **P99 latency increase** across tenants (not just one)—rate limiting should not raise latency for everyone.
- **Spike in integration‑level throttling** for one tenant—could indicate a misconfigured client or a bug.
- **Sudden drop in request volume for an enterprise tenant**—possible that a sub‑key limit is too low and blocking legitimate integration traffic.
- **Global rate limit hit rate > 5%**—the API may need a capacity review or better burst handling.

**Dashboards** should show:
- Per‑tenant rate limit usage heatmap (tenants with high usage need attention).
- Integration‑level throttle share (pinpoint noisy internal components).
- Queue length and discard rates.

## Recommended Baseline Design

For most multi‑tenant APIs serving teams and enterprises:

1. **Use token bucket** per tenant and per integration (sub‑key). Bucket size = burst allowance (e.g., 2x sustained rate). Refill rate = plan limit. Each tenant gets a default integration-level bucket at 20% of the tenant limit.

2. **Two‑level hierarchy**: Reject at integration bucket first; only if the integration bucket is empty, check the tenant bucket. This prevents one noisy integration from starving others.

3. **Return standard headers** (`X-RateLimit-Limit`, `Remaining`, `Reset`, `Retry-After`) plus a `scope` field in the error body.

4. **Implement a small request queue** (e.g., 100ms max wait) for endpoints that can tolerate latency. Reject only if the queue is full. This handles micro‑bursts gracefully.

5. **Store rate limit state in a fast, shared data store** (e.g., Redis or Memcached) with per‑tenant TTLs. Use atomic operations (INCR, EXPIRE) to avoid race conditions.

6. **Monitor at the tenant and integration level**. Alert if throttle rate exceeds 1% of total requests for a given integration, and if P99 latency increases globally.

A well-designed rate limiter is invisible to legitimate users and transparent to those who need to self-correct. By separating concerns, using token buckets, and building observability from day one, you protect your API’s reliability without punishing noisy-but-necessary integrations—a balance that keeps both small teams and enterprise customers happy.
```
