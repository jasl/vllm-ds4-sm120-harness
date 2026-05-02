# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.09135
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2318, "completion_tokens": 2166, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2166
- Total tokens: 2318

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
# Fine-Grained Throttling: Designing Rate Limits for Multi-Tenant APIs

**By: [Your Name]**
*For backend engineers building shared infrastructure that must serve both scrappy startups and Fortune 500s.*

---

## 1. Foundational Distinctions

Before designing limits, we must clarify four often-conflated concepts:

- **Authentication** answers *who you are* (e.g., API key, JWT).
- **Authorization** answers *what you are allowed to do* (e.g., read, write, admin).
- **Quotas** are *hard ceilings* on resource usage over a billing or compliance period (e.g., 1 million requests per month). They prevent runaway costs but do not protect against short-term bursts.
- **Rate limits** are *short-term traffic control* (e.g., 100 requests per second). They protect system stability, not budgets.

A multi-tenant API must enforce all four independently. A small team may have low quotas but bursty patterns; an enterprise tenant may have high quotas but a commitment to sustained throughput. Rate limits should be tenant-aware, not quota-aware.

---

## 2. Algorithm Choices at a Practical Level

Three algorithms dominate production systems. Here is how they behave under real-world loads.

### Token Bucket
- **Mechanics**: A bucket holds N tokens, refilled at R tokens/second. Each request consumes one token. Unused tokens accumulate up to the bucket size.
- **Practical behavior**: Allows bursts up to N tokens while enforcing a sustained rate. A small team that makes no calls for 10 seconds can then fire 50 requests instantly (if N=50). An enterprise with a high refill rate can maintain steady throughput without bursts.
- **Pros**: Simple, natural for burst-friendly clients. No “reset-window” edge cases.
- **Cons**: Requires careful storage (distributed counters, atomic decrements). Token accounting can drift if clock skew is present.

### Fixed Window
- **Mechanics**: Divide time into fixed intervals (e.g., 1-second windows). Count requests per window. If count exceeds limit, reject until next window.
- **Practical behavior**: A request at t=0.999 and another at t=1.001 might both count toward the same window? No—they land in adjacent windows, letting through up to 2x the limit in a 2ms span. This “boundary effect” is well known.
- **Pros**: Trivial to implement (e.g., Redis `INCR` with TTL). Low memory.
- **Cons**: Bursty clients can exploit window edges. Harder to explain to customers (“Why did my request fail? The window resets in 200ms.”)

### Sliding Window (Log or Counter)
- **Mechanics**: Maintain a rolling window of the last N seconds. Count requests within that window. A sliding log keeps timestamps per request; a sliding counter uses weighted sub-buckets (e.g., 1-second granularity over a 10-second window).
- **Practical behavior**: No boundary spikes. A request at t=2999ms is compared against the sum of requests in [1000ms, 2999ms]—not just the current second.
- **Pros**: Most accurate; smooth throttling. Good for APIs where bursts disrupt reliability.
- **Cons**: Sliding logs require memory proportional to request rate. Sliding counters need slightly more complex logic (e.g., Redis Sorted Sets or Lua scripts).

**Recommendation**: Use token bucket for most endpoints. It combines burst tolerance (vital for small teams that batch operations) with a clear contractual rate. For endpoints that are especially latency-sensitive (webhook delivery, real-time sync), consider sliding window to eliminate boundary artifacts.

---

## 3. Avoiding the “Noisy Neighbor” Problem

A single misconfigured integration (e.g., a polling script with no backoff) should not degrade service for other customers of the same tenant. This requires two levels of containment:

### Tenant-Level Limits (Global)
- Each tenant has a top‑level rate limit (e.g., 5,000 requests/second for an enterprise, 500 for a small team). This is the hard ceiling for all API keys under that tenant.

### Integration-Level Limits (Per Key)
- Each API key (or authentication context) gets its own token bucket, typically 10–20% of the tenant limit. For example, if tenant limit is 1,000 req/s, each of their 5 keys gets a 200 req/s bucket. A noisy key exhausts only its own bucket; other keys continue normally.
- When an integration hits its per‑key limit, it receives a `429 Too Many Requests` with a `Retry-After` header. The tenant’s admin receives a warning, but other integrations are unaffected.

### Fallback: Shared Burst Pool
- If per‑key limits are too restrictive for legitimate parallel operations, add a shared burst pool. Each key can exceed its individual limit up to a tenant-wide cap, but only for a short burst (e.g., 200 additional tokens across all keys). This prevents a key from starving others while allowing temporary spikes.

