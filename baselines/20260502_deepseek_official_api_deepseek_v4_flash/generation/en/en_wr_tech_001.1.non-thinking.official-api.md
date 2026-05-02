# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-v4-flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `official-api`
- OK: `True`
- Status: PASS
- Check: expectation checks skipped
- Detail: `expectation checks skipped`
- Elapsed seconds: 29.733563
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "completion_tokens": 2294, "total_tokens": 2446, "prompt_tokens_details": {"cached_tokens": 0}, "prompt_cache_hit_tokens": 0, "prompt_cache_miss_tokens": 152}`
- Prompt tokens: 152
- Completion tokens: 2294
- Total tokens: 2446

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
# Throttle the Titans: Designing Rate Limits for a Multi-Tenant API

Rate limiting is one of those infrastructure decisions that, if done poorly, will make you famous for the wrong reasons. When your API serves both a three-person startup and a Fortune 500 enterprise, the wrong rate limit can bring down the entire system—or silence a paying customer just as they were about to close a deal. This article walks through the practical design decisions for a multi-tenant rate limiter that protects system reliability without punishing entire tenants for one bad actor.

## 1. Clearing the Terminology Fog

Before diving into algorithms, we need crisp definitions that your team will use in code reviews, runbooks, and incident postmortems.

- **Authentication**: “Who are you?” The API client proves identity via API keys, OAuth tokens, or mTLS certificates. Rate limiting should operate at an identity granularity (e.g., API key, user ID) but must never be confused with authentication—a rejected rate limit is a 429, not a 401.

- **Authorization**: “What are you allowed to do?” Determines access to specific resources (e.g., read vs. write, tenant-scoped data). Rate limits are orthogonal: an authorized request can still be throttled.

- **Quotas**: “How much can you use over a long period?” Quotas are cumulative (e.g., 10,000 requests per month) and reset on a billing cycle. They are enforced at the end of the period or preemptively after exhaustion. Exceed a quota? Return 403 with a billing message.

- **Rate Limits**: “How fast can you use it?” Rate limits protect system stability over short windows (seconds to minutes). Exceed a rate limit? Return 429 and tell the client to back off.

**Key rule for multi-tenancy**: quotas are per-tenant (or per-plan), while rate limits can be per-tenant *and* per-client. Overlapping them without confusion is the design challenge.

## 2. Three Algorithms in Practice

You will not use a leaky bucket or generic counter—those are academic exercises. Here are the three implementations you actually need to evaluate.

### Token Bucket (Smooth, Burst-Friendly)
- **How it works**: A bucket holds up to `B` tokens. Tokens refill at rate `R` per second. Each request consumes one token. A request passes if tokens exist; otherwise it’s rejected.
- **Why use it**: Allows natural bursts (e.g., a CI pipeline sending 50 requests at once) while enforcing a sustainable long-term rate. Ideal for enterprise integrations that batch operations.
- **Gotcha**: Memory cost—each client needs a bucket. For 10,000 clients, you need 10,000 counters in Redis. Fine with pipelining; death by OOM without.

### Fixed Window (Simple but Punishing)
- **How it works**: Partition time into buckets (e.g., 1-minute windows). Each client gets a counter per window. Counter resets at window boundary.
- **Why use it**: Easy to implement with a single Redis key per client per minute. Stateless if you use a background reset.
- **Gotcha**: The “traffic jam at the boundary” problem. A client can send 100 requests at 0:59 and 100 more at 1:01—200 requests in two seconds, even though the limit is 100/min. This can spike your database.

### Sliding Window (Fair but Complex)
- **How it works**: Maintain a rolling log of timestamps for each client. Calculate the number of requests in the last `N` seconds. Reject if above threshold.
- **Why use it**: Eliminates bursting at window boundaries. More accurate for real-time APIs.
- **Gotcha**: Memory and CPU overhead. Storing 10,000 timestamps per client is untenable at scale. Practical implementations use a sorted set in Redis with TTL, or approximate using a sliding window counter (e.g., combine two fixed windows weighted by overlap).

**Recommendation**: Use token bucket as the base algorithm. It is well-understood, burst-tolerant, and a single Redis key per client suffices. If you need precise near-real-time enforcement (e.g., for financial APIs), implement sliding window with approximate counters to keep memory bounded.

## 3. Don’t Punish the Tenant for One Noisy Integration

This is the single biggest mistake in multi-tenant rate limiting. Consider: a team’s CI system goes rogue and sends 10,000 requests per second. If you limit by tenant ID, you just blocked every other user in that tenant—including the CEO trying to fetch a dashboard.

**Solution: Hierarchical rate limiting.**

Define two levels of limits:

- **Tenant-level limit**: Total requests across all API keys in the tenant. This protects the backend from one tenant overwhelming the system.
- **Client-level limit** (per API key or per user): A stricter limit nested under the tenant limit.

But here’s the critical detail: **a client failure should not exhaust the tenant limit.** Use separate rate limit counters:

- A client hitting its client-level limit gets a 429 immediately.
- A client hitting the tenant-level limit is rare—only if the sum of all clients exceeds the tenant’s cap.

**How to implement**: Use two token buckets in series. First, check the client bucket. If it has tokens but the tenant bucket is empty, the request passes (the client still has its own burst allowance). Only if both are empty does the request fail. This way, a noisy client only hurts itself—the tenant bucket is a *circuit breaker*, not a per-request gate.

**Practical trick**: For enterprise tenants, expose a separate “integration” API key with its own sub-limits, so that the integration’s noise never touches the human users’ keys.

## 4. Headers and Error Messages That Don’t Make Clients Angry

Your API clients are engineers. They deserve clarity, not silence.

### Request Headers (to inform)
Include standard rate limit headers on every response (even successful ones:

- `X-RateLimit-Limit`: The maximum requests per window (e.g., 100).
- `X-RateLimit-Remaining`: How many requests left in the current window.
- `X-RateLimit-Reset`: Unix timestamp when the window resets.

Add a custom header for multi-tenancy context:

- `X-RateLimit-Scope`: `client` or `tenant` — tells the client which limit was evaluated.

### Response for Throttled Requests (429)
Return a JSON body (not HTML) with:

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the rate limit for API key 'prod-key-abc'. Retry after 15 seconds.",
  "scope": "client",
  "retry_after_seconds": 15
}
```

