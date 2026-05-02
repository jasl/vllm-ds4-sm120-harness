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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 15.875138
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2385, "completion_tokens": 2233, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2233
- Total tokens: 2385

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
# Granular by Design: Rate Limiting for Multi-Tenant APIs

Rate limiting is often treated as an afterthought—a simple "10 requests per second" sticker slapped onto an API gateway. But when your product serves both a three-person startup and a Fortune 500 enterprise under the same API surface, naive rate limiting becomes a source of revenue loss, support tickets, and silent reliability degradation. This article walks through the design decisions that separate a blunt instrument from a surgical one.

## 1. The Four Pillars: Auth, Authorization, Quotas, and Rate Limits

These four concepts are frequently conflated, leading to confusing error messages and broken client logic. Here is the distinction:

- **Authentication** answers *who* the caller is. It is the API key, bearer token, or mTLS certificate at the door. Without it, the request is rejected at the transport layer (`401 Unauthorized`).

- **Authorization** answers *what* the caller is allowed to do. After authentication, the system checks permissions: Can this key access the `DELETE /users` endpoint? That is a `403 Forbidden` if not.

- **Quotas** are *allocations over a long window* (daily, monthly). "Your plan includes 10,000 API calls per month." Quotas enforce business agreements. They are checked at request time but reset infrequently. Exceeding a quota should return a different error than a rate limit hit (`429 Quota Exceeded`).

- **Rate Limits** are *short-term traffic shaping* (per second, per minute). They protect system stability. A burst of 100 requests in one second might violate your rate limit even if the monthly quota has room. Rate limits reset frequently (sliding windows, typically 1–60 seconds).

**Why it matters:** If you return `429` for both quota and rate limit violations, clients cannot distinguish between "you need to buy more credits" and "slow down, you're hammering the server." This ambiguity leads to frustrated customers who retry inappropriate strategies.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window

At the practical implementation level, the choice of algorithm determines how fairly and predictably your system handles bursts.

- **Fixed Window** (e.g., reset every 60 seconds): Simple to implement—store a counter per tenant per window. *Problem:* Traffic concentrated at the window boundary can double the allowed rate. A tenant sending 60 requests at second 59 and another 60 requests at second 60 has effectively used 120 requests in a 2-second span. This defeats the purpose of rate limiting.

- **Sliding Window Log** (e.g., track timestamps of each request): Every request records a timestamp. A new request checks how many timestamps fall within the last N seconds. *Problem:* Memory and computation cost grow linearly with request volume. At high throughput, you end up with O(n) lookups per request.

- **Sliding Window Counter** (hybrid approach): Divide time into small buckets (e.g., 1-second sub-windows within a 60-second window). A rolling sum of the current window and the previous window weighted by overlap gives a close approximation with O(1) memory per tenant. This is the practical sweet spot—accurate enough to prevent abuse, cheap enough to run at scale.

- **Token Bucket**: Refill a bucket of capacity at a steady rate. Each request consumes one token. Bursts are allowed up to the bucket size, but the sustained rate is bounded. *Pros:* Handles natural bursts (e.g., a team deploying a new feature and hitting the API 50 times in a second) without falsely punishing the tenant. *Cons:* Requires the cost of token refill logic. Still, token bucket is my recommended default for multi-tenant APIs because it mirrors real-world usage patterns: teams occasionally spike, then go quiet.

**Summary:** Use token bucket for the primary rate limit. Use sliding window counters for secondary, hit-harder enforcement (like a 10x burst penalty check). Avoid fixed window entirely unless your traffic is perfectly uniform—which it never is.

## 3. Avoiding Tenant-Wide Punishment for Noisy Integrations

Consider a tenant called "Acme Corp" that has five integrations: one poorly written polling script sends 500 requests per second, while the other four behave well. A naive per-tenant rate limit of 1000 requests/minute will let the bad integration consume all capacity, starving the good ones. Or worse, the global limit kicks in and blocks *all* Acme traffic, causing a cascading outage.

**Design principle: Isolate by integration.**

At a minimum, use a compound key for rate limiting: `(tenant_id, integration_id)` or `(tenant_id, api_key)`. Each integration key gets its own token bucket. Acme's bound is the sum of all integration buckets, but a single noisy integration can only exhaust its own bucket. The other integrations remain untouched.

**Secondary measure: Soft caps and per-route limits.**

