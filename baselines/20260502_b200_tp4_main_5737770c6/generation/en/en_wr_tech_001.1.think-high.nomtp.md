# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 15.347716
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2303, "completion_tokens": 2151, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2151
- Total tokens: 2303

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
# Throttle Wars: Designing Rate Limits That Don't Break Your Multi-Tenant API

Backend engineers love building APIs. We hate when they fall over. Rate limiting is the unsung hero of API reliability—but in a multi-tenant environment serving both small teams and enterprise customers, getting it wrong means either starving startups or enraging Fortune 500s. Let's design a system that scales with the tenant, not against them.

## 1. Four Concepts You Must Separate (Or Pay the Price)

Most engineers conflate these terms. They are not interchangeable.

**Authentication** answers "who are you?" It's the API key or OAuth token presented with each request. Without it, you can't even start rate limiting meaningfully.

**Authorization** answers "what are you allowed to do?" It's the permission model. A free-tier tenant might be forbidden from calling the `/batch` endpoint entirely. Authorization failures should return 403, not 429.

**Quotas** are cumulative, time-bound allowances. "Your plan includes 100,000 API calls per month." Quotas are enforced at the end of the billing period. They are not rate limits. A tenant can burn through their monthly quota in one hour—that's fine, but your infrastructure might not survive it.

**Rate limits** are burst-and-sustain controls. "You can send 50 requests per second." They protect your infrastructure from short-term spikes. A tenant with high monthly quota still needs polite per-second boundaries.

The failure mode when you conflate them: an enterprise customer who hit their monthly quota suddenly can't make any requests at all—even though their rate limit hasn't been breached. This creates cascading failures in their deployment pipeline. Don't do that.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window: The Practical Reality

**Fixed Window** is the simplest: "500 requests per minute" resets every 60 seconds on the clock. Problem: a client sends 500 requests at 11:59:59, then another 500 at 12:00:01. They just did 1000 requests in 2 seconds without technically violating any single window. Your backend sees a thundering herd. This is the most common "works in testing, fails in production" pattern.

**Sliding Window Log** tracks timestamps of individual requests. It's accurate but memory-inefficient at scale. For 10,000 tenants each making 100 req/s, you're storing 1M timestamps per second. Not practical without aggressive pruning.

**Token Bucket** is the pragmatic winner. Start with a bucket capacity (burst) and a refill rate (sustain). A tenant gets 1000 tokens with a refill of 50 tokens per second. They can burst to 1000, then settle at 50/sec. If they go idle, the bucket fills back to 1000. This naturally handles both spikes and steady state. Redis-backed token buckets are the industry standard for good reason—they're cheap to store (one integer + one timestamp per tenant), fast (O(1) set/check), and handle the quiet-then-burst pattern that real APIs face.

**Sliding Window Counter** sits between fixed and token bucket in complexity. You store two counters: current window and previous window. Approximate request count = previous_window_count * (1 - elapsed_fraction) + current_window_count. It smooths out the fixed window edge case without storing every timestamp. Works well if your traffic is predictable. Token bucket is more forgiving for uneven load.

**Bottom line**: Start with token bucket. It's the most forgiving for clients and the most defensible for your infrastructure.

## 3. Protecting Tenants From Themselves—and From Each Other

The cardinal sin of multi-tenant rate limiting: a noisy integration in Tenant A's workspace brings down Tenant A entirely.

Consider: Tenant A has 500 API keys across 4 different integrations. One integration goes rogue—sends 10,000 requests in 30 seconds. If you rate-limit at the tenant level, that single integration exhausts the shared pool. Every other integration stops working. The customer calls support irate that "your API is down."

**Three tiers of isolation**:

First, **key-level rate limits** that are stricter than tenant-level limits. Each API key gets its own bucket—say 20 req/s. Tenant-level limit is 200 req/s across all keys. One misbehaving key hits its 20 req/s ceiling and gets 429'd. The other 19 keys continue working. The noisy integration self-isolates.

Second, **priority sub-buckets** for critical endpoints. If the tenant has a read endpoint and a write endpoint, give writes a separate bucket. A burst of read requests shouldn't block status updates or data exports.

Third, **concurrent request limits** (max in-flight) separate from rate limits (max arrival rate). A single integration sending 50 requests that each take 30 seconds to process can exhaust connection pools even at low request-per-second rates. Set max concurrent per key at 5 or 10. This prevents long-running queries from consuming all worker threads.

