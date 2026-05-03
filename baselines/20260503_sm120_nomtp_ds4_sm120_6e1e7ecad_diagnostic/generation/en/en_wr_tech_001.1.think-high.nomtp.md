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
- Elapsed seconds: 37.019684
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2520, "completion_tokens": 2368, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2368
- Total tokens: 2520

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
# Don't Let One Noisy Neighbor Wreck Your API: Designing Multi-Tenant Rate Limits That Scale

Every backend engineer has lived the nightmare: a single misconfigured integration floods your API, latency spikes, and suddenly every customer—from the two-person startup to the Fortune 500 enterprise—is staring at 429 errors. Your rate limiter did its job, but it did it badly. It punished everyone for one tenant's mistake.

Designing rate limiting for a multi-tenant API isn't just about traffic shaping—it's about maintaining trust across customers with wildly different usage patterns. Small teams need predictable limits that don't suffocate their growth; enterprises need headroom to run dozens of integrations simultaneously. Get it wrong, and you'll either throttle legitimate business or let noisy neighbors degrade service for everyone.

Let's walk through a production-grade approach.

## 1. Authentication, Authorization, Quotas, and Rate Limits: Know the Difference

These four concepts are often conflated. They serve distinct purposes and belong in different layers of your system.

**Authentication** answers "Who is this?" It's verifying identity via API keys, JWTs, or OAuth tokens. It happens first, before any request reaches your business logic.

**Authorization** answers "What can they do?" It checks permissions—can this API key create invoices? Can this user access admin endpoints? Authorization enforces scopes, roles, and resource ownership.

**Quotas** answer "How much total can they use?" These are hard limits on cumulative consumption over a billing period (e.g., 10,000 requests per month). Quotas enforce subscription tiers and drive revenue. They're checked periodically (hourly, daily) and can be reset at billing cycles.

**Rate limits** answer "How fast can they use it?" These are short-term per-second or per-minute limits that protect system stability. Rate limits prevent bursts from overwhelming your infrastructure. They're checked on every request and reset continuously.

Authentication comes first. Then rate limiting (to protect your system). Then authorization and quota checks (to enforce business rules). Order matters: you don't want to compute expensive authorization logic for a request you're about to reject.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window: Practical Trade-offs

### Fixed Window
Simplest to implement: allow N requests per minute, reset counter at the top of each minute. Works fine for low-traffic APIs.
**The spike problem:** At 59 seconds, a tenant bursts with 100 requests. At 60 seconds, the window resets, and they immediately burst with another 100. Your database sees 200 requests in two seconds, despite the 100/minute limit. This defeats the purpose of rate limiting.

### Sliding Window Log
Maintains a log of timestamps per tenant. On each request, remove timestamps older than the window, then check if the count exceeds the limit.
**Trade-off:** Memory-intensive at scale. Storing tens of thousands of timestamps per tenant in Redis is expensive. Also slow under heavy load—each request requires scanning and pruning a list.

### Token Bucket
The industry standard for production APIs. Each tenant has a bucket that fills at a fixed rate (e.g., 10 tokens per second) up to a maximum burst capacity (e.g., 50 tokens). Each request consumes one token. If the bucket is empty, reject.
**Why it wins:** It naturally handles bursts up to the bucket capacity, then smooths out. A team that makes 100 requests all at once can use 50 tokens immediately, then must wait for tokens to refill. No sudden resets, no memory bloat. Redis-backed token buckets (using sorted sets or a Lua script) are fast and atomic.

**Practical recommendation:** Implement token bucket per tenant with per-endpoint and per-IP sub-buckets for fine-grained control.

## 3. Avoiding Collective Punishment: Isolation Is Key

The cardinal sin of multi-tenant rate limiting: a single global limit that all tenants share. If Tenant A generates 10,000 requests/second, they'll exhaust the pool, and Tenant B (who made one legitimate request) gets a 429. This is how you lose customers.

**Per-tenant buckets** are essential. Each tenant (identified by API key) gets its own bucket with its own refill rate and capacity. Small teams get, say, 5 tokens/second with a burst of 20; enterprise customers get 100 tokens/second with a burst of 500.

But that's not enough. Within a tenant, one aggressive integration can starve all other integrations owned by that same customer. A tenant might have a user-facing web app, a background cron job, and a third-party webhook receiver—each with different traffic patterns.

**Solution:** Hierarchical buckets. The tenant has a global bucket, then each integration (identified by API key or IP) gets a sub-bucket. The integration's request first deducts from its own bucket. If that bucket is empty, it fails fast. The tenant's global bucket acts as a shared reserve: if an integration's sub-bucket is empty but the tenant bucket has tokens, you can allow a small overage. This prevents one bad integration from DoSing the tenant's entire account.

