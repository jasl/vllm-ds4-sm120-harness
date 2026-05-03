# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 28.415973
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 1974, "completion_tokens": 1822, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 1822
- Total tokens: 1974

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
# Rate Limiting for Multi-Tenant APIs: A Practical Guide for Backend Engineers

## 1. Foundational Distinctions

Before designing a rate limiting system, we must disentangle four often-confused concepts:

- **Authentication** confirms *who* the caller is (e.g., API key, OAuth token).
- **Authorization** determines *what* the caller is allowed to do (e.g., read vs. write, specific endpoints).
- **Quotas** define *how much* a tenant can consume over a long period (e.g., 1 million requests per month). Quotas are enforced asynchronously or at billing boundaries.
- **Rate limits** control *how fast* a tenant can consume resources (e.g., 100 requests per second). They protect the system from short-term overload, not cumulative exhaustion.

A tenant might be properly authenticated and authorized, stay within their monthly quota, yet still exhaust shared resources if they burst too rapidly. Rate limits exist for that reason.

## 2. Algorithm Choices: Practical Trade-offs

### Token Bucket
- Accumulates tokens at a fixed rate (e.g., 10 tokens per second) up to a burst capacity (e.g., 100 tokens).
- A request consumes one token; if none remain, the request is denied.
- **Strengths:** Allows natural bursts—a tenant can use saved tokens during traffic spikes. Works well for most APIs.
- **Weakness:** Memory consumption per tenant is small, but coordinating token counts across distributed servers requires a shared store (Redis, etc.), adding latency on each check.

### Fixed Window
- Divides time into discrete windows (e.g., 1 minute). Counts requests per tenant; if count exceeds limit, reject until next window.
- **Strengths:** Simple to implement; low memory overhead.
- **Weakness:** Suffers from boundary bursts—at the edge of a window, traffic can double (end of one window + start of next). This can cause unexpected overload precisely when protection matters most.

### Sliding Window (Log or Counter)
- Maintains a time-ordered log of timestamps per tenant, or uses a sliding counter based on a rolling time interval.
- **Strengths:** Smooths out boundary effects; provides precise per-second control.
- **Weakness:** Higher memory and computational cost, especially with many tenants. A sliding log tracking every request can become expensive; a sliding counter (using a sorted set or weighted buckets) is more scalable but more complex.

**Recommendation:** Start with **token bucket**. It is the most forgiving for legitimate bursts and least surprising to developers. For high-throughput APIs, a single token bucket per tenant with a shared Redis-backed implementation is a proven pattern.

## 3. Avoiding Collective Punishment

One noisy integration (a misconfigured CI pipeline, a buggy client retry storm) should never degrade service for the entire tenant. Key techniques:

- **Per-client sub-keys.** Use the API key or a derived hash as the rate limiting key. If a tenant has 50 API keys, each key gets its own rate limit, isolated from others.
- **Tenant-level hard ceiling.** Even if individual keys are limited, aggregate all keys under the tenant ID and enforce a tenant-wide limit that is lower than the sum of per-key limits. This prevents a tenant using 100 keys to bypass the intended cap.
- **Resource-level limits.** Separate rate limits per endpoint or resource class (e.g., `/orders` vs. `/analytics`). A scraper hitting `/analytics` repeatedly should not starve `/orders` requests from the same tenant.
- **Priority lanes.** Enterprise customers may be assigned higher per-key limits, but still share a tenant ceiling. Within that ceiling, you can implement weighted priority—enterprise requests get 80% of the burst capacity, while team-tier requests cannot consume more than 20% during contention. This is optional but fair.

## 4. Headers and Error Responses

Clients must be able to adapt their behavior without guesswork. Standardize these response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 23
X-RateLimit-Reset: 1623456789
Retry-After: 5
```

- `X-RateLimit-Limit`: The maximum requests allowed in the current window (or token replenish rate, depending on algorithm).
- `X-RateLimit-Remaining`: How many requests the client can still make before hitting the limit.
- `X-RateLimit-Reset`: Unix timestamp when the counting window resets (or when the token bucket will have at least one token).
- `Retry-After`: Seconds the client should wait before retrying. Send this only on the 429 response.

**On rejection**, return HTTP 429 Too Many Requests with a JSON body:

```json
{
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "API rate limit exceeded for this API key. Retry after the time specified in Retry-After header.",
  "retry_after_seconds": 5,
  "rate_limit_type": "per_key"
}
```

Include the `rate_limit_type` field so clients can distinguish per-key limits from tenant-level or endpoint-level limits. This aids debugging.

## 5. Observability: Protecting Without Blocking

Rate limits are useless if you cannot tell whether they are working. Instrument at three levels:

### Metrics (counters and histograms)
- **Requests allowed vs. blocked** per tenant, per endpoint, per key.
- **Current token count remaining** (or requests in window) per tenant.
- **Rate limit decision latency**—the time spent checking and eventually rejecting a request. If this exceeds 5ms on average, your rate limiting store is a bottleneck.
- **Burst utilization**: percentage of tenants using >80% of their allowed burst. This signals imminent throttling.

### Logs (structured, sampled)
- Log every rate limit rejection with tenant ID, key ID, endpoint, and current counts.
- Sample allowed requests at 1% to reduce volume, but log 100% of rejected requests.
- Include a `ratelimit_debug_id` in each log line that links to a trace of the decision path (which limit was hit, what was the remaining count).

### Alerts (meaningful thresholds)
- **P50/P99 of per-tenant rate limit utilization** > 80% for a sustained period → tenant may be hitting limits; investigate if configuration needs adjustment.
- **Global rate limit rejection rate** > 5% of total traffic → something is misconfigured or an attack is ongoing.
- **Rate limit check latency** > 50ms P99 → the backing store or algorithm is too slow.
- **Single tenant rejection rate** > 20% of its own traffic → likely client bug or integration error; contact tenant.

Crucially, do not alert on “rate limit block events” in isolation. A 2% block rate might be normal; instead, alert on *deviations from baseline* per tenant.

## Recommended Baseline Design

1. **Algorithm:** Token bucket per API key, with a shared Redis instance as the token store. Use Lua scripts for atomic operations.
2. **Keyspace:** Key format: `ratelimit:{tenant_id}:{key_id}:{endpoint_group}`. Tenant-level limit key: `ratelimit:{tenant_id}:aggregate`.
3. **Limits:**
   - Per key: 100 tokens, refill 10 per second (burst = 100; sustained = 10/s).
   - Per tenant cap: 500 tokens, refill 50 per second (soft limit; can be overridden for enterprise).
4. **Headers:** As described in section 4, with `X-RateLimit-Type: per_key` and a separate `X-Tenant-RateLimit-Remaining` header for aggregate visibility.
5. **Observability:** Prometheus counters for `requests_allowed`, `requests_blocked`, `rate_limit_check_duration` (histogram), all tagged with `tenant`, `key`, `endpoint`. Alerts on P99 latency > 50ms and single-tenant block rate > 20% of that tenant’s traffic.
6. **Fallback:** If the rate limiting store is unreachable, log a critical warning and allow the request (fail open) with a deterministic max-burst count to prevent runaway consumption.

This design gives you isolation, fairness, and debuggability—without over-engineering for day one.
````
