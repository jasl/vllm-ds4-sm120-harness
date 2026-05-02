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
- Elapsed seconds: 17.163457
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2257, "completion_tokens": 2105, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2105
- Total tokens: 2257

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

```markdown
# Throttle with Purpose: Designing Rate Limits for a Multi-Tenant API

Rate limiting is one of those topics that seems simple until you have to make it work for both a five-person startup and a Fortune 500 enterprise sharing the same API. Get it wrong, and you either crush legitimate traffic or let one noisy tenant degrade everyone’s experience. This article walks through the core concepts, algorithm trade-offs, tenant isolation strategies, client-facing signals, and observability needs for a multi-tenant backend.

## 1. Authentication, Authorization, Quotas, and Rate Limits – The Four Layers

Before designing limits, be absolutely clear about what each mechanism does and where it fits in the request lifecycle.

**Authentication** answers “Who are you?” It validates credentials (API keys, OAuth tokens) and establishes identity. Without authentication, you cannot apply per-tenant or per-user limits.

**Authorization** answers “What are you allowed to do?” It checks permissions after authentication: can this tenant create resources? Can this user read sensitive data? Rate limits are not a substitute for authorization.

**Quotas** define *hard boundaries* on consumption over a long period – 1,000 API calls per month, 10 GB of storage, or 100 concurrent active projects. Quotas are enforced asynchronously or at the start of a billing cycle; they protect business models, not system stability.

**Rate limits** protect *operational capacity* over short time windows – seconds to minutes. They prevent a single misbehaving client (or a coordinated burst) from exhausting CPU, database connections, or memory. Rate limits are the first line of defense for reliability; quotas are the second line for business logic.

The key insight: rate limits should never be used to enforce a contract. If a customer agreed to 10,000 calls/hour, you honor that. Rate limits kick in only when bursts threaten the system’s ability to serve *any* tenant.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window – Practical Trade-Offs

Three algorithms dominate production rate limiters. Here is how they behave under load.

**Fixed Window** divides time into discrete buckets (e.g., one per minute). Each bucket has a counter that resets at the top of the minute. It is simple to implement and cheap in memory. However, it suffers from the “border burst” problem: if a client sends 100 requests at 11:59:59 and 100 requests at 12:00:01, the system sees 200 requests in two seconds but only 100 in each window. This defeats the purpose of short-term protection.

**Sliding Window** solves the border burst by tracking timestamps per request (or per increment). A rolling window of, say, 60 seconds counts requests from the current time backward. Implementations range from storing every timestamp (accurate but memory-heavy) to tracking a counter plus the previous window’s count (a compromise known as sliding window counter). Sliding windows feel fairer to clients—no sudden reset—but require more coordination in distributed systems.

**Token Bucket** is the workhorse of production systems. It works by refilling a bucket of tokens at a steady rate (e.g., 10 tokens per second) up to a maximum burst capacity (e.g., 100 tokens). A client consumes one token per request; if no tokens remain, the request is delayed or rejected. Token buckets naturally allow short bursts (up to the bucket size) while enforcing a long-term average. They are intuitive for engineers and map well to real-world capacity planning—the refill rate is your steady-state throughput, and the bucket size is your tolerance for spikes.

**Recommendation**: Use token bucket for most multi-tenant APIs. It provides burst tolerance (good for small teams that occasionally need to process a batch) and a hard average limit (essential for enterprise tenants that share infrastructure). Pair it with a sliding window counter only if you need precise per-second fairness and can afford the memory overhead.

## 3. Tenant Isolation – Never Punish One Tenant for Another’s Noisy Integration

The simplest mistake is a global counter shared across all tenants. A single misconfigured integration on one team’s account can exhaust the global token pool, blocking every other tenant. That is unacceptable.

**Per-tenant buckets** are the minimum: each API key or tenant ID gets its own token bucket. Memory scales linearly with tenant count, which is manageable for thousands of tenants but not millions. For large-scale systems, use a sharded Redis cluster with a token bucket per tenant key, or move to a tiered approach where “small” tenants share a bucket (with individual sub-limits) and “enterprise” tenants get dedicated resources.

**Hierarchical rate limits** add another layer. Apply a global cluster-level limit (e.g., total requests per second across all tenants) to protect the infrastructure, then per-tenant limits that are a fraction of the global capacity. Overcommit slightly: the sum of per-tenant limits can exceed global capacity, because not all tenants burst simultaneously. But never let one tenant consume more than 25–30% of global capacity without manual review. This prevents a noisy neighbor from starving everyone else.

**Integration-level sub-limits** prevent a tenant from shooting itself in the foot. A tenant might have 1,000 requests/second total, but a single long-polling connection or a retry loop can saturate that. Offer the ability to set per-integration (per-API key) or per-endpoint limits inside the tenant’s bucket. This moves isolation from “tenant vs. everyone” to “integration vs. same tenant other integrations.”

## 4. Headers and Error Responses – Tell Clients Exactly What Happened

Clients cannot behave well if they have no feedback. Return these headers on every response:

- `X-RateLimit-Limit`: the maximum number of requests allowed in the current window (or bucket capacity).
- `X-RateLimit-Remaining`: how many requests remain.
- `X-RateLimit-Reset`: a Unix timestamp (or ISO 8601) indicating when the counter resets or the bucket refills.

When a request is rejected, use HTTP 429 Too Many Requests. The body should include:

- A human-readable message: “Rate limit exceeded. Retry after [time].”
- A `Retry-After` header with the number of seconds the client should wait (integer or HTTP-date).
- Optionally, a structured JSON body with fields like `error.code`, `error.message`, and `error.retry_after_seconds`.

**Critical**: Distinguish between rate limits (operational) and quota limits (contractual). A 429 with “rate limit exceeded” means back off for seconds. A 403 or 429 with “quota exceeded” means you have hit your monthly cap and need to upgrade or wait for the billing cycle. Use different HTTP status codes or distinct error codes so automation can react appropriately.

## 5. Observability – Are Your Limits Doing Their Job?

Rate limits should block bad behavior, not hurt good customers. Metrics and alerts are the only way to know.

**Metrics to track**:
- `rate_limit.requests_total` by tenant tier, endpoint, and status (allowed / blocked).
- `rate_limit.blocked_requests_total` with labels for tenant ID and integration key.
- `rate_limit.throttled_requests_total` for requests allowed after waiting (if you use queuing).
- `rate_limit.latency_ms` for the rate limiter itself – it must be fast (sub-millisecond).
- `rate_limit.token_refill_rate` and `rate_limit.bucket_capacity` per tier.

**Logs**: Log every blocked request at warning level. Include tenant ID, endpoint, current usage count, limit, and the algorithm in use. Do not log every allowed request—that creates noise equal to total traffic.

**Alerts**:
1. **Global traffic spike** – if total requests per second exceeds 80% of global bucket capacity for > 1 minute, alert the on-call.
2. **Per-tenant throttling spike** – if a single tenant experiences > 10% blocked requests over 5 minutes, investigate. They may have a bug or need a plan upgrade.
3. **Rate limit latency** – if the rate limiter itself takes > 5ms p99, it is becoming a bottleneck.
4. **False positive detection** – if a tenant that rarely hits limits suddenly gets blocked extensively, check for misconfiguration (e.g., too aggressive a sub-limit on a new integration).

## Recommended Baseline Design

For a multi-tenant API serving both small teams and enterprises:

- **Algorithm**: Per-tenant token bucket with 1-second refill granularity. Bucket capacity = 150% of the refill rate per second to allow small bursts.
- **Implementation**: Centralized Redis cluster with key format `ratelimit:{tenant_id}:{bucket_name}`. Use a Lua script to atomically check and decrement tokens. This avoids race conditions and is fast (< 1ms).
- **Tiers**: Define three tiers: “Starter” (50 req/s, burst 75), “Pro” (500 req/s, burst 750), “Enterprise” (5000 req/s, burst 7500 or custom). Overcommit global capacity by 2x.
- **Isolation**: Each tenant gets its own bucket. Offer optional sub-buckets per API key inside the tenant’s account.
- **Headers**: Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` on every response. Use 429 + `Retry-After` on rejection.
- **Observability**: Counters for requests and blocks broken by tenant tier and endpoint. Alerts for >10% per-tenant blocking rate and >80% global capacity utilization.

This design balances fairness, performance, and simplicity. It gives small teams the burst they need for batch jobs and gives enterprises the isolation they demand—without letting one tenant’s loop bring down the entire system.
```
