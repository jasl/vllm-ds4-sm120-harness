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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.108232
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
# Leaky Faucets and Fair Shares: Designing Rate Limits for Multi‑Tenant APIs

You’ve built an API that serves both a five‑person startup and a Fortune 500 enterprise. The startup sends 10 requests per minute; the enterprise’s automated integration fires 10,000. When the enterprise hits a rate limit, the startup’s dashboard breaks because you designed a single global counter. Your users don’t care about “tenant isolation”—they care that their own requests succeed. This article walks through how to design a multi‑tenant rate limiter that protects reliability without punishing tenants for each other’s behavior.

## Distinguishing the Four Pillars of Access Control

Before drawing boxes, engineers must agree on vocabulary. Authentication, authorization, quotas, and rate limits address different problems and failure modes.

- **Authentication** answers *who you are*. It’s the API key, OAuth token, or JWT. The limiter operates *after* authentication—an unauthenticated request should be rejected before it reaches the rate limiter.

- **Authorization** answers *what you may do*. Even if a tenant has remaining quota, they may lack permission to call a specific endpoint. Rate limits should not duplicate authorization logic; they operate on already‑authorized requests.

- **Quotas** are *financial or contractual limits*. Example: “Your plan allows 100,000 API calls per month.” Quotas are enforced asynchronously (typically via billing systems) and allow brief overages with a soft “over‑age” notification.

- **Rate limits** are *operational limits* that prevent system overload. Example: “You may send 100 requests per second.” Rate limits are enforced synchronously and should be adapted dynamically as infrastructure health changes.

A well‑designed system checks authentication, then authorization, then rate limits, and finally deducts from the quota in an eventually‑consistent manner.

## Algorithmic Options: Token Bucket, Fixed Window, Sliding Window

Three algorithms dominate production rate limiters. Each has tradeoffs that matter in multi‑tenant scenarios.

**Fixed Window** partitions time into discrete buckets (e.g., one minute). The counter resets exactly at the minute boundary. This is simple to implement but suffers from *boundary bursts*—a tenant can send 100 requests at 00:59 and another 100 at 01:01, effectively doubling capacity across the boundary. For multi‑tenant systems, fixed windows amplify noise: one noisy integration can spike at the boundary, and the reset doesn’t smooth usage for quieter tenants.

**Sliding Window Log** keeps a timestamp for each request. It provides precise, memory‑intensive enforcement. For a tenant sending 1,000 requests/sec, you maintain a log of that many timestamps. In multi‑tenant systems with thousands of tenants, memory and garbage‑collection overhead become non‑trivial. Sliding window logs are academic purity that rarely survive production cost constraints.

**Token Bucket** is the pragmatic workhorse. A bucket holds a number of tokens; tokens are added at a fixed rate (the *fill rate*) up to a *burst capacity*. When a request arrives, it consumes one token. If the bucket is empty, the request is delayed or rejected. Token buckets naturally handle bursts: a tenant that has been idle for 10 seconds can send a burst of tokens, then settle back to the fill rate. In multi‑tenant systems, each tenant receives its own bucket, and the system can assign different fill rates and bursts per tier.

Practical recommendation: notional token bucket per tenant. Enforce with a distributed counter (e.g., Redis `INCR` with expiry, or an in‑memory bucket if you accept per‑process limits). The burst size should be at least 2× the fill rate per second to accommodate client retry spikes.

## Avoiding Tenant Punishment: Per-Tenant Isolation with Global Overrides

The cardinal sin is a single global counter. Tenants become correlated—one noisy integration causes all tenants to be throttled. The first step: **every rate limit decision must be scoped to a tenant identifier** (API key prefix, customer ID, or JWK key ID).

But isolated per‑tenant buckets have a hidden failure mode. Imagine your infrastructure can handle 10,000 requests per second total. If you give each tenant a 1,000‑req/sec bucket and you have 20 tenants, a simultaneous burst from all tenants overwhelms the backend. You need **two layers of concurrency protection**:

1. **Per‑tenant bucket**: enforces the contract per customer.
2. **Global capacity bucket**: enforces the total infrastructure capacity.

The global bucket shares tokens across tenants. When the global bucket is empty, *all* tenants are throttled—but critically, a request that fails the per‑tenant bucket is rejected before it touches the global bucket. This prevents one tenant’s overage from consuming global capacity intended for others.

