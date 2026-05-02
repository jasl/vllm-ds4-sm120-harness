# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 18.138153
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2378, "completion_tokens": 2226, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2226
- Total tokens: 2378

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
# Bounded by Design: Rate Limiting for the Multi-Tenant API

## 1. The Four Pillars of Access Control

Before discussing rate limiting, we must distinguish it from three closely related concepts that often get conflated.

**Authentication** answers *who you are*. It’s the credential check—API key, OAuth token, mTLS certificate. Without it, no request proceeds. A rate limit is meaningless if unauthenticated traffic can exhaust it.

**Authorization** answers *what you can do*. It governs access to specific resources or actions (e.g., “tenant A can read, tenant B can write”). A properly authorized request still must pass rate limiting.

**Quotas** are *hard, often contractual limits* enforced over longer intervals (daily, monthly). Exceeding a quota means the tenant must upgrade their plan or wait for the next billing cycle. Quotas are typically checked asynchronously, not on every request.

**Rate limits** are *soft, short-term limits* (per second, per minute) that protect system stability. Exceeding a rate limit is transient—the client can retry after a brief cooldown. Rate limits are checked synchronously on every request.

The key insight: authentication and authorization gate **access to the API**; quotas and rate limits gate **access to capacity**. Both are needed, but they solve different problems.

## 2. Three Algorithms at a Practical Level

### Fixed Window
Divide time into discrete buckets (e.g., 60-second windows). Count requests per bucket. When a bucket fills, reject until the next bucket opens.

**Reality check:** This algorithm is simple to implement (a single counter per window, resetting on a timer) but suffers from *boundary spikes*. If a tenant sends 1,000 requests at the last millisecond of window N and 1,000 requests at the first millisecond of window N+1, the system sees 2,000 requests in near-zero time. Fixed windows thus require a safety margin—lowering the limit to absorb these bursts—which wastes capacity.

### Sliding Window Log
Track timestamps of every request (e.g., in a sorted set or circular buffer). On each request, remove timestamps older than the window duration, then count remaining timestamps.

**Reality check:** This removes the boundary spike problem but introduces memory and CPU overhead proportional to throughput at the window boundary. For a tenant doing 10,000 requests/minute, you must store and sort 10,000 timestamps. For multi-tenant systems with thousands of active tenants, this becomes a hot loop that needs careful data structure choice (e.g., a rolling buffer with O(1) eviction).

### Token Bucket
A bucket holds a fixed number of tokens (the *capacity*). Tokens are added at a fixed *refill rate* (e.g., 10 tokens per second). Each request consumes one token. If the bucket is empty, the request is rejected.

**Reality check:** Token bucket is the industry favorite for three reasons. First, it naturally allows bursts up to the bucket capacity—if a tenant hasn’t sent requests for 10 seconds, they can send 100 at once (if capacity=100). Second, it aligns with how TCP and connection pooling work: a client can send a burst right after connection establishment. Third, implementation is trivial: two atomic integers (tokens, last_refill_timestamp) and a refill calculation on each request. The only pitfall is clock skew in distributed systems—use monotonic time or a central coordinator.

**Practical recommendation:** Token bucket for per-tenant limits. Fixed window only if you need global, non-burstable limits (e.g., “no more than 1,000 logins per hour per IP”). Avoid sliding window logs unless you have a specific need for exact counting (e.g., enforcing strict compliance SLAs).

## 3. The Noisy Neighbor Problem

In multi-tenant systems, one tenant might have an integration that sends bursts (e.g., a webhook retry storm, a buggy client, or a sudden data sync). Without isolation, this tenant’s behavior can exhaust shared resources (database connections, CPU, network bandwidth) and degrade service for everyone.

**The cardinal rule: never rate-limit at the shared resource level.** Instead, institute hierarchical limits:

- **Global pool:** A soft cap on total system throughput. If crossed, begin rejecting *all tenants* as a last resort, but this should never happen in normal operation.
- **Per-tenant bucket:** Each tenant gets its own token bucket (capacity = their plan limit × burst multiplier). The key design choice: the per-tenant limit is *independent* of other tenants. Tenant A’s burst must not consume tokens from Tenant B’s bucket.
- **Per-integration sub-buckets (optional):** For enterprise tenants, allow them to create API keys scoped to specific integrations. Each key gets its own sub-bucket with capacity `(parent_tenant_capacity / N)`. This prevents one buggy webhook from exhausting the tenant’s entire limit.