**Key design rule**: Never use a single token bucket for a tenant. Always split into per-authentication-context buckets. The tenant limit becomes the sum of individual buckets plus optional overage.

---

## 4. Headers and Error Messages

Clients need clear signals to self-regulate. Return the following HTTP headers on every response (whether success or limit):

- `X-RateLimit-Limit`: The maximum requests per window (e.g., `1000`).
- `X-RateLimit-Remaining`: How many requests are left in the current window (e.g., `342`).
- `X-RateLimit-Reset`: Unix timestamp when the current window resets (or bucket refills).

On limit hit (`429`):
- `Retry-After`: Seconds until client can retry (e.g., `2`).
- Response body (JSON):
  ```json
  {
    "error": "rate_limit_exceeded",
    "message": "Request rate limit exceeded. You have made 1000 requests in the last second. Retry after 2 seconds.",
    "scope": "tenant",       // or "integration"
    "limit": 1000,
    "remaining": 0,
    "reset_at": 1717000000
  }
  ```

Avoid vague messages. Tell clients exactly *which* limit they hit (tenant-level vs. per‑key) and when they can try again. This reduces support tickets and enables automated backoff.

---

## 5. Observability: Proving Limits Work

Rate limiting is only useful if it demonstrably protects the system without harming legitimate traffic. Monitor these dimensions:

### Metrics (counters and histograms)

| Metric | Why |
|--------|-----|
| `rate_limit_decision_total` {tenant, key, result: allowed/denied} | Total throughput and rejection rate per tenant. |
| `rate_limit_throttled_requests` {tenant, key} | Frequency of `429` responses. High numbers suggest a misconfigured integration. |
| `rate_limit_bucket_utilization` {tenant} | Average fill level of token buckets. A consistently near‑zero bucket may mean too‑tight limits. |
| `latency_p99` across all requests | If rate limiting is working, latency should remain stable even during traffic spikes. |
| `error_budget_error_ratio` (e.g., error count / total requests) | Alert when ratio exceeds 5%—could be false positives from overly aggressive limiting. |

### Logs (structured, low‑volume)
- Log every `429` decision with tenant ID, key prefix, current limit, and `Retry-After` value.
- *Do not* log every allowed request—that would double your write load. Instead, sample allowed requests at 1%.

### Alerts
- **High rejection rate for a single tenant**: If a tenant’s 5‑minute rejection rate exceeds 10%, check whether they are legitimate (e.g., batch import) or a noisy neighbor.
- **System‑level p99 latency increase**: If latency climbs while rejection rates are low, your limits may be too generous.
- **Global rejection rate > 0.1%**: Indicates a systemic issue (e.g., too‑tight default limits or a DDoS masked as legitimate traffic).

**Most important**: Correlate rejection rates with downstream service health. If your database CPU spikes after you raise limits, your rate limits were doing their job. If your database is idle while you reject requests, tighten the limits.

---

## Recommended Baseline Design

For a multi-tenant API serving teams of 5 to enterprises of 10,000+ users:

1. **Algorithm**: Token bucket per API key (per authentication context), with a shared burst pool at the tenant level.
2. **Parameters**:
   - **Small team** (<10 keys): 100 req/s per key, bucket size 200. Tenant limit: 1,000 req/s.
   - **Enterprise** (10+ keys): 500 req/s per key, bucket size 1,000. Tenant limit: 5,000 req/s, with ability to raise after review.
3. **Storage**: Distributed Redis (or equivalent) with Lua scripts for atomic token operations. Use `EVALSHA` for efficiency.
4. **Request authentication**: Extract tenant ID and key ID from the API key prefix (e.g., `sk_tenant037_key012`).
5. **Headers**: Always return `X-RateLimit-*` headers. On `429`, include `Retry-After` and full error JSON.
6. **Monitoring**: Dashboard showing rejection rates per tenant, bucket fill levels, and downstream service health. Alert on any single tenant exceeding 10% rejection or any system‑wide p99 latency increase.

This design balances burst friendliness (small teams) with predictable throughput (enterprises), while isolating noisy integrations. Adjust the per‑key/tenant ratios as you observe real traffic patterns—but never remove the per‑key isolation. A multi‑tenant API is only as reliable as its least‑cooperative client. Rate limiting done right makes that client invisible to everyone else.
````