Even with per-integration buckets, you may want a separate per-route limit. For example, `POST /search` might be computationally expensive—allow 10 requests per minute per integration, regardless of the global limit. This prevents a single expensive endpoint from saturating the database connection pool.

**Third measure: dynamic throttling with backoff hints.**

When an integration hits its limit, return a `Retry-After` header with a suggested delay. But do not hard-block immediately. Instead, progressively degrade: 1-second delay on first violation, 5 seconds on second, then full throttle. This gives poorly written clients time to slow down without impacting other integrations in the same tenant.

## 4. Headers and Error Messages

Clients need deterministic information to adapt their behavior. Return the following headers on every response:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1678901234
```

- `X-RateLimit-Limit`: The maximum requests allowed in the current window (for the specific integration key).
- `X-RateLimit-Remaining`: How many requests are left *before the next request* (this should be decremented).
- `X-RateLimit-Reset`: Unix timestamp of when the window resets (or when tokens will refill to capacity).

Standardize the error response for `429`:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Request rate limit exceeded. Retry after 30 seconds.",
  "retry_after_seconds": 30,
  "quota_type": "per_integration"
}
```

Do not return generic `"TOO_MANY_REQUESTS"`. Distinguish between *rate limit* and *quota exceeded*:

- Rate limit → `error: "rate_limit_exceeded"` + `Retry-After: 30`
- Quota exceeded → `error: "quota_exceeded"` + `X-Quota-Reset: <monthly timestamp>`

Why this matters: an automated client that receives a quota error should stop retrying until the next billing cycle. A rate limit error indicates immediate retry with backoff.

## 5. Observability: Metrics, Logs, and Alerts

Your rate limiter should not be a black box. Instrument it at three levels:

**Metrics (counters and histograms)**
- `rate_limit.total_requests`: total requests seen, tagged by tenant tier and route.
- `rate_limit.blocked_requests`: count of `429` responses. Tag by tenant, integration, and reason (rate vs. quota).
- `rate_limit.bucket_utilization`: histogram of remaining tokens at request time. If most requests are near 0 remaining capacity, you need to increase limits or optimize the endpoint.
- `rate_limit.refill_latency`: how long token bucket refills take. Spikes indicate contention in your data store.

**Logs**
- Each blocked request should log a structured payload: `{tenant_id, integration_id, route, method, limit_type, retry_after}`.
- Do *not* log every allowed request—that wastes storage. Instead, log a sampling (1% of passing requests) to detect false positives.

**Alerts**
- **Alert 1:** `rate_limit.blocked_requests` for a single integration exceeds 100 per minute → likely a misconfigured client. Notify the tenant's support contact.
- **Alert 2:** `rate_limit.blocked_requests` across all tenants exceeds 10% of total requests → your limits are too tight or your system is under-provisioned. Investigate capacity.
- **Alert 3:** `rate_limit.bucket_utilization` below 10th percentile for a tenant over one hour → that tenant is barely using their allocated capacity. This may indicate over-provisioning (lost revenue) or a dead integration.

**Dashboard**
- Build a per-tenant view: current bucket fill, recent throttled count, top integrations by request volume. This helps support engineers answer "why did my API stop working?" without digging through raw logs.

## Recommended Baseline Design

For a multi-tenant API serving teams and enterprises:

1. **Algorithm:** Token bucket per `(tenant_id, api_key)`.
   - Capacity = 100 tokens for small teams, 5000 for enterprise (configurable by plan).
   - Refill rate = capacity per minute.
   - Maximum burst = 2x capacity (allows short spikes).

2. **Secondary limit:** Per-route token bucket for expensive endpoints (e.g., 10 req/min per integration for export endpoints).

3. **Headers:** Always return `X-RateLimit-*` on every request. Differentiate `Retry-After` for rate limits vs. monthly quota in the error body.

4. **Isolation:** No integration can consume more than 50% of its parent tenant's global capacity within a 1-minute window. This prevents a single bad actor from starving other integrations.

5. **Observability:** Metrics at the integration level, logs for blocked requests, and alerts for anomalous throttling rates.

6. **Fallthrough:** If the rate limiter data store is unreachable, allow the request (fail-open) but log the incident. A degraded experience is better than a full outage.

Rate limiting is not just about traffic shaping—it is about trust. When clients understand exactly why they were blocked and when they can retry, they adapt. When tenants see that a noisy integration does not take down their entire operation, they stay. Design for that trust from day one.
````
