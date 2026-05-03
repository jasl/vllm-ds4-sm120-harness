# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `3`
- Thinking mode: `think-high`
- Thinking strength: `high`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 30.583305
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2112, "completion_tokens": 1960, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 1960
- Total tokens: 2112

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
# Designing Rate Limiting for Multi-Tenant APIs: Balancing Protection and Fairness

## The Four Pillars of Access Control

Before designing rate limiting, we must distinguish four concepts that are often conflated:

**Authentication** answers "Who are you?" – verifying identity via API keys, OAuth tokens, or mTLS certificates. It is the gate.

**Authorization** answers "What are you allowed to do?" – checking permissions at the resource or action level (e.g., a read-only key cannot issue DELETE requests).

**Quotas** define hard limits over a billing or planning period: "Your plan allows 100,000 requests per month." Quotas are enforced after the fact and are about capacity planning.

**Rate limits** control request velocity over short windows (seconds to minutes) to protect system stability. They are preventive, not retrospective.

A multi-tenant API must layer these: authenticate first, then authorize, then apply rate limits, with quotas checked asynchronously (e.g., via background reconciliation). Rate limiting should never substitute for proper authentication or authorization.

## Practical Comparison of Algorithms

**Fixed window** divides time into discrete buckets (e.g., 1-minute intervals). At minute start, the counter resets. *Problem:* A burst at the end of one window and start of the next can double the allowed traffic within seconds. Example: 100 req/min yields 198 requests in two adjacent seconds if timed at boundaries.

**Sliding window log** records each request timestamp and counts unique timestamps within the window. *Problem:* Memory and computation grow with request volume. For high-throughput tenants, this becomes expensive to evaluate on every request.

**Sliding window counter** approximates sliding behavior by tracking the current window's count plus a weighted portion of the previous window. It's a pragmatic compromise between accuracy and overhead. *Practical insight:* The weighting formula (previous_count * (window_duration - elapsed) / window_duration) works well when your backend operates at sub-millisecond latency.

**Token bucket** maintains a bucket of tokens that refill at a steady rate (e.g., 10 tokens per second). Each request consumes one token; bursts up to the bucket size are allowed, but sustained rate is capped. *Why it wins:* It naturally absorbs short bursts (a team deploying code might spike for 30 seconds) while preventing sustained overload. It requires only two values (tokens, last refill timestamp) per key, making it memory-efficient even for millions of tenants.

For multi-tenant APIs with both small teams (who benefit from bursts) and enterprise customers (who need predictable steady rates), token bucket is the recommended starting point.

## Avoiding Tenant-Wide Collateral Damage

A single noisy integration—a misconfigured cron job, a chatty webhook consumer, or an aggressive polling script—should not degrade service for other customers of the same tenant.

**Hierarchical rate limiting** is the solution. Maintain at least two levels:

1. **Per-API-key** (or per-integration) limit: the fine-grained control that stops the noisy caller.
2. **Per-tenant** aggregate limit: a global cap for all keys under that tenant's account.

When a single key exhausts its bucket, reject only that key. The tenant's other keys retain their own budgets. Only when the tenant-level cap is reached do you return 429 for *all* keys of that tenant.

**Implementation principle:** Always check the per-key limit first. If the key has capacity, check the tenant limit. This avoids unnecessarily counting a request against the tenant budget when a key is already blocked.

**Separate pools for critical operations:** Allowlist certain endpoints (health checks, webhook delivery confirmations) from rate counting, or give them separate, higher-limit buckets. This prevents a flood of GET requests from starving a tenant's ability to POST critical data.

## Headers, Error Responses, and Client Guidance

A well-designed rate limit response tells the client *when* to retry and *how much* capacity they have left. Return these headers on every request:

- `X-RateLimit-Limit`: The maximum requests allowed in the window (e.g., "100").
- `X-RateLimit-Remaining`: The remaining count for the current window (e.g., "42").
- `X-RateLimit-Reset`: Unix timestamp (seconds) when the limit resets.
- `Retry-After`: Seconds the client should wait before retrying (only on 429 responses).

