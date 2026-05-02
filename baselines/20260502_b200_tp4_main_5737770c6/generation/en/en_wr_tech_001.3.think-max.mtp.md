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
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 10.025341
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2281, "completion_tokens": 2129, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2129
- Total tokens: 2281

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
# Designing Rate Limiting for a Multi-Tenant API: Balancing Teams and Enterprises

When your API serves both small teams and enterprise customers, rate limiting becomes a strategic design decision—not just a technical safeguard. A poorly designed limiter will throttle a startup’s integration while letting a single noisy enterprise endpoint degrade service for everyone else. This article walks through the foundational concepts, algorithmic trade-offs, tenant isolation strategies, client communication, and observability patterns necessary to build a rate limiter that protects reliability without punishing legitimate use.

## 1. Authentication, Authorization, Quotas, and Rate Limits: Clearing the Confusion

These four concepts are often conflated, but they serve distinct purposes:

- **Authentication** verifies *who* the client is (e.g., API key, OAuth token). It answers: “Can you prove your identity?”
- **Authorization** determines *what* they are allowed to do (e.g., read vs. write, access to specific endpoints). It answers: “Are you permitted to perform this action?”
- **Quotas** are long-term, hard limits on resource consumption—often enforced per billing cycle. Example: “Your plan allows 1 million requests per month.” Quotas are checked after the request completes or cost is incurred.
- **Rate limits** are short-term, sliding constraints that protect system stability. They prevent a burst of requests from overwhelming resources. Example: “You may send 100 requests per second.” Rate limits are checked *before* the request is processed.

In a multi-tenant system, rate limits sit between authentication and quota enforcement. They are a real-time gate, not a post-hoc accounting mechanism.

## 2. Algorithm Selection: Token Bucket, Fixed Window, and Sliding Window

Each algorithm offers different trade-offs for burstiness, fairness, and implementation complexity.

### Token Bucket
A bucket holds a maximum number of tokens. Tokens are added at a fixed rate (e.g., 10 per second). A request consumes one token. If the bucket is empty, the request is denied.

- **Pros:** Allows natural bursts up to the bucket size. Smooths traffic without rigid windows.
- **Cons:** Hard to reason about at a glance—clients don’t “see” when tokens will refill.
- **Best for:** APIs where bursty traffic is expected (e.g., batch processing, webhook replays).

### Fixed Window
Divide time into fixed intervals (e.g., 1-second windows). Count requests in each window. If the count exceeds the limit, reject until the next window.

- **Pros:** Simple to implement and monitor.
- **Cons:** Suffers from “traffic spikes at boundaries”—a client can send double the limit if they hit the end of one window and the start of the next.
- **Best for:** Low-traffic internal tools where burstiness is acceptable.

### Sliding Window (Log or Counter)
Track request timestamps in a moving window (e.g., last 60 seconds). A common approach is a sliding window counter that weights partial intervals.

- **Pros:** Fairer than fixed window; no boundary spikes. Better for high-traffic enterprise integrations.
- **Cons:** More memory and computational overhead (especially for high-cardinality tenants).
- **Best for:** Production APIs where predictable limits and fairness matter.

**Practical recommendation:** Use token bucket per tenant for its burst-tolerance, but cap the bucket size to no more than 2x the sustained rate. This prevents a single integration from hogging capacity.

## 3. Tenant Isolation: Avoiding Punishment for a Noisy Neighbor

The cardinal sin of multi-tenant rate limiting is applying a global limit across all tenants. A single misbehaving integration (e.g., a buggy retry loop) can exhaust the shared pool, starving small teams.

**Strategy 1: Per-Tenant Buckets**
Each tenant (identified by their API key or account ID) gets its own token bucket. The bucket refill rate is based on their plan (e.g., 10 req/s for small teams, 1000 req/s for enterprise). This is the simplest isolation model.

**Strategy 2: Hierarchical Buckets**
For complex cases (e.g., a tenant with many integrations), introduce sub-buckets per integration key or IP. The tenant has a global bucket, and each integration has a smaller bucket that draws from the tenant’s token pool. If one integration goes rogue, it exhausts only its own sub-bucket, not the tenant’s entire allocation.

**Strategy 3: Priority over Shaping**
Never hard-reject a tenant’s request if their limit is exceeded but system capacity is free. Instead, queue the request with a decaying priority. This prevents false positives when a tenant briefly bursts during a quiet period.

