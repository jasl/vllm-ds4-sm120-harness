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
- Elapsed seconds: 18.115011
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
# The Multi-Tenant Balance: Designing Rate Limits That Protect Without Punishing

Backend engineers often conflate several related but distinct concepts when designing API access control. For a multi-tenant API serving both small teams and enterprise customers, getting this wrong means either allowing a noisy integration to degrade service for everyone, or frustrating legitimate users with false positives. This article breaks down how to design rate limiting that distinguishes between authentication, quotas, and limits—and that scales in fairness across tenants of wildly different sizes.

## 1. Authentication, Authorization, Quotas, and Rate Limits: The Four Layers

Most API design discussions blur these terms, but each serves a separate purpose:

**Authentication** answers *who you are*. It’s the token, API key, or OAuth handshake that identifies the client. Without it, no other layer can act.

**Authorization** answers *what you are allowed to do*. It’s the policy layer: can this tenant write to the analytics endpoint? Can this user delete other users’ data? Authorization is about permissions, not volume.

**Quotas** answer *how much you are allowed to consume over a long period*. Quotas are contractual limits: “Your plan allows 1 million requests per month.” They are typically enforced as hard caps after the fact, or as soft warnings. Quotas are rarely enforced in real-time because they are tied to billing.

**Rate limits** answer *how fast you are allowed to consume*. They protect the system’s stability moment-to-moment. A quota might say “10,000 requests per month,” but a rate limit says “no more than 100 requests per second.” Rate limits are the circuit breaker that prevents a single tenant from overwhelming shared infrastructure.

In a multi-tenant system, rate limits must be tenant-aware and plan-aware. A small team with 10 requests/second should not be treated the same as an enterprise tenant with 1,000 requests/second, but both must be protected from abusive behavior.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window: Practical Trade-offs

The three common algorithms behave quite differently under real traffic patterns.

**Fixed window** divides time into discrete buckets (e.g., one per minute). It’s simple to implement and understand. However, it suffers from “burst at the boundary” problems: if a tenant sends 100 requests at 11:59:59 and another 100 at 12:00:01, they effectively get 200 requests in two seconds. This defeats the purpose of rate limiting. Fixed windows are acceptable only for very coarse limits with wide windows, and even then only as a first approximation.

**Sliding window log** (or sliding window counter) tracks timestamps per request and slides the window continuously. It solves the boundary problem but introduces memory overhead—each request creates a record. For high-throughput services, this becomes expensive to store and query. Many implementations approximate it with a counter and a timestamp of the window start, which reintroduces some boundary issues.

**Token bucket** is the gold standard for multi-tenant API rate limiting. It models a bucket that fills at a steady rate (refill rate) and holds a maximum number of tokens (burst capacity). A tenant can use tokens as fast as they want until the bucket empties, then must wait for refill. The key advantage: a tenant with low average usage can still handle sudden bursts (e.g., a webhook flood), while a tenant that saturates the refill rate is smoothly throttled. Token bucket is simple to implement with a counter and a last-refill timestamp per tenant, has bounded memory, and naturally allows bursts—exactly what small teams need and large enterprises require.

**Recommendation**: Implement token bucket per tenant, with bucket size (burst) and refill rate configurable per plan. For enterprise tenants, increase both parameters; for small teams, keep them modest.

## 3. Avoiding Punishment of an Entire Tenant for One Noisy Integration

The worst outcome in multi-tenant rate limiting: a single customer’s misbehaving integration (e.g., an infinite retry loop) exhausts the tenant’s global rate limit, blocking all other legitimate integrations for that tenant. This is not just an engineering failure—it’s a customer support disaster.

The solution is **hierarchical or nested rate limits**. Implement at least two tiers:

- **Per-API-key level**: Each integration (API key) has its own token bucket. A noisy key can exhaust its own bucket and be throttled.
- **Per-tenant level**: A second, larger bucket that sums across all API keys for that tenant. This prevents a single key from consuming the tenant’s entire allocation, but also prevents the tenant from exceeding its total plan limit.

When a per-key bucket empties, the client for that key receives a 429. Other keys for the same tenant continue unaffected. Only when the tenant-level bucket is exhausted do all keys for that tenant get throttled—and only then should an alert fire, because that suggests a systemic problem (e.g., the tenant’s total usage exceeds their contracted plan, or there is a DDoS).