*Important note about key vs. tenant scope:* When using hierarchical limits, include scope in header names or values: `X-RateLimit-KeyLimit` and `X-RateLimit-TenantLimit`. Otherwise, a client might see "100 remaining" and assume it refers to their key, while it actually refers to the tenant aggregate.

**Error response body (429 Too Many Requests):**

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded. See Retry-After header.",
    "scope": "api_key",  // or "tenant" to indicate which limit was hit
    "reset_at": 1712345678
  }
}
```

Distinguish between per-key and per-tenant exhaustion in the `scope` field. This helps teams debug: "Our integration hit its own limit, not the tenant's" vs. "We need to request a plan upgrade."

## Observability: Knowing Whether It's Working

Rate limiting that silently kicks in or out is dangerous. You need three pillars of observation:

### Metrics (aggregate, real-time)

- **Total requests by tenant, by key, by endpoint:** baseline for comparison.
- **Rate limited requests by tenant, by key, by scope (key vs. tenant):** the primary signal. A healthy system should see occasional per-key throttling (stops noisy clients) but near-zero per-tenant throttling (indicates under-provisioned or overloaded tenant).
- **Average latency and 99th percentile latency:** If rate limiting is working, P99 latency should remain stable during traffic spikes. If P99 rises alongside throttling, the limit might be set too high.
- **Token bucket fill rate and consumption rate:** For each tenant tier, track actual consumption divided by allocated rate. A ratio > 0.8 for sustained periods suggests the limit is too tight.

### Logs (individual events, for debugging)

Log every rate limit decision (allow, block by key, block by tenant) with:

- Tenant ID, API key ID
- Endpoint and HTTP method
- Current bucket state (tokens before/after)
- Decision reason

*Don't* log every single accepted request—that's cost-prohibitive at scale. Sample at 1% or use structured logging only for denied requests and edge cases.

### Alerts (proactive, threshold-based)

- **Per-tenant throttling rate > 1% of total requests for that tenant:** This indicates a systemic problem (e.g., a tenant hitting global limits frequently) that needs human review.
- **Any tenant hitting per-tenant limit > 5 times in 10 minutes:** Could indicate a misconfiguration or attack.
- **Global rate limiter latency (the time spent evaluating limits) > 5ms P99:** If the rate limiter itself becomes slow during traffic spikes, its overhead may destabilize instead of protecting.
- **Rate limited requests increasing while overall request count stays flat:** A subtle signal that something is degrading—maybe token bucket refills are delayed or clock drift is off.

## Recommended Baseline Design

For a multi-tenant API serving both small teams and enterprises:

1. **Use token bucket** as the core algorithm with 1-second refill granularity. Store bucket state in a fast, consistent data store (e.g., Redis with Lua scripting for atomicity). Bucket size = burst allowance; refill rate = sustained throughput.

2. **Implement hierarchical limits:** Per-key limits at, e.g., 10 req/s for the smallest plan, with per-tenant aggregate at 50 req/s. Enterprise plans increase both proportionally (e.g., 100 req/s per key, 1000 req/s aggregate).

3. **Separate critical endpoints** into their own bucket pools. For example, POST `/invoices` gets 20% of the tenant's budget, reserving the rest for read-heavy usage.

4. **Return clear headers** (`X-RateLimit-KeyLimit`, `X-RateLimit-TenantLimit`, `Retry-After`) and a scoped error body on 429.

5. **Start with per-key throttling** and escalate to per-tenant throttling only when the aggregate is exhausted. Document this behavior publicly.

6. **Monitor per-tenant throttle rate** as the key health metric. Keep it below 0.1% of total requests for that tenant. If it rises, investigate before conversations about "unfair throttling" begin.

7. **Provide a rate limit dashboard** to tenants showing their real-time consumption, remaining budget, and which keys are hitting limits. Transparency reduces support tickets and helps teams self-correct.

A well-designed rate limiter protects infrastructure without becoming a source of friction. With the right algorithm, hierarchical scope, observability, and client feedback, you can serve both a startup's script and an enterprise's core integration without either damaging the other's experience.
````