- `retry_after_seconds` must match the `Retry-After` header value (in seconds, not a date).
- If the limit is at the tenant level, include a different message: “This tenant has reached its global rate limit. Contact support to raise your plan limit.”

**Never return the same message for 429 and 403.** Clients will conflate “you’re out of money” with “you’re going too fast.” They need different remediation paths.

## 5. Observability: Are Your Limits Protecting or Blocking?

You will not know if your rate limits are effective without multi-dimensional observability.

### Metrics to Track (every rate limit decision)

- `rate_limit_decision_total` by `tenant_id`, `api_key_hash`, `decision` (allow | deny), `scope` (client | tenant). This lets you see which tenants are hitting client limits vs. tenant limits.
- `rate_limit_bucket_level` per client: the current token count in the bucket. Useful for detecting clients perpetually near zero (they may need a higher limit).
- `rate_limit_bypass_count`: number of requests that would have been denied but were allowed due to a “fail open” mishap (should be zero in steady state).

### Logs (for debugging)

Log every 429 with: `api_key_hash`, `tenant_id`, `client_ip`, `user_agent`, `path`, `current_rate`, `limit`. Aggregate these into a dashboard to spot clusters—e.g., a single enterprise tenant generating 80% of all 429s because of one misconfigured polling script.

### Alerts (don’t alert on every 429)

- **High-priority**: Tenant-level rate limit exceeded by more than 5% of requests for that tenant for 5 minutes. This indicates a tenant is about to be blocked globally, meaning a support ticket is imminent.
- **Medium-priority**: A single API key is responsible for >50% of all 429s in a tenant. This automation likely needs a backoff fix.
- **Low-priority (info)**: Overall rate limit rejection rate >1% of total requests system-wide. This may indicate capacity planning needs attention.

### Dashboard Design

Create a single page with two views:
1. **Per-tenant**: Shows request rate vs. limit, 429 rate, top noisy keys.
2. **System-wide**: Shows total throughput, average latency (rate limits should reduce latency for compliant clients by preventing queue build-up), and error budget burn rate.

If you see latency increasing *and* 429s low, you may not be limiting aggressively enough. If 429s are high but latency is stable, the limits are working but customers may be unhappy—check whether limits are too tight for legitimate use.

## Recommended Baseline Design

For most multi-tenant APIs serving teams to enterprises:

1. **Algorithm**: Token bucket per API key (client) and per tenant, with separate counters.
2. **Storage**: Redis with Lua scripting for atomic check-and-decrement. Use `EVALSHA` to avoid network overhead.
3. **Hierarchy**: Client bucket evaluated first; tenant bucket only checked if client bucket allows. A client exceeding its own limit does not consume tenant capacity—only errors that pass client check consume tenant tokens.
4. **Defaults**:
   - Client: 100 req/min, burst 20.
   - Tenant: 10,000 req/min (adjust by plan).
   - Enterprise: allow override to configurable limits via API.
5. **Headers**: Include all standard rate-limit headers plus scope in `X-RateLimit-Scope`.
6. **Observability**: Count every decision by tenant, key, and scope. Alert only on anomalous patterns.

Rate limiting is not a security feature—it is a reliability contract. Design it so that when your API is being hammered, the legitimate users never feel a thing, and the noisy ones get a clear, actionable error. Your customers (and your on-call rotations) will thank you.
````
