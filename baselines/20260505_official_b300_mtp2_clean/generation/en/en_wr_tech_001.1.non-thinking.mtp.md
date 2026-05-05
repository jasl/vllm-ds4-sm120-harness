# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `1`
- Thinking mode: `non-thinking`
- Thinking strength: `disabled`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `mtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 11.332679
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2156, "completion_tokens": 2004, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2004
- Total tokens: 2156

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
# The Shared-Bucket Paradox: Designing Rate Limits for Multi-Tenant APIs

Backend engineers often conflate rate limiting with authentication, authorization, or quota management. In a multi-tenant API serving both small teams and enterprise customers, this confusion leads to systems that either block legitimate usage or fail to protect shared infrastructure. This article clarifies those distinctions and provides a design framework for rate limiting that scales across tenant sizes.

## 1. Authentication, Authorization, Quotas, and Rate Limits: The Four Distinct Layers

These four concepts are frequently grouped together, but they serve fundamentally different purposes:

- **Authentication** answers *“Who is making this request?”* – verifying identity via API keys, OAuth tokens, or mTLS certificates. A request can be fully authenticated yet still be denied for other reasons.
- **Authorization** answers *“Is this requester allowed to perform this action?”* – checking permissions (e.g., can this user delete a production database?). It operates on identity and resource scope, not request volume.
- **Quotas** define *“How much total usage is the customer allowed over a billing period?”* – a hard ceiling on operations per month, storage consumed, or data transferred. Quotas enforce contractual bounds; they are enforcement, not traffic shaping.
- **Rate limits** answer *“How fast can this requester send requests right now?”* – they protect system stability by smoothing traffic spikes. Unlike quotas, rate limits reset frequently (seconds to minutes) and are about burstiness, not total usage.

A common anti-pattern: using rate limits to enforce quotas. This causes small teams to hit limits during legitimate bursts (e.g., batch uploads) while enterprise customers with high quotas also get throttled, defeating the purpose of differentiated service.

## 2. Practical Algorithm Comparison: Token Bucket, Fixed Window, Sliding Window

### Fixed Window
Divides time into discrete intervals (e.g., 1 minute). A counter resets at each window boundary.
**Pros:** Simple to implement, low memory.
**Cons:** Known “burst at boundary” problem: 100 requests allowed per minute → 99 requests at 00:59, then 100 more at 01:00 → effectively 199 requests in 2 seconds. This penalizes small teams with noisy services that naturally batch.

### Sliding Window Log
Tracks timestamps of all requests within a rolling window.
**Pros:** Accurate smoothing, no boundary bursts.
**Cons:** Memory grows linearly with allowed requests; expensive to store per-tenant request logs for enterprise customers handling millions of requests.

### Sliding Window Counter (Hybrid)
Combines fixed window counters with a sliding ratio. Tracks current window count and previous window count, calculates: `current_count + (prev_count * overlap_ratio)`.
**Pros:** Near-exact smoothing with O(1) memory per key.
**Cons:** Slightly more compute on each request; requires careful handling of clock skew in distributed setups.

### Token Bucket
A bucket holds tokens up to a max capacity. Tokens are added at a steady rate (refill). Each request consumes a token.
**Pros:** Allows bursts up to bucket size, then throttles to sustained rate. Intuitive for developers – “send as fast as you want until you empty the bucket.”
**Cons:** Refill rate must be tuned carefully; if refill is too slow, small teams with legitimate bursts (e.g., CI/CD pipeline) get blocked. If too fast, enterprise tenants can still overwhelm the system.

**Recommendation:** Use token bucket per tenant with separate bucket sizes for “burst limit” and “sustained rate.” This gives small teams flexibility during development bursts while capping long-term throughput.

## 3. Avoiding Tenant-Wide Punishment from Noisy Integrations

The most common mistake: applying a single rate limit at the tenant level. When one noisy integration (e.g., a misconfigured cron job, a webhook spammer) exhausts the tenant’s bucket, **all** other integrations – including critical user-facing API calls – get blocked.

**Solution: Hierarchical rate limiting with key-scoped buckets.**

Design two levels:
- **Tenant-level bucket:** Covers the total traffic to protect the system. Size is based on customer tier (e.g., 1000 req/min for small teams, 50,000 req/min for enterprise).
- **Key-level (integration) bucket:** Each API key or OAuth client within a tenant gets its own bucket. The sum of all key-level limits should be **greater** than the tenant limit (e.g., each of 5 keys can burst to 300 req/min while tenant max is 1000 req/min – this intentionally allows some over-provisioning so no single key blocks others).

When a request arrives:
1. Check key-level bucket: if empty, return 429 (with reason: “API key rate limit exceeded”).
2. If key-level passes, check tenant-level bucket: if empty, return 429 (with reason: “Team rate limit exceeded”).
3. Only if both pass, process the request.

This prevents one noisy integration from starving others. The noisy key gets blocked; other keys within the same tenant continue working.

## 4. Headers and Error Messages: Transparency Is a Feature

Clients should never have to guess why they were throttled. Return the following headers on every response:

| Header | Description | Example |
|--------|-------------|---------|
| `X-RateLimit-Limit` | Maximum requests allowed per window | `1000` |
| `X-RateLimit-Remaining` | Requests remaining in current window | `423` |
| `X-RateLimit-Reset` | Unix timestamp when the window resets | `1700000000` |

Additionally, on a 429 response, include:

```http
Retry-After: 3
```

…where the value is seconds until the client can retry. This allows HTTP clients to automatically back off without polling.

**Error body (JSON):**
```json
{
  "error": {
    "type": "rate_limit_exceeded",
    "scope": "api_key",   // or "tenant"
    "limit": 300,
    "reset_at": 1700000000,
    "retry_after_seconds": 3
  }
}
```

The `scope` field is critical: it tells the client *which* bucket was exhausted, allowing them to diagnose if a single integration is misbehaving or if the whole tenant needs a plan upgrade.

## 5. Observability: Beyond Dashboards

Rate limits are only useful if you know they’re working. Design for these three signals:

### Metrics (cardinality-aware)
- `rate_limit_checks_total` by tenant_id, key_id, decision (pass/block)
- `rate_limit_blocked_requests_total`  – track *which* endpoints are being blocked (helps identify DDoS vs. legit usage)
- `rate_limit_bucket_fill_percentile` – p50, p95, p99 of bucket fullness at request time. If p99 is >90%, throttling is healthy; if p50 is >90%, limits are too tight.
- **Avoid** high-cardinality labels like full request paths. Aggregate by endpoint category (e.g., `read`, `write`, `admin`).

### Logs (sampled, structured)
- Log every 10th blocked request with: tenant_id, key_id, endpoint, user_agent, current bucket fill, reason.
- Log 1% of passed requests with the same fields. This allows comparative analysis: “Is the blocked traffic pattern different from passed traffic?” (e.g., same user agent hammering `/batch` vs. normal distribution).

### Alerts (actionable, not noisy)
- **P1:** Tenant blocked >90% of traffic for >5 minutes → indicates noisy integration or DDoS.
- **P2:** Any key-level bucket hitting zero for >10 seconds → potential client misconfiguration; alert the client contact.
- **P3:** Global p95 bucket fill >80% for an hour → limits may need tuning.
- **Non-alert:** “One key is at 50% fill” – this is normal. Noise here erodes trust in alerts.

## 6. Recommended Baseline Design

For most multi-tenant APIs with small teams and enterprise customers, start with:

1. **Algorithm:** Token bucket for each tenant (refill every second). Different tiers: small teams (1000 req/min, 50 burst), mid (10k req/min, 500 burst), enterprise (50k req/min, 2000 burst).
2. **Hierarchy:** Tenant-level bucket + per-key (or per-integration) sub-buckets. Each key’s burst is 20% of the tenant total, so one key can’t dominate.
3. **Headers:** `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`. Error bodies include `scope` field.
4. **Observability:** Three metrics, sampled logs, and three-level alerting as described.
5. **Avoid:** Fixed window (boundary burst problem); global rate limits (punishes all customers for one noisy tenant); 400 status codes (429 is the standard).

This design protects service stability without punishing small teams during legitimate bursts or blocking enterprise customers due to a single misconfigured integration. Start simple, measure what happens when a CI pipeline runs 100 parallel builds, and adjust bucket sizes from there.
````