**Implementation trick:** Use Redis hash fields. Key = `ratelimit:tenant:{id}`, fields = `burst`, `tokens`, `last_refill`. For sub-buckets: `ratelimit:tenant:{id}:integration:{ip_or_key_id}`. A Lua script atomically deducts from both.

## 4. Error Headers and Messages: Help Clients Help Themselves

Your API clients (including other engineers) will debug rate limiting issues. Your responses must be informative.

**Every rate-limited response should include:**

- `Retry-After: 5` (seconds until next token is available—helps clients implement backoff)
- `X-RateLimit-Limit: 50` (maximum requests per second allowed for this tenant)
- `X-RateLimit-Remaining: 12` (tokens remaining in current bucket)
- `X-RateLimit-Reset: 1723800000` (Unix timestamp when the bucket refills next—or, more practically, when the client can expect RPS to restore)

**Error body (HTTP 429):**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded. You are making requests too quickly. Back off and retry.",
    "retry_after_seconds": 5,
    "rate_limit": {
      "limit_per_second": 50,
      "remaining_tokens": 0,
      "reset_epoch": 1723800005
    }
  }
}
```

**For integration-level throttling** (one IP within a tenant), include `X-RateLimit-Integration-Id` header to identify which sub-bucket triggered the limit.

**What not to do:** Don't return vague messages like "Too many requests." Don't omit the Retry-After header (clients will hammer you with exponential backoff guesses). Don't change limit values between responses (it confuses client-sync algorithms).

## 5. Observability: Know When Your Limits Are Working—or Breaking

Your rate limiter is a safety valve. You must know if it's protecting reliability or choking legitimate traffic.

### Metrics to Track (every 10 seconds or per-shard):

- **Requests blocked vs. allowed per tenant** (ratio < 5% is healthy; > 20% means your limits are too tight or a tenant is breaking SLA)
- **Token bucket utilization** (average tokens consumed per second per tenant—if enterprises hover at 90% capacity, they're hitting limits; if small teams hover at 10%, you can safely increase their limits)
- **429s by endpoint and HTTP method** (is your POST /import endpoint being hit? Maybe that endpoint needs higher limits)
- **429s by IP** (detect accidental DDoS from a single misconfigured integration within a tenant)
- **Token refill latency** (your Lua script must complete in <5ms; if Redis is bottlenecked, your rate limiter becomes the bottleneck)
- **Global vs. per-tenant limit hit ratio** (if 80% of 429s come from one tenant, that's a problem—either they're abusing or their limits are too low)

### Logs (structured, with correlation IDs):

Every rate-limited request should log:
```json
{
  "event": "rate_limit_violation",
  "tenant_id": "acme_corp",
  "integration_id": "ip_203.0.113.42",
  "endpoint": "/api/v1/orders",
  "tokens_consumed": 0,
  "bucket_capacity": 500,
  "bucket_tokens_available": 0,
  "retry_after_seconds": 2
}
```

### Alerts (critical first, then warnings):

**P0:** If >1% of all API requests are 429s across all tenants, your limits are globally too tight or there's a traffic anomaly. Alert immediately.

**P1:** If a single tenant's 429 rate exceeds 10% of its requests, investigate. They may have a buggy integration or need a limit increase.

**P2:** If token bucket refill latency exceeds 20ms for more than 5 minutes, your Redis cluster may be overloaded—rate limiting will start failing open (allow all traffic), defeating the purpose.

**P3:** Warning if any tenant consistently consumes 95%+ of its bucket capacity—consider proposing a tier upgrade or investigating their patterns.

**Dashboard idea:** Plot "429s per tenant" as a stacked area chart. If a single color dominates, that tenant needs attention.

## Recommended Baseline Design

1. **Redis-backed token buckets** per tenant (keyed by `ratelimit:{tenant_id}`) with a Lua script for atomic read-refill-deduct. Set per-tenant limits from a config service (not hardcoded).
2. **Hierarchical sub-buckets** per integration (by API key or source IP). Each sub-bucket deducts from its own pool first; if empty, checks the parent tenant bucket for one-time burst allowance.
3. **Per-endpoint overrides** stored in a separate Redis hash—certain endpoints (bulk import, webhook replay) get lower RPS limits within the same tenant bucket.
4. **Headers and error responses** as described in section 4, with `Retry-After` implementing exponential backoff hints.
5. **Observability pipeline:** emit metrics to your time-series database every 10 seconds; log every 429 with tenant and integration details; alert on global threshold >1% 429 rate.
6. **Fallback:** If Redis is unreachable, default to a second-granularity in-memory fixed window per process (not ideal but prevents total bypass). Log the fallback.

Rate limiting is a paradox: you're building a system that exists to deny requests, but its success is measured by how rarely legitimate requests are denied. Get the isolation right, and your customers won't even know it's there—which is exactly how it should be.
````
