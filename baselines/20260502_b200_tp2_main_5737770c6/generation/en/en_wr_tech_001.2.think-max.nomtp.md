# Generation Transcript

- Case: `en_wr_tech_001`
- Language group: `en`
- Workload: `writing`
- Model: `deepseek-ai/DeepSeek-V4-Flash`
- Round: `2`
- Thinking mode: `think-max`
- Thinking strength: `max`
- Temperature: `1.0`
- Top P: `1.0`
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 16.851564
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2214, "completion_tokens": 2062, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2062
- Total tokens: 2214

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
# Designing Rate Limits for Multi-Tenant APIs Serving Both Small Teams and Enterprise Customers

## 1. Clearing the Terminology: Auth, Authorization, Quotas, and Rate Limits

Before designing any throttling mechanism, it is critical to distinguish four concepts that are often conflated.

**Authentication** answers *who* you are. It is the process of verifying identity—typically via API keys, OAuth tokens, or mTLS certificates. It does not gate access to resources; it only establishes identity.

**Authorization** answers *what you are allowed to do*. RBAC or ACLs determine whether a given principal can read, write, or delete a specific endpoint or resource. Authorization is a binary permission check, not a capacity control.

**Quotas** define *how much* a tenant is entitled to consume over a long period—usually a month or billing cycle. Examples: 100,000 API calls per month, or 10 GB of storage. Quotas are enforced at the end of the cycle via throttling or billing.

**Rate limits** govern *how fast* a tenant can send requests over a short time window (seconds, minutes, hours). They protect system stability by preventing any single tenant from overwhelming shared infrastructure. Rate limits are dynamic by nature and reset quickly.

A well-designed multi-tenant API applies authentication first, then authorization, then rate limiting, and finally quota checks. Rate limits protect the service; quotas protect business margins.

## 2. Algorithm Choice: Token Bucket vs. Fixed Window vs. Sliding Window

### Fixed Window
Simplest to implement: count requests per wall-clock minute. At second 0 of each minute, reset the counter. This exhibits a known “burst at reset” problem: a tenant could send 1,000 requests at 12:00:59 and another 1,000 at 12:01:00, effectively doubling capacity in two seconds. Also volatile for long-lived connections.

### Sliding Window Log
Each request logs a timestamp. The window is a queue of timestamps that you maintain over a sliding time interval. This is the most precise—any 60-second window gets exactly the configured limit. Drawback: O(n) memory per tenant (queue size grows with limit), and pruning old entries adds latency. Impractical for tens of thousands of tenants.

### Sliding Window Counter (Hybrid)
A practical compromise: partition time into small buckets (e.g., 1-second sub-windows within a 60-second window). Maintain a fixed-size array of counters. On each request, sum all sub-window counters within the last 60 seconds. This gives near-continuous precision with O(1) memory per tenant and O(window_buckets) compute, which is trivially cached.

### Token Bucket
Model a bucket with capacity `B` (maximum burst) that refills at rate `R` tokens per second. Each request consumes one token. If the bucket is empty, the request is denied. This is the most forgiving of natural traffic bursts while still enforcing a sustained rate. No reset edge-case. Easy to implement with a single atomic counter and a timestamp per tenant.

**Recommendation for multi-tenant APIs:** Use token bucket for per-endpoint or per-tenant rates. It handles bursty developer integrations gracefully and is straightforward to reason about. Fixed window is acceptable only if you can tolerate the reset burst, which is risky for enterprise tenants.

## 3. Avoiding Punishing an Entire Tenant for One Noisy Integration

A classic failure scenario: Tenant A has 50 integrations—one misbehaving script calling `/search` 100 times per second—and that tenant’s shared rate limit kicks in, blocking all 49 legitimate integrations for the next hour. The tenant’s engineering team blames your API.

**Solution: Multi-dimensional rate keys.**

- **Global tenant rate:** hard cap on total requests per second (e.g., 10,000 req/s). Protects infrastructure.
- **Per-integration (API key) rate:** tenant should use separate API keys for each logical integration. Rate-limit each key independently. The noisy key gets throttled; other keys remain healthy.
- **Per-endpoint rate:** assign lower limits to expensive endpoints (e.g., `/search`, `/export`). Even if an integration hits it hard, other endpoints stay fast.

**Implementation pattern:** When a request arrives, extract the tenant ID and API key ID. Evaluate rate limits in order: (1) endpoint-specific bucket, (2) key-specific bucket, (3) tenant-global bucket. Deny at the first empty bucket. This guarantees isolation.

