# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-v4-flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: expectation checks skipped
- Detail: `expectation checks skipped`
- Elapsed seconds: 26.079089
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "completion_tokens": 2309, "total_tokens": 2461, "prompt_tokens_details": {"cached_tokens": 128}, "completion_tokens_details": {"reasoning_tokens": 165}, "prompt_cache_hit_tokens": 128, "prompt_cache_miss_tokens": 24}`
- Prompt tokens: 152
- Completion tokens: 2309
- Total tokens: 2461

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

## Reasoning Content

```text
We need to write a technical article for backend engineers on designing rate limiting for a multi-tenant API. The article must be 800-1000 words, no code, no vendor-specific services. Topics: 1. Difference between auth, authorization, quotas, rate limits. 2. Token bucket vs fixed window vs sliding window practical. 3. Avoid punishing entire tenant for one noisy integration. 4. Headers and error messages. 5. Observability. Include a "recommended baseline design" section at end.

Plan: Write in a professional, instructive tone. Start with an engaging intro about challenges of multi-tenant rate limiting. Then address each point in order. Use clear explanations, no code. End with baseline design.

Word count target: 800-1000. Let's write.
```

## Assistant

````markdown
# Designing Rate Limiting for a Multi-Tenant API

Every backend engineer who has operated a multi-tenant API knows the tension: a single overzealous integration can degrade service for everyone, yet aggressive limits frustrate legitimate users. Rate limiting is the tool that balances reliability and fairness, but in a world where tenants range from a three-person startup to a Fortune 500 enterprise, “one size fits all” fails. This article walks through the core concepts, algorithm trade-offs, multi-tenant isolation strategies, client-facing protocols, and observability practices needed to build a rate limiter that protects your infrastructure without punishing your customers.

## 1. Authentication, Authorization, Quotas, and Rate Limits – The Four Layers

Engineers often conflate these terms, but they serve distinct purposes.

- **Authentication** verifies *who* the client is (e.g., API key, OAuth token). It answers “Can you prove your identity?”
- **Authorization** determines *what* that identity is allowed to do (e.g., read only, write access, admin scope). It answers “Do you have permission?”
- **Quotas** define *how much* a tenant can consume over a long period (e.g., 10,000 requests per month, 100 GB of storage). Quotas are enforced asynchronously, often after the fact, and are tied to billing tiers.
- **Rate limits** govern *how fast* a tenant can send requests over a short window (e.g., 100 requests per second). They are enforced synchronously and protect system stability.

A rate limiter sits after authentication and authorization but before quota enforcement. It rejects requests that exceed the allowed rate, returning `429 Too Many Requests`. Quota violations usually return `403 Forbidden` with a different error code. Understanding this layering prevents mixing up semantics: you can have a valid auth token, be authorized, still have quota remaining, yet be rate‑limited.

## 2. The Three Practical Algorithms

### Token Bucket
A token bucket holds a fixed number of tokens (capacity). Tokens are added at a steady rate (refill rate) up to the capacity. Each request consumes one token. Bursts are absorbed as long as tokens remain; after depletion, requests are throttled until new tokens arrive.

- *Pros*: Allows short bursts up to capacity; smooths traffic naturally. Easy to implement with a per-tenant counter and a timestamp.
- *Cons*: Requires either a persistent store or in‑memory state (lossy on restart). Can be tricky to tune capacity and refill rate for diverse tenants.
- *Best for*: APIs that need to handle spikes (e.g., batch imports) but still enforce a long‑term average.

### Fixed Window
Divide time into discrete windows (e.g., 1 second). Count requests in the current window. If the count exceeds the limit, reject until the window resets.

- *Pros*: Simple to implement, especially with Redis `INCR` and `EXPIRE`. Stateless per window.
- *Cons*: Suffers from “burst at the edge” – a client can send 100 requests at the end of window *n* and another 100 at the start of window *n+1*, effectively doubling throughput. This punishes infrastructure and is unfair to other tenants.
- *Best for*: Low‑precision limits where occasional spikes are acceptable (e.g., hourly quotas).

### Sliding Window
Instead of fixed boundaries, track timestamps of recent requests (sliding window log) or use a sliding counter based on overlapping windows. The algorithm sees the actual time interval of length `N` ending at the current request.

- *Pros*: Eliminates edge bursts. More accurate reflection of true rate.
- *Cons*: Higher memory or computational cost (e.g., storing timestamps, or approximating with two counters). Implementation complexity.
- *Best for*: Production APIs where fairness and precision matter. A common pragmatic approach is the *sliding window counter* (e.g., using Redis sorted sets or approximate counters).

**Practical recommendation**: For a multi‑tenant API, start with **token bucket** due to its burst tolerance and straightforward per‑tenant configuration. For stricter fairness, upgrade to a sliding window implementation that records timestamps but limits each tenant to, say, 200 entries in the log.

## 3. Tenant Isolation: Protecting the Whole from the One

In a multi‑tenant system, one tenant’s noisy integration (e.g., a misconfigured webhook retry storm) must not degrade service for others. Three principles achieve this:

1. **Per‑tenant limit buckets.** Each tenant (identified by API key) has its own rate limit counter. No shared state that could cause a single tenant to exhaust a global pool.
2. **Hierarchical limits.** Implement a two‑level hierarchy: a per‑tenant limit (e.g., 100 req/s) *and* a global limit for all tenants combined (e.g., 10,000 req/s). The global limit protects your origin servers even if many tenants simultaneously trigger spikes. When the global limit is hit, all tenants are throttled proportionally, but the per‑tenant limit already ensures most are well below the global ceiling.
3. **Separate “noisy tenant” monitoring and dynamic capping.** Detect tenants whose request rate exceeds, say, 10× their historical average. Automatically reduce their limit (soft throttle) or redirect to a lower‑priority queue. This allows the limit to adapt without an outage. Ensure the reduction is reversible once traffic normalizes.

Never use a per‑IP limit for authentication‑based APIs – multiple legitimate users behind a NAT would be punished together. Always key on the tenant’s API key or authenticated identity.

## 4. What to Tell the Client: Headers and Error Messages

A well‑designed rate limiter communicates *why* a request was rejected and *when* it can try again. These HTTP headers are standard:

- `X-RateLimit-Limit`: The maximum allowed requests per window (e.g., `100`).
- `X-RateLimit-Remaining`: Number of requests left in the current window (e.g., `23`).
- `X-RateLimit-Reset`: Unix timestamp (or seconds‑until‑reset) when the window resets.

For token bucket, you might include `X-RateLimit-Burst-Capacity` if you expose burst behavior.

**Error response body** for `429 Too Many Requests`:
```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit. Retry after 15 seconds.",
  "retry_after_seconds": 15
}
```
Always include the `Retry-After` header (in seconds) so clients can honor backoff without parsing the body. For quota violations, use a different error code (e.g., `quota_exceeded`) and a `403` status.

Additionally, consider sending a warning header (e.g., `X-RateLimit-Warning: 10 requests remaining`) when the remaining count drops below a threshold, so clients can slow down proactively.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting is only effective if you know it’s working – and not blocking legitimate traffic.

### Key Metrics (per tenant and global)
- **Requests allowed vs. throttled** (count per minute). A sudden spike in throttling for a specific tenant indicates a problem on their side; a global spike suggests your limits are too tight.
- **Current rate limit usage** (as percentage of limit). Alert when any tenant consistently uses >90% of its limit – they may need a tier upgrade.
- **Queue depth or wait time** if you use a queue before rate limiting. High wait times indicate your rate limiter is becoming a bottleneck.
- **Error rate** of the rate limiter itself (e.g., storage failures, timeouts). A misbehaving rate limiter can silently allow all traffic.

### Logs
Log every rate limit decision at a reasonable sampling rate (1:1000 or only on throttling). Include tenant ID, limit configuration, current count, and the action taken (allow/reject). Structured logs (JSON) make it easy to aggregate and query.

### Alerts
- **High throttling rate for a single tenant** (e.g., >50% of their requests are rejected). Could be a client bug or a DoS attempt.
- **Global throttling % exceeds 1%** – your infrastructure may be unable to handle legitimate load.
- **Sudden drop in global throttling** – possible that your rate limiter failed open (allowing all traffic). Monitor a “rate limiter healthy” heartbeat.

**Dashboard suggestion**: A single chart showing, for each of the top‑10 tenants, the ratio of allowed to throttled requests over time. Overlay with global CPU/network usage to correlate.

## Recommended Baseline Design

For a multi‑tenant API with teams ranging from small to enterprise:

- **Algorithm**: Token bucket per tenant with a capacity equal to 2× the sustained rate. Store state in a distributed cache (e.g., Redis). Use a faster but approximate variant if latency is critical.
- **Hierarchical limits**: Per‑tenant limit (configurable per plan) + a global limit set to 10× the estimated sum of all tenant limits.
- **Client communication**: Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` on every response, plus `Retry-After` on 429. Use a clear JSON error body.
- **Isolation**: Detect noisy tenants via rolling average and dynamically reduce their limit to 50% of plan allowance for 5 minutes. Notify the tenant through a webhook or email.
- **Observability**: Export per‑tenant and global metrics. Alert on any tenant exceeding 95% of their limit for >10 minutes. Log all throttling events with fractional sampling.

Rate limiting is not a static configuration – it must evolve with your traffic patterns and customer relationships. Start simple, instrument everything, and iterate based on real‑world behavior. Your API’s reliability – and your customers’ trust – depend on it.
````