## 4. Headers and Error Messages: The Client Engineer's Frenemy

Bad rate limiting makes clients blind. Good rate limiting tells them exactly what to do.

**Required response headers** on every request:

```
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 37
X-RateLimit-Reset: 1712345678
```

*Limit* is the maximum per window (usually a sliding window's effective rate). *Remaining* is the count of requests left in current window. *Reset* is the Unix timestamp when the window resets—critical for clients to know when they can try again.

**On 429 Too Many Requests**, add:

```
Retry-After: 12
```

This is the number of seconds the client should wait. Not the timestamp, not a request count. A single integer. Why? Because `sleep(retry_after)` is the simplest correct thing a client can do, and most client libraries handle this header natively.

**Error response body** should be JSON, but more importantly:

```json
{
  "error": "rate_limit_exceeded",
  "message": "API key key_abc123 exceeded 20 requests per second. Limit resets in 12 seconds.",
  "retry_after_seconds": 12,
  "key_limit": 20,
  "organization_id": "org_456"
}
```

Include the organization ID so client-side debugging can distinguish between "my key is throttled" versus "my org is throttled." Never return internal debug info (which bucket, which Redis shard). Be specific enough to debug, vague enough to not leak architecture.

## 5. Observability: Are You Protecting or Persecuting?

Rate limiting that you can't observe is guessing. Here's what matters:

**Metrics per tenant, per key, per endpoint**:

- `rate_limit_total`: total requests received
- `rate_limit_passed`: requests allowed through
- `rate_limit_blocked`: requests that returned 429
- `rate_limit_bucket_level`: current token count (0 = blocked, max = fully refilled)

Graph these over time. A tenant with consistent 0 bucket level is perpetually throttled—maybe their limits are too low. A tenant with bucket always at max is never throttled—maybe their limits are too generous.

**Metrics per shard/region** (not per vendor, but per logical partition):

- Request latency under throttling vs. not
- Error rate of the rate limiter itself (Redis timeouts, connection pool exhaustion)

**Alerts**:

- P50 latency increase >20% when rate limiting is active (your limiter might be too aggressive or your implementation slow)
- Any tenant hitting 429 >5% of their total requests for >15 minutes (they're either misconfigured or your limits are wrong)
- Rate limiter component error rate >0.1% (your infrastructure is failing)
- Same tenant hitting 429 on multiple keys simultaneously (possible DDoS or bug in your tenant-level limit)

**Logs**:

Every 429 should be logged with: tenant ID, key ID, endpoint, reason (key-level limit hit? tenant-level limit? concurrency limit?). Never log the full request body—that's a data leak. Do log request path and headers (user-agent especially—you'll see which libraries are misbehaving).

**Dashboards**:

Build one that shows "top 10 most throttled tenants" and "top 10 most blocked keys." If a single tenant dominates the blocked count, their limits might need adjustment—or they might have a buggy integration that needs a conversation.

## Recommended Baseline Design

1. **Token bucket algorithm** backed by Redis (one key per API key + one key per tenant). Burst = 2x sustained rate for enterprise, 1.5x for small teams.
2. **Two-tier limits**: per API key (stricter) and per tenant (aggregate). A key hitting its limit gets 429; the tenant's other keys continue working.
3. **Per-key concurrency limit** set to 10 for standard endpoints, 5 for compute-heavy endpoints.
4. **Three rate limit headers** on all responses. `Retry-After` header on all 429 responses with a human-readable JSON body containing the offending key ID and reset time.
5. **Separate rate limit buckets** for read vs. write endpoints. Writes get tighter limits to protect data integrity.
6. **Observability pipeline**: log every 429, metric every decision, alert when any tenant exceeds 5% 429 rate over 15 minutes or when the rate limiter component itself degrades.
7. **Quarterly review** of top-throttled tenants. Raise limits for legitimate usage patterns, reach out to abusive ones.

Rate limiting is a conversation with your customers, not a wall. When you separate authentication from authorization from quotas from rate limits, isolate noisy tenants gracefully, and expose clear signals, you build trust. Your API becomes known as reliable—not because it's slow, but because it's predictable. And in multi-tenant systems, predictability is reliability.
````