Additionally, implement **integration‑level sub‑buckets**. If a tenant has five API keys (one for each integration), each key should have its own token bucket, nested under the tenant bucket. This prevents a misbehaving script from consuming all of the tenant’s capacity. Why does a noisy integration matter at the tenant level? Because the tenant pays the bill. Sub‑buckets let you reject the noisy integration while the tenant’s other keys remain unthrottled.

## HTTP Headers and Error Messages: Predictability over Surprise

Clients need deterministic feedback. Return these headers on every response:

- `X-RateLimit-Limit`: the maximum requests per window (for the tenant’s plan).
- `X-RateLimit-Remaining`: remaining requests in the current window.
- `X-RateLimit-Reset`: Unix timestamp of when the window resets (or when the bucket refills). Use a consistent epoch—not “seconds from now”—so clients can schedule retries precisely.
- `Retry-After`: number of seconds the client must wait. Return this *only* when throttled (HTTP 429). The value should be the estimated time until at least one token replenishes.

HTTP status code for rejection: **429 Too Many Requests**. Never use 503 (service unavailable) for rate limits—503 implies the server is overloaded, not that the client exceeded its allowance. A client that receives 429 should retry with exponential backoff based on `Retry-After`. A client that receives 503 may throttle back, but the signal is ambiguous.

Error body (JSON):

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit of 100 requests per second. Retry after 2 seconds.",
  "retry_after_seconds": 2
}
```

Keep the message actionable. Avoid vague phrasing like “too many requests.” Mention the limit and the retry interval.

## Observability: Metrics, Logs, Alerts That Tell a Story

Rate limiters are invisible when they work. When they fail, they fail loudly. Instrument these signals:

**Key metrics** (three cardinalities: tenant, endpoint, status code):

- `rate_limit_requests_total`: count of all requests entering the limiter, labeled by `tenant_id`, `endpoint`, `decision` (allowed vs. rejected).
- `rate_limit_bucket_usage`: for each tenant, current token count. Track as a gauge. Alert when a tenant’s usage consistently stays above 90% of their limit—this predicts future rejection and suggests the client needs a plan upgrade.
- `rate_limit_global_bucket_exhausted`: boolean gauge. If the global bucket is empty for more than 5 seconds, page the on‑call team. This indicates systemic overload that per‑tenant limits cannot mask.
- `rate_limit_integration_sub_bucket_rejection`: count of rejections due to an integration sub‑bucket, broken down by `tenant_id` and `integration_id`. This metric reveals which specific integration is abusive without alerting on the entire tenant.

**Logs** are for debugging, not alerting. Log when a request is rejected with the tenant ID, sub‑bucket ID (if any), and the `Retry-After` value. Do *not* log every allowed request—your log volume will exceed your request volume.

**Alerts** should be rare but meaningful:

- **P0 alert**: Global bucket exhausted for >5 seconds → backend capacity needs scaling.
- **P1 alert**: Any single tenant is >95% rejected for >1 minute → client misconfiguration or intentional abuse.
- **P2 warning**: A tenant’s global rejection rate exceeds 10% → possible integration issue; notify the customer success team.

## Recommended Baseline Design

For most small‑to‑enterprise APIs, start here:

- **Algorithm**: Token bucket per tenant, with per‑API‑key sub‑buckets.
- **Storage**: In‑memory counters for low‑latency (if single‑process), or a shared key‑value store with 1‑second TTL for distributed deployments. Avoid global locks; use atomic increment‑and‑expire.
- **Capacity tiers**: Three tiers—Small (10 req/s, burst 20), Medium (100 req/s, burst 200), Enterprise (negotiated per contract, burst 2× fill rate). Global capacity set to 80% of your infrastructure’s peak throughput.
- **Headers**: Always return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. Return `Retry-After` on 429.
- **Observability**: Export per‑tenant bucket usage as a histogram (not just a gauge), and set up a dashboard that shows the ratio of allowed/rejected per tenant per endpoint.

This design is not perfect—it’s a starting point. The enterprise that runs ETL jobs at midnight will need different limits than the startup’s real‑time dashboard. Your job is to make the system adaptable without making it fragile. Rate limiting is a social contract: you promise predictable behavior; the client promises to respect the headers. Build the instrument that enforces that contract fairly.
````