**Anti-pattern:** Do **not** use a single global counter and deny the loudest tenants. Always isolate at the tenant level, and consider isolation per integration within enterprise tenants.

## 4. Client Communication: Headers and Error Messages

Clients need to know *what* they hit, *when* they can retry, and *why* they were limited. Return these HTTP headers on every response:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 423
X-RateLimit-Reset: 1620000000  (Unix timestamp)
```

- `X-RateLimit-Limit`: The maximum requests allowed in the current window.
- `X-RateLimit-Remaining`: Count of remaining requests in the current window.
- `X-RateLimit-Reset`: When the window resets (or when the token bucket will refill to capacity).

When a request is rejected, return **429 Too Many Requests** with a JSON body:

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "You have exceeded the rate limit of 1000 requests per minute. Please retry at the time specified in the Retry-After header.",
    "retry_after_seconds": 15,
    "type": "rate_limit"
  }
}
```

Include the `Retry-After` header (in seconds) as a machine-readable hint. Never return a 500 or 403—a 429 is semantically correct and triggers appropriate client-side retry logic.

**Additional guidance for enterprise customers:** Some clients cannot parse custom headers. Provide a `Retry-After` header in two formats: integer seconds (preferred) and an HTTP-date string. Document that all enterprise integrations should respect the `Retry-After` header, not a hard-coded delay.

## 5. Observability: Metrics, Logs, and Alerts

Your rate limiter must be visible to both operations and customers. Without observability, you cannot tell whether limits are blocking attacks or blocking legitimate traffic.

**Metrics (counters and gauges):**

- `rate_limit.requests_total` – total requests (tagged by tenant, endpoint, HTTP status)
- `rate_limit.throttled_total` – number of 429 responses (tagged by tenant, reason: “burst,” “quota exceeded,” etc.)
- `rate_limit.token_bucket_remaining` – gauge per tenant; alerts when median falls below 10% for >5 minutes
- `rate_limit.p95_latency` – ensure the rate limiter itself does not add >1ms overhead

**Logs (structured, not verbose):**

- Log only on 429 responses or when a tenant’s bucket drops below 20%.
- Include: tenant ID, integration ID (if available), current limit, remaining tokens, time since last refill.
- Do *not* log every accepted request—this creates noise and cost.

**Alerts:**

- **High throttling rate:** If >5% of requests return 429 for any single tenant, alert. This indicates either a misconfigured client or a rogue integration.
- **Low bucket reserves:** If a tenant’s bucket consistently depletes (e.g., average remaining <10% over 10 minutes), their rate limit may be too low for their workload. Trigger a review, not an automatic escalation.
- **Global capacity saturation:** If aggregate system CPU or memory exceeds 80% and throttling is still low, your rate limits are too permissive—tighten them.

**Customer-visible dashboards:** Provide a per-tenant usage dashboard in your developer portal showing current limit, used requests, and throtting events. This reduces support tickets and lets users self-diagnose.

## Recommended Baseline Design

For most multi-tenant APIs serving teams and enterprises, start with this:

1. **Algorithm:** Per-tenant token bucket with a refill rate equal to the tenant’s plan limit and a burst capacity of 2x the refill rate. Use sliding window counters for tenants with custom high-limit plans.

2. **Isolation:** One bucket per tenant. For enterprise tenants, optionally expose sub-buckets per integration key (e.g., per API key or per webhook URL) so one misbehaving integration does not exhaust the entire tenant’s allowance.

3. **Precedence:** Rate limit before authorization, but after authentication. Do not rate-limit unauthenticated requests differently (this leaks information). Use a fast in-memory store (e.g., a distributed cache with atomic increment) to avoid database queries on every request.

4. **Headers and errors:** Always return `X-RateLimit-*` headers on every response. On 429, include `Retry-After` and a JSON error body with `retry_after_seconds`. Avoid vague messages like “rate limit exceeded”—tell them exactly what limit they hit.

5. **Observability:** Export per-tenant metrics of remaining tokens and throttling rate. Alert when any tenant’s throttling rate exceeds 5% for more than 5 minutes. Log only on throttling events and bucket exhaustion.

This design balances fairness (no noisy neighbor punishments), predictability (documented burst allowances), and operational safety (early warnings before capacity collapse). Test your limiters under burst scenarios before releasing them to production—and adjust refill rates based on real traffic patterns, not arbitrary plan limits.
````