**A critical nuance:** If a tenant hits their per-tenant limit, reject only *that* tenant’s requests. Do not degrade or delay other tenants. This requires your rate limiter to be a pure function that takes (tenant_id, request_timestamp) and returns (allow/deny) without global state that can be contaminated by other tenants’ counters.

**Warning against shared counters:** Avoid designs where all tenants share a single sliding window or a global token bucket. This turns every noisy neighbor into a global outage. Instead, use sharding by tenant_id across your rate limiter instances (e.g., hash tenant_id to a consistent backend that holds that tenant’s state in memory).

## 4. Headers and Error Messages That Help Clients

Clients need enough information to self-correct. Return the following headers on every response:

- `X-RateLimit-Limit`: The maximum requests allowed per window (or bucket size). Helps clients know their ceiling.
- `X-RateLimit-Remaining`: Number of requests remaining in the current window (or current bucket level). This is the most actionable header.
- `X-RateLimit-Reset`: Unix timestamp (or seconds until reset) when the bucket refills or the window resets. Use a uniform format (e.g., Unix epoch seconds) to avoid client parsing errors.

**For rejected requests (HTTP 429):**
Return a body that includes:
- An error code like `rate_limit_exceeded`.
- A human-readable message indicating *which* limit was exceeded (e.g., “API calls per minute exceeded” vs. “Concurrent requests per integration exceeded”).
- A `Retry-After` header with seconds until the client should retry. This is more reliable than the reset timestamp because it accounts for clock skew.

**Crucial:** Never expose the *global* limit or another tenant’s capacity. Return only the calling tenant’s per-tenant limits. Leaking global limits invites probing attacks.

## 5. Observability: Proving Protection Without Blocking Legitimate Use

You must answer two questions in production: “Are rate limits protecting the system?” and “Are we blocking legitimate requests?”

### Metrics (aggregated, low cardinality)

- `rate_limit_calls_total` (with labels: tenant_id, status=allowed|blocked, endpoint_group)
- `rate_limit_bucket_current` (per tenant, per bucket level). Export to Prometheus with high cardinality only if you can afford it—otherwise use histograms.
- `rate_limit_global_capacity_remaining` (a gauge of system breathing room). If this stays > 20%, your limits are generous enough.

### Logs (sampled, high-cardinality)

Log only when a request is *blocked*. Include: tenant_id, endpoint, integration_key (if present), bucket level at time of rejection, and the header values returned. This allows root-cause analysis: “Tenant X has a bug in their sync process that retries every 100ms.” Never log every allowed request—that’s noise at scale.

### Alerts

- **High rejection rate per tenant:** If any tenant’s rejection rate exceeds 10% of their total requests for 5 minutes, alert. This usually means a buggy client, not an abusive tenant.
- **Global capacity dropping:** If global capacity remaining falls below 10%, alert immediately. This indicates either too many tenants are nearing their limits simultaneously, or the limits themselves are too generous.
- **Latency increase for allowed requests:** If p99 latency for allowed requests rises when rate limits are not being hit, you have another problem (resource contention, not rate limiting).

**Diagnostic practice:** Build a dashboard showing per-tenant allowed vs. blocked requests as stacked bar charts, overlaid with the bucket refill rate for a few representative tenants. This reveals patterns: “Tenant A spikes at the top of every hour (cron job) but stays below the limit; Tenant B has a slow leak that gradually depletes their bucket over 10 minutes.”

## Recommended Baseline Design

For a multi-tenant API serving both small teams and enterprises:

1. **Algorithm:** Token bucket per tenant, with bucket capacity = (plan limit × 2) and refill rate = plan limit per minute. This gives every tenant a 2× burst that recovers in one minute.

2. **Hierarchy:** Three levels—global (failsafe, never permit > 2× total planned capacity), per-tenant (primary enforcement), optional per-key sub-buckets for enterprise customers who need integration isolation.

3. **Headers:** Always return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`. On 429, return `Retry-After` and a JSON body with `error:rate_limit_exceeded` and a message scoped to the tenant’s limit.

4. **State storage:** In-memory hash table keyed by tenant_id on a single rate-limiter node. Scale by replicating the rate limiter behind a load balancer that routes by tenant_id hash. This avoids distributed locking and keeps latency under 1μs per check.

5. **Observability:** Counters on every decision, sampled logs on rejection only, and per-tenant and global alerts. Review rejection patterns weekly—they are a signal of client behavior, not just system stress.

The goal is not to block traffic—it’s to shape traffic so that your system remains predictable, your costs stay bounded, and your customers never discover who their noisy neighbors are.
```
