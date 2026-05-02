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
- Elapsed seconds: 10.220339
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2352, "completion_tokens": 2200, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2200
- Total tokens: 2352

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
# Designing Rate Limiting for a Multi-Tenant API: Protecting Small Teams and Enterprise Customers

Rate limiting is often treated as a simple "throttle everything" afterthought, but in a multi-tenant API serving both small teams and enterprise customers, it becomes a complex reliability and fairness problem. A poorly designed rate limiter can silently ruin developer experience for a bootstrap startup while failing to protect infrastructure from an enterprise customer’s runaway batch job.

This article provides a design framework focused on practical trade-offs, not vendor-specific tools. We will clarify foundational concepts, compare the three most common rate-limiting algorithms, address per-tenant isolation, specify what to return to clients, and define the observability signals that tell you whether your limits are working.

## 1. Authentication vs. Authorization vs. Quotas vs. Rate Limits

Engineers often conflate these terms, leading to bad designs. Here is the precise distinction:

- **Authentication** answers: *Who is this request from?* It validates credentials (API keys, OAuth tokens). It does not control what they can do or how often.
- **Authorization** answers: *Is this request allowed to perform this action?* It checks permissions (read vs. write, access to specific resources). It does not manage frequency.
- **Quotas** define *how much total usage is allowed over a billing cycle* (e.g., 10,000 requests per month). Quotas are enforced at the end of a period and often result in a denial after the limit is hit. They are not meant to prevent short-term spikes.
- **Rate limits** define *how fast usage can occur in a short window* (e.g., 100 requests per second). They are designed to protect system stability, not to enforce business agreements. Rate limits should be much tighter than quotas.

**Design implication:** Rate limits must operate at sub-second granularity and should reset automatically. Quotas should be checked off the critical path (e.g., via eventual counters) and trigger a degraded response, not a hard rejection until the end of the month.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window

These three algorithms handle burstiness and fairness very differently.

### Fixed Window
Think of a minute-level counter resetting every 60 seconds. If a tenant sends 60 requests at 0:59 and 60 requests at 1:01, they get 120 requests in two seconds despite a limit of 100 per minute. Fixed windows are simple to implement but allow burst through at window boundaries. They also suffer from the "thundering herd" problem: at the start of each window, all clients rush in.

### Sliding Window (log-based)
This tracks timestamps for every request within a rolling window. If the window is 60 seconds, each new request checks how many timestamps fall within the last 60 seconds. This eliminates boundary bursts, but it requires storing each request timestamp for the entire window duration, which increases memory and time complexity (O(n) per check). It is precise but expensive, especially for high-throughput tenants.

### Token Bucket
A bucket holds up to `N` tokens. Tokens are added at a fixed rate (e.g., 10 tokens per second). Each request consumes one token. If the bucket is empty, the request is denied. This allows bursts up to the bucket size, then smooths out. It does not have the boundary issue of fixed windows, and it is O(1) per check. The downside: you need a timer to refill tokens, and a single large burst can still exhaust the bucket (design the bucket size accordingly).

**Practical recommendation:** Use **token bucket per tenant**. It is the best balance of low overhead and burst tolerance. Configure bucket size to allow short bursts (e.g., 2x the per-second rate) and refill rate equal to the allowed sustained rate. Sliding windows are only justified when you need exact counters for credit-based billing where burst behavior must be auditable to the millisecond.

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

A common mistake: a single API key, IP address, or integration (e.g., a webhook client, a misconfigured CI/CD pipeline) triggers the rate limit for the entire tenant, blocking all other services—including critical user-facing calls.

**Solution: Multi-level rate limiting with scopes.**

Implement rate limits at three granularities, evaluated in sequence:

1. **Global per-root-account (tenant):** The hard ceiling. This protects your infrastructure from a tenant going rogue. For a typical enterprise tenant, this might be 5,000 requests per second.
2. **Per-client-ID (sub-account, integration):** Each API key or client credential gets its own bucket. For example, a CI pipeline key has a 50 req/s limit, while a user-facing key has 200 req/s. This prevents one broken script from starving the tenant's production traffic.
3. **Per-route or per-action:** GraphQL mutations, file uploads, and expensive search endpoints should have lower limits than lightweight GET endpoints. Use a separate bucket per "cost group."

