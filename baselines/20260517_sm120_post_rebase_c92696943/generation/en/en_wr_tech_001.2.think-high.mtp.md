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
- Elapsed seconds: 15.139958
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2510, "completion_tokens": 2358, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2358
- Total tokens: 2510

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
We need to write a technical article for backend engineers on designing rate limiting for a multi-tenant API. The article should be 800-1000 words, no code, no vendor-specific services. Must cover five points: 1) auth vs. authorization vs. quotas vs. rate limits; 2) token bucket vs. fixed window vs. sliding window practical level; 3) avoid punishing entire tenant for one noisy integration; 4) headers and error messages; 5) observability metrics/logs/alerts. End with a "recommended baseline design" section.

I'll structure the article with a title, introduction, then sections for each point, then baseline design. Keep technical but accessible. Use practical examples. Avoid code. Focus on concepts.

Title idea: "Rate Limiting in Multi-Tenant APIs: Protecting Reliability Without Sacrificing Fairness"

Word count target: 800-1000. I'll write concisely.
```

## Assistant

````markdown
# Rate Limiting in Multi-Tenant APIs: Protecting Reliability Without Sacrificing Fairness

Backend engineers building APIs for both small teams and enterprise customers face a fundamental tension: how to protect system resources from abuse without punishing legitimate tenants. A naive rate‑limiting strategy can cripple a startup that shares a tenant ID with a data‑intensive integration while leaving a large enterprise free to monopolise capacity. This article dissects the design decisions that distinguish a fair, observable rate‑limiting system from a blunt instrument.

## 1. Authentication, Authorization, Quotas, and Rate Limits – The Four Layers

Engineers often conflate these concepts, but each serves a distinct purpose.

- **Authentication** answers *who* is calling. It validates identity via API keys, OAuth tokens, or mTLS. Authentication is binary – pass or fail.
- **Authorization** answers *what* they are allowed to do. It checks scope, role, or resource ACLs. A tenant might authenticate but be forbidden from deleting production data.
- **Quotas** define a *hard, non‑negotiable* limit over a long duration – 10,000 requests per day, 100 GB of storage. Exceeding a quota usually blocks further requests until the next billing cycle or a plan upgrade. Quotas are about *entitlement*.
- **Rate limits** manage *velocity* over short time windows – 100 requests per second, 5 concurrent connections. Rate limits protect system stability in real time. Unlike quotas, they are temporary; a rejected request can be retried after a short cooldown.

In a multi‑tenant system you must enforce all four. Rate limits sit between authentication/authorization and the actual business logic. They should check *after* authentication (so you know who the tenant is) but *before* authorization (to avoid wasting compute on a request that will be throttled).

## 2. Practical Algorithm Comparison: Token Bucket, Fixed Window, Sliding Window

Three algorithms dominate production rate limiting. Their practical trade‑offs matter more than academic purity.

- **Fixed Window** divides time into discrete buckets (e.g., every minute). Counter resets at each window boundary. *Problem*: a burst of requests at the end of one window and the beginning of the next can double allowed throughput. In a multi‑tenant system this can cause momentary overload without triggering the limit. Fixed window is simple to implement in a distributed cache but often leads to unfair bursts.
- **Sliding Window Log** keeps a timestamp per request and counts how many fall within the last N seconds. *Practical issue*: storing and scanning logs for every request is expensive at scale. An optimisation – sliding window *counter* – divides a window into sub‑windows (e.g., 1‑second buckets for a 60‑second window) and approximates the count by weighting older buckets. This reduces memory while still smoothing the burst problem.
- **Token Bucket** maintains a bucket that fills at a constant rate (e.g., 10 tokens per second) up to a burst capacity (e.g., 20). Each request consumes a token. *Advantage*: it naturally handles bursts (up to the bucket size) and enforces a long‑term average. In multi‑tenant APIs, token bucket is often the best choice because it allows small teams to burst when needed while protecting the system – the bucket size limits maximum instantaneous load per tenant.

**Recommendation**: use token bucket per tenant. The fill rate corresponds to your baseline capacity commitment per tenant; the bucket size is the allowed short‑term spike. This avoids the “double burst” of fixed windows and the memory overhead of sliding window logs.

## 3. Avoiding Tenant‑Wide Punishment for a Noisy Integration

The biggest failure in multi‑tenant rate limiting is a *global* limit that affects all sub‑resources equally. Suppose an enterprise tenant has a single noisy integration that polls an endpoint every 10ms. If the tenant’s total limit is 100 req/s, that single integration consumes 90% of the budget, starving all other integrations and users under the same tenant.

**Solution: Hierarchical rate limiting with cost attribution.**

- Define *degrees of granularity*: tenant level (highest), followed by API key (or client ID), and optionally endpoint + method.
- Each request is counted against *multiple* buckets: the specific API key bucket, the tenant aggregate, and optionally a service‑level bucket. The request passes only if *all* relevant buckets have capacity.
- The noisy integration exhausts its own key bucket first. Other keys under the same tenant remain unaffected. The tenant aggregate only blocks when the sum of *all* key‑level bursts exceeds the tenant’s hard cap (a safety net).

*Practical consequence*: a misbehaving third‑party script cannot take down the entire enterprise. Small teams that share a single key benefit from the tenant‑level burst allowance, but are still protected from one heavy API call in their integration.

Additionally, use *weighted rate limiting* for expensive endpoints. A heavy write operation might consume 5 tokens versus 1 for a lightweight read. This prevents a single costly request from “feeling” cheap.

## 4. Headers and Error Messages That Clients Understand

A well‑designed API returns rate limit information in every response, not just when limits are exceeded. This lets clients self‑regulate.

**Standard headers (inspired by IETF RateLimit draft):**

| Header | Purpose |
|--------|---------|
| `RateLimit-Limit` | The maximum requests allowed per window (e.g., 100) |
| `RateLimit-Remaining` | Number of requests remaining in the current window (for the key) |
| `RateLimit-Reset` | Unix timestamp (or UTC formatted) when the window resets |

For hierarchical limits, consider multiple header sets:
```
RateLimit-Limit: 100
RateLimit-Remaining: 67
RateLimit-Reset: 1690000000
X-RateLimit-Key-Limit: 50
X-RateLimit-Key-Remaining: 3
```

On limit exceeded, return HTTP `429 Too Many Requests` with:
- A `Retry-After` header (seconds to wait).
- A JSON error body containing the policy that was breached (tenant, key, or endpoint) and the reset time.
- Do *not* return `403 Forbidden` – that conflates authorization.

**Error body example:**
```json
{
  "error": "rate_limit_exceeded",
  "detail": "You have exceeded the per‑key rate limit. This limit resets at 2023-07-22T10:15:00Z.",
  "retry_after": 45
}
```

Include a `X-RateLimit-Scope` header to clarify which limit was hit (e.g., `tenant`, `key`, `endpoint`). This is invaluable for debugging noisy integrations.

## 5. Observability: Metrics, Logs, and Alerts

You cannot tune rate limits blind. Observability must answer: “Are limits protecting reliability without blocking legitimate use?”

**Metrics (expose as counters and histograms):**

- `rate_limit_counter{tenant, key, endpoint, decision}` – increment on `pass`, `block`, or `defer` (e.g., queued requests).
- `rate_limit_remaining{tenant, key}` – gauge of current tokens. Useful for dashboards showing how close tenants are to the edge.
- `rate_limit_latency_seconds` – histogram of time spent evaluating the limit (should be sub‑millisecond).
- `http_requests_total{tenant, status_code}` – correlate 429s with HTTP 2xx trends.

**Logs:**
- Log every rate‑limit block with tenant ID, key identifier, endpoint, current limit values, and client IP. Include a unique request ID for correlation.
- *Do not* log every successful rate‑limit check – that’s too noisy. Use sampled logging (e.g., 1 in 1000) for pass records.

**Alerts:**
- **High per‑tenant block rate**: if a tenant has >5% of its requests blocked for more than 5 minutes, alert. This could indicate a misconfigured client or a DDoS via a compromised key.
- **Low remaining capacity**: if the system‑wide `rate_limit_remaining` drops below 20% for sustained periods, alert the operations team. The system may need capacity scaling or limit adjustment.
- **Spike in `429` across all tenants**: suggests global resource exhaustion (e.g., database connection pool) rather than tenant misbehaviour.
- **Inverse alert**: if *no* tenant ever hits a limit, your limits are too generous – reliability is reduced and you have no headroom. Send an alert when peak block rate stays below 0.1% for 24 hours.

## Recommended Baseline Design

For a multi‑tenant API serving both small teams and enterprise customers, start with:

1. **Algorithm**: Token bucket per tenant *and* per API key. Fill rates sized for each tenant’s plan (e.g., small team: 50 req/s, burst 100; enterprise: 500 req/s, burst 1000). Key‑level limits default to 20% of tenant limit.
2. **Hierarchy**: Evaluate key bucket first, then tenant bucket only if key bucket has capacity. This avoids punishing the tenant for a single key.
3. **Headers**: Return `RateLimit-*` for the most restrictive level hit. Use `X-RateLimit-Key-*` and `X-RateLimit-Scope` headers for transparency.
4. **Error response**: HTTP 429 with `Retry-After`, structured JSON indicating which limit was exceeded.
5. **Observability**: Expose per‑tenant and per‑key counters; alert on high block rates and low system capacity; log all blocks with correlation IDs.

Iterate from there. Add endpoint‑specific cost weights as you learn which endpoints are expensive. Review limits quarterly with your largest tenants to ensure they still make sense. Effective rate limiting is not a one‑time configuration – it is a continuous optimisation between protecting your infrastructure and enabling your customers’ growth.
````
