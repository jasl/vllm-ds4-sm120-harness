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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 33.185063
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2277, "completion_tokens": 2125, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2125
- Total tokens: 2277

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
# Designing Fair Rate Limits for Multi-Tenant APIs Serving Teams and Enterprises

Rate limiting is one of those subjects where every engineer thinks they understand it—until they have to design it for a multi-tenant system that serves both a three-person startup and a Fortune 500 enterprise. One integration goes rogue, and suddenly all tenants sharing your infrastructure experience degraded performance. Your job as a backend engineer is to build a system that prevents noisy neighbors from harming others while preserving maximum throughput for legitimate traffic.

## Authentication, Authorization, Quotas, and Rate Limits: The Boundary

Before designing any limit, you need to understand the four distinct concepts that often get conflated:

- **Authentication** answers: *Who is making this request?* It’s the API key, OAuth token, or JWT that identifies the caller. Authentication says nothing about what they can do.

- **Authorization** answers: *Are they allowed to do this?* It determines whether a tenant’s role or subscription tier permits a specific action (e.g., “only enterprise tenants can use the bulk export endpoint”).

- **Quotas** answer: *How much total usage are they allowed over a long period?* A quota is a hard cap on total resource consumption—usually enforced monthly or daily. For example: “Tenant A may make 100,000 requests this month.” Quotas are used for billing and preventing runaway costs.

- **Rate limits** answer: *How fast can they use it right now?* Rate limits control instantaneous traffic to protect system stability. They are enforced per second or per minute and reset frequently.

The critical distinction: quotas protect your *business*, and rate limits protect your *infrastructure*. A tenant can hit their quota by submitting 100,000 requests over 30 days at a steady rate. A rate limit prevents them from doing it in five seconds.

## Algorithm Selection: Token Bucket, Fixed Window, and Sliding Window

### Fixed Window
The simplest approach divides time into discrete buckets (e.g., one-minute windows). Each window has a counter reset at the end. If the counter exceeds the limit, requests are rejected until the next window.

**Practical problem:** At the boundary between windows, a client can burst double the allowed rate—send 100 requests at 00:59 and another 100 at 01:01. The system sees two discrete windows with 100 requests each, but the client experienced 200 requests in two seconds. This defeats the purpose of rate limiting.

### Sliding Window Log
This stores a timestamp for each request within the current window. When a new request arrives, the system removes timestamps older than the window duration and counts the remaining. It provides precise control but incurs memory and compute overhead. For multi-tenant systems with thousands of concurrent tenants, this becomes expensive and prone to race conditions.

### Token Bucket
A bucket holds tokens that refill at a steady rate (e.g., 10 tokens per second). Each request consumes one token. If no tokens remain, the request is denied. The bucket has a maximum capacity (burst size).

**Why this wins for multi-tenant APIs:** Token bucket allows natural bursts—a team can send 50 requests instantly if the bucket is full (assuming capacity 50), then must wait as tokens refill. It smooths traffic without punishing the client for natural spikes. Implementation is straightforward: a counter, a last-refill timestamp, and a refill calculation formula. Memory cost per tenant is tiny.

**Practical recommendation:** Use a token bucket with: a refill rate proportional to the tenant’s tier, a burst capacity equal to at least the refill rate (to handle startup spikes), and per-endpoint token costs (e.g., a batch import costs 5 tokens).

## Avoiding Collective Punishment from Noisy Integrations

The most destructive pattern in multi-tenant rate limiting is applying a single global limit across all tenants. If one misconfigured polling script hits your API at 1,000 requests per second, the entire infrastructure might reject *everyone’s* requests. This is collective punishment.

**Design principle:** Rate limits must be *per-tenant* (per API key, per organization ID), with *no shared bucket*. Each tenant operates independently. But this is only the first level.

A single tenant can have multiple integrations—perhaps a webhook consumer and a cron job. If one integration is misbehaving, you should not block the tenant’s entire use of the API. The solution is *hierarchical rate limiting*:

1. **Global per-tenant bucket** (e.g., 1,000 tokens/second for the whole tenant).
2. **Per-integration sub-bucket** (e.g., 200 tokens/second per API key or source IP group).

Requests first deduct from the integration’s sub-bucket, then from the tenant’s global bucket. If the sub-bucket is empty but the global bucket has tokens, the request fails—but other integrations under the same tenant continue to function. This isolates noisy behavior to the specific integration that caused it.