**Fallback for tenants that won’t isolate keys:** Provide a “shared pool” with a configurable concurrency limit per integration. You can also offer a “burst pool” (extra tokens) that the tenant purchases—giving them control over peak usage.

## 4. HTTP Headers and Error Responses

Clients must know both their current status and how to react. Return these headers on every response:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 342
X-RateLimit-Reset: 1700000000
```

- `X-RateLimit-Limit` — the maximum requests allowed per window (or token bucket capacity).
- `X-RateLimit-Remaining` — tokens left.
- `X-RateLimit-Reset` — Unix timestamp when the bucket will refill (or window resets). Clients use this to compute backoff without guessing.

**On rate limit exceeded:**

- HTTP status: `429 Too Many Requests`.
- `Retry-After` header: seconds until the next token becomes available. Use an integer, not a date string.
- JSON body:
  ```json
  {
    "error": "rate_limit_exceeded",
    "message": "API rate limit exceeded for tenant mycorp. Retry after 12 seconds.",
    "retry_after_seconds": 12
  }
  ```
- Never return `503`. That implies server fault, not client behavior.

**For authorized but quota-exhausted (e.g., monthly call limit):** return `403 Forbidden` with `X-Quota-Limit` and `X-Quota-Reset` headers. Do not mix rate limit and quota responses—they have different remediation patterns.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting that cannot be observed is indistinguishable from unreliability. Instrument three categories:

### Metrics (counters and histograms)

- `rate_limit.requests.total` — total requests evaluated by tenant, key, endpoint.
- `rate_limit.throttled` — count of requests denied by tenant, key, endpoint. Tagged by reason (tenant cap vs. key cap vs. endpoint cap).
- `rate_limit.bucket_depth` — for each token bucket, publish current token count as a gauge. Sudden drops indicate bursts; sustained low values suggest limit is too tight.
- `rate_limit.latency` — histogram of time spent evaluating rate limits. Must be <1ms. If >10ms, your rate limiter is the bottleneck.

### Logs

Log only rate limit *denials*, not every request. Each log entry should include:
- tenant_id, api_key_id, endpoint, requested_at.
- Current bucket state (capacity, remaining, refill_rate).
- Which threshold was hit.

Do not log the full request body or headers—this is high cardinality data that will bankrupt your log budget and privacy compliance.

### Alerts

Set threshold-based alerts:
- **P1:** `rate_limit.throttled` for *any* tenant exceeds 5% of that tenant’s total requests over 5 minutes. Indicates the tenant is blocked and may escalate.
- **P2:** `rate_limit.throttled` per endpoint exceeds 10% of total requests—unlikely normal usage; an endpoint may be too expensive.
- **P2:** Global throttled rate > 2% of total traffic—system-wide limits may be misconfigured or under-provisioned.
- **P3:** `rate_limit.latency` p99 > 5ms—rate limiter implementation is degrading.

Crucially, distinguish between *tenant-caused* throttling (their usage is spiky) and *infrastructure-caused* throttling (limits are too low for legitimate patterns). The former should trigger a tenant support ticket; the latter triggers an ops ticket.

## Recommended Baseline Design

1. **Algorithm:** Token bucket per (tenant, API key, endpoint). Use a single atomic counter stored in Redis (or equivalent fast KV store) per key. No batch operations. Refill evaluated lazily using a last-refill timestamp.

2. **Burst allowance:** Give each tenant a burst capacity equal to 5x their sustained rate (e.g., 500 req/s sustained → 2,500 burst). This accommodates development spikes without requiring all tenants to buy enterprise plans.

3. **Dimensions:**
   - Global tenant: `N * sustained` (where N is number of keys).
   - Per API key: `sustained / number_of_keys`.
   - Per endpoint: custom, based on endpoint cost (CPU time, DB queries, external calls).

4. **Headers:** Always return `X-RateLimit-*`. Always return `Retry-After` on 429.

5. **Observability:** Publish per-bucket metrics. Log only denials. Alert on >5% tenant throttling.

6. **Self-service:** Provide a dashboard for tenants to view their current token levels, reset rates, and per-key usage. This turns rate limiting from opaque punishment into a controllable tool.

The goal is not to block users—it is to shape traffic into a pattern the system can handle while giving every tenant, from a solo developer to a Fortune 500 enterprise, a predictable, fair experience.
````