Additionally, implement a **concurrency limiter** alongside the rate limiter. Rate limits control request volume over time; concurrency limits control how many simultaneous connections or inflight requests a single key can maintain. A retry loop that keeps connections open can exhaust server resources faster than a rate limit can catch it. A concurrency limit (e.g., max 5 inflight requests per API key) acts as a softer, faster-acting backpressure.

## 4. Headers and Error Messages: Transparency for Clients

Rate limit feedback must be clear, actionable, and consistent. The industry-standard headers are:

- `X-RateLimit-Limit`: The maximum number of requests allowed in the current window (or the burst capacity for token bucket). For per-key limits, this is the key’s bucket size.
- `X-RateLimit-Remaining`: The number of requests remaining in the current bucket. This lets clients self-throttle.
- `X-RateLimit-Reset`: A Unix timestamp indicating when the bucket will fully refill (or the window will reset). For token bucket, you can calculate this as `now + (empty_tokens / refill_rate)`.
- `Retry-After`: If a 429 is returned, the number of seconds the client should wait before retrying. This is mandatory for proper client backoff.

The 429 response body should include a structured JSON object:

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "API rate limit exceeded for API key 'abc123'. Retry after 30 seconds.",
    "rate_limit": {
      "limit": 100,
      "remaining": 0,
      "reset_at": 1735689600
    }
  }
}
```

Distinguish between per-key and per-tenant limits in the error message. If a per-key limit is hit, say so explicitly. If the tenant-level limit is hit, include the tenant ID and a message like “Your tenant’s total request volume has exceeded its plan limit.”

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting is only useful if you know it’s working—and not blocking traffic you want.

**Metrics to track** (per tenant, per API key, aggregated):

- **Requests total**: Total requests served (not throttled).
- **Requests throttled**: Count of 429 responses.
- **Throttle rate**: Throttled / Total, monitored per tenant.
- **Token bucket fill level**: Average usage vs. refill rate. This tells you how close each tenant is to their limit under normal conditions.
- **Concurrency**: Current in-flight requests per key.

**Logs** should record every 429 with: tenant ID, API key, endpoint, request path, rate limit tier hit (key vs. tenant), and the token bucket state. This allows post-mortem analysis of whether a noisy integration was legitimately abusive or the limit was too tight.

**Alerts** – set thresholds carefully:

- **Per-key throttle rate > 30%** for a given key over 5 minutes: likely a misbehaving client. Notify the tenant’s team or auto-disable the key after confirmation.
- **Per-tenant throttle rate > 50%**: critical. This means the tenant is hitting its global limit, which blocks all their integrations. Investigate whether the tenant needs a plan upgrade or has a compromised key.
- **System-wide throttle rate > 10%**: the infrastructure may be under-provisioned, or a burst of legitimate traffic is being blocked incorrectly.

Crucially, track false positives. Compare throttled requests against client retry behavior: if clients retry after 429 and succeed, the limit is working. If they retry and still get 429, the throttle may be too aggressive for their use case. Monitor customer support tickets mentioning “429” to correlate.

The goal of observability is not just to see when limits are hit, but to verify that the limits are set at the right level: protecting reliability while allowing legitimate traffic to pass smoothly. If a small team’s integration consistently operates at 95% of its limit, consider raising their limit or suggesting a plan upgrade—not forcing them to refactor.

## Recommended Baseline Design

For a multi-tenant API serving small teams and enterprise customers, start with this configuration:

1. **Per API key**: Token bucket with burst = 50, refill rate = 10/second (allows short bursts but sustainable at 10 rps).
2. **Per tenant**: Token bucket with burst = 500, refill rate = 100/second (sum of all keys).
3. **Concurrency limiter**: Max 10 in-flight requests per API key.
4. **Enterprise plan overrides**: Custom bucket sizes (e.g., burst = 1000, refill = 200/s) configured per tenant.
5. **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After` on 429.
6. **Observability**: Metrics for per-key and per-tenant throttle rates; alert when per-tenant throttle exceeds 50% over 5 minutes.

This design gives small teams the burst capacity they need for normal operations while preventing any single integration from degrading service for others. Enterprise tenants get room to scale, but still have hard boundaries that protect the shared infrastructure. The key insight: rate limiting should be as fine-grained as your authentication model allows—per key, per user, per endpoint—and always with a tenant-level safety net.
````