Additionally, implement *read vs. write rate limits* separately. A polling script overwhelming GET endpoints should not block critical write operations like creating an invoice. Use two token buckets per tenant: one for reads, one for writes.

## Headers and Error Messages

Your API clients need to know exactly what is happening. Standardize on headers inspired by HTTP RateLimit (RFC 6585, updated by draft-ietf-httpapi-ratelimit-headers):

- `X-RateLimit-Limit`: The maximum requests per the window (e.g., 1000).
- `X-RateLimit-Remaining`: The tokens available for the current interval.
- `X-RateLimit-Reset`: Unix timestamp when the bucket will be full again (or when the next window starts). For token bucket: the time when the bucket will have 1 token again.
- `Retry-After`: Seconds the client must wait before retrying. Required for 429 responses.

**Error messages:** When returning HTTP 429 Too Many Requests, provide a JSON body explaining what happened and what the client can do:

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded your rate limit for read requests. Retry after 12 seconds.",
  "limit": 1000,
  "remaining": 0,
  "reset_at": "2025-04-10T14:32:05Z",
  "integration": "cron-job-backup-sync"
}
```

Include the integration identifier so developers can pinpoint which of their integrations caused the limit. This reduces support tickets dramatically.

**Crucially: never return ambiguous codes.** Use 429 for rate limit, 403 for authorization failures, and 401 for authentication. Don’t confuse them.

## Observability: Are Limits Protecting Reliability?

Rate limits are only useful if you know they are working correctly. Build observability into the system from day one.

### Metrics (expose to your monitoring dashboards)
- `rate_limit_requests_total` (by tenant tier, endpoint, status: allowed/denied)
- `rate_limit_bucket_remaining` (current tokens per tenant, sampled every 10 seconds)
- `rate_limit_denied_requests_by_integration` (top-10 noisy integrations per hour)
- `rate_limit_refill_lag` (difference between intended and actual refill time, to detect contention)

### Logs (structured, sampled to avoid log storms)
Log *when limits are approached* (remaining < 10%) and when they are exceeded. Do not log every allowed request. Include: tenant id, integration id, endpoint, request latency, token refill rate at that moment.

### Alerts
- **Denial rate spike:** If the percentage of denied requests exceeds 5% of total traffic for more than 5 minutes, investigate.
- **Single tenant dominating denial:** If one tenant accounts for >80% of all 429 responses, alert. They might have a bug.
- **Rate limit underutilization:** If *no* tenant ever hits their limit, the limits are too permissive and offer no protection.
- **Latency correlation:** Track p99 latency before and after implementing rate limits. If latency drops while denial rates remain low, limits are working. If denial rates spike and latency also spikes, the limits are too aggressive.

### A Note on Fairness
Use *weighted fairness*: enterprise tenants get higher token refill rates, but each token should cost the same server resources. If a massive enterprise tenant uses 10x the tokens of a small team, they should contribute 10x the server cost. This means your cost allocation model must align with your rate limit structure, otherwise you will face profitable abuse.

## Recommended Baseline Design

Start with the following configuration for a general-purpose REST API:

1. **Algorithm:** Token bucket per tenant, per read/write dimension.
2. **Default limits:** Small team (100 tokens/second, burst 150). Medium team (500 tokens/second, burst 750). Enterprise (5,000 tokens/second, burst 7,500). Adjust based on server capacity per host.
3. **Sub-buckets:** One per API key per endpoint group (reads vs. writes). Enterprise sub-bucket: 1,000 tokens/second per integration.
4. **Headers:** `X-RateLimit-Limit`, `-Remaining`, `-Reset` on every response. `Retry-After` on 429.
5. **Error response:** JSON with `error`, `message`, `limit`, `remaining`, `reset_at`, `integration`.
6. **Observability:** Log all rate limit denial events. Alert when any tenant exceeds 10% denial rate on writes. Expose bucket states to Prometheus-style metrics.
7. **Fail-open on outage:** If the rate limit store (Redis or equivalent) is unreachable, allow requests but log and alert. Degrading availability to protect rate limiting defeats the purpose.

Rate limiting is a dynamic system, not a static config. Monitor, tune, and communicate changes to tenants. Your goal is not to be a gatekeeper—it is to be a traffic controller that keeps the highway flowing for everyone.
````