**When a per-client-ID limit is hit, reject *only that client*.** The tenant-level bucket is not consumed. The response should clearly indicate which client hit the limit and that the tenant itself has not been restricted. This avoids "hair-trigger" blocking of the whole account.

## 4. Headers and Error Messages for API Clients

Clients need deterministic signals to implement backoff and retry correctly.

### Required Response Headers (for every rate-limited request)
- `X-RateLimit-Limit`: The maximum requests allowed in the current window (e.g., `100`).
- `X-RateLimit-Remaining`: How many requests the current client can still make in this window (e.g., `42`). This should be the bucket's current token count, not a decremented counter, because token bucket refills continuously.
- `X-RateLimit-Reset`: A Unix timestamp (seconds) when the bucket will be at least partially refilled. For a token bucket, this is the time when the next token is added. It helps clients compute a precise retry delay.
- `Retry-After`: HTTP standard header indicating seconds to wait before retrying. Often the same as `X-RateLimit-Reset - now`.

### Error Body
When rate limited (HTTP 429), return a JSON body:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests for this integration. Retry after the specified time.",
  "scope": "client_id:ci_1234",
  "retry_after_seconds": 5
}
```
Do **not** say "Your account is blocked." Differentiate between client-scoped and tenant-scoped limits. If the *tenant* limit is hit, the message should say "Tenant-wide rate limit exceeded." This prevents support escalations where a user sees "rate limited" and cannot determine whether it is their integration or their entire account.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting that silently breaks legitimate usage is worse than no rate limiting. You need signals that distinguish "protection working" from "configuration too tight."

### Key Metrics
- `rate_limit.total_hits`: Total number of requests hitting any rate limit.
- `rate_limit.by_scope`: Split by tenant, client_id, and route. This identifies which integrations are consuming limits.
- `rate_limit.by_status`: Count of `429` responses vs. allowed requests for each scope. A high ratio for a specific client points to a misbehaving integration.
- `rate_limit.bucket_exhaustion_seconds`: How long a bucket stayed empty before being refilled. Long periods suggest the limit is too tight for normal traffic.
- `latency.p99` and `error_rate.5xx`: Correlate with rate limit enforcement. If P99 latency drops significantly after throttling kicks in, the rate limiter is doing its job. If both latency and error rates remain high *despite* throttling, the limit may be too low or the backend has a different bottleneck.

### Logs
Every rate-limited request should emit a structured log with: tenant_id, client_id, route, method, current bucket level, limit, and retry_after. Do not log every successful request; only log transitions (e.g., bucket dropped below 30%, or a limit was hit).

### Alerts
- **Critical:** Tenant-level limit hit >10 times per minute for any tenant. This indicates the tenant may be under attack or has a severely misconfigured integration.
- **Warning:** Any single client_id consistently hitting its limit for >5 minutes. Investigation likely reveals a loop or a batch job that should be rate-limited internally.
- **Informational:** Global rate limit utilization >80% across all tenants. This suggests you may need to scale capacity or redistribute load.
- **False positive guard:** Never alert on isolated spikes (e.g., 3 requests in one second hitting a 100 req/s limit). Alert only on sustained patterns.

## Recommended Baseline Design

1. **Algorithm:** Token bucket per tenant, per client ID, and per route cost group. Bucket size = 2x the allowed sustained rate. Refill = the allowed rate.
2. **Fail-closed:** If the rate limiter itself (e.g., Redis) is unreachable, default to *allow* but log aggressively. A brief bypass is better than downtime. If you must fail-closed, set a very low safety limit (e.g., 10 req/s globally) to avoid complete blackout.
3. **Response:** 429 with `X-RateLimit-*` headers and a clear error body differentiating client vs. tenant scope.
4. **Observability:** Expose rate limit counters as Prometheus-style metrics, log all 429s, and set alerts on sustained per-client or per-tenant limit exhaustion, not on brief spikes.
5. **Documentation:** Publish a rate limit policy page with examples of retry-after header use. Provide a small initial burst allowance for new clients to avoid immediate throttling during integration testing.

Rate limiting is not a binary "on/off" switch. It is a continuous negotiation between infrastructure capacity and client behavior. Design it with granular scopes, deterministic feedback, and observability that lets you tune limits without guesswork. Your small teams will appreciate the burst headroom, and your enterprise customers will respect the predictable boundaries.
````
