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
- Elapsed seconds: 10.279257
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2334, "completion_tokens": 2182, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2182
- Total tokens: 2334

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
# Rate Limiting for Multi-Tenant APIs: Balancing Fairness and Reliability

## 1. Foundational Concepts: Authentication, Authorization, Quotas, and Rate Limits

Before designing a rate-limiting system, we must clarify four distinct concepts that are often conflated:

- **Authentication** verifies *who* the caller is (e.g., API key validation, OAuth token introspection). It answers: “Is this request coming from a known entity?”
- **Authorization** determines *what* the caller is allowed to do (e.g., read vs. write, access to specific endpoints). It answers: “Does this caller have permission for this action?”
- **Quotas** define *how much* a tenant can consume over a long period (e.g., 100,000 requests per month, 10 GB of storage). Quotas are enforced periodically (hourly, daily, monthly) and typically result in soft warnings or hard blocking.
- **Rate limits** control *how fast* requests can be made (e.g., 1,000 requests per minute). Rate limits protect against short-term bursts, accidental loops, or abusive traffic that could degrade service for all tenants.

In a multi-tenant API, rate limits operate at sub-second to minute granularity, while quotas operate over hours or days. Both are necessary: quotas control cost and fair usage over time; rate limits protect real-time system stability.

## 2. Practical Algorithm Choices: Token Bucket vs. Fixed Window vs. Sliding Window

### Fixed Window
Partitions time into discrete buckets (e.g., 1-minute slices). Each tenant can make N requests per window. **The problem**: at the boundary between windows, a tenant can send 2N requests in near-zero time (last request of window A, first of window B), causing traffic spikes that defeat the purpose of rate limiting.

### Sliding Window Log
Maintains a timestamp-ordered list of recent request times per tenant. When a request arrives, remove timestamps older than the window (e.g., 60 seconds) and count remaining. **Accuracy**: perfect. **Cost**: O(n) memory and time per check, where n is the number of requests in the window. For high-throughput endpoints, this becomes expensive.

### Sliding Window Counter
A hybrid: keep two counters for the current and previous fixed windows. The effective count at any moment is:
`previous_window_count * (elapsed_time_in_current_window / window_duration) + current_window_count`
This avoids storing all timestamps while smoothing the boundary spike to a near-linear decline. **It is the pragmatic choice** for most multi-tenant APIs: memory O(1) per tenant, accuracy within ~5% of true sliding window, and fast computation using only atomic increments.

### Token Bucket
Conceptually, a bucket holds up to `capacity` tokens, and new tokens are added at a fixed `rate` (e.g., 10 tokens per second). Each request consumes one token. A burst of size `capacity` is allowed, then the sustained rate is throttled. **Token bucket is ideal for bursty workloads**: a small team that spikes for 5 seconds then goes quiet should be allowed, while an enterprise client with steady traffic gets predictable throughput.

**Recommendation**: Use **token bucket** as the primary algorithm for API rate limits. For scenarios where you must enforce hard per-second ceilings (e.g., database connection limits), complement with a **sliding window counter** at second-level granularity.

## 3. Avoiding Tenant-Wide Punishment for a Noisy Integration

One misbehaving integration (e.g., a customer’s CI/CD pipeline stuck in a retry loop) should degrade only that integration, not the entire tenant’s API access.

**Design patterns**:

- **Hierarchical rate limits** with three tiers:
  *Global (cluster-wide)* → protects the entire system.
  *Per-tenant* → ensures fair share across customers.
  *Per-endpoint or per-client-id* the most granular—each API key or integration gets its own bucket.

  When a specific client-id exceeds its limit, return 429 **for that client only**. Other client-ids under the same tenant continue normally.

- **Quotas vs. rate limits are separate**
  If an integration exhausts a per-client rate limit, it should still be able to make *some* requests at a reduced rate. Only quotas (monthly) should result in complete denial of service for the tenant.

- **Internal traffic classification**
  Tag requests by source (web app, SDK, batch job). Apply different rate limit tiers: interactive traffic gets higher priority than background syncs.

- **Graceful degradation**
  When a tenant approaches its per-tenant limit, start increasing response times (via added artificial delays) *before* returning 429. This gives client-side retry logic a chance to back off naturally without dropping requests entirely. For enterprise customers, allow a configurable “overage” buffer that incurs a soft throttle rather than hard rejection.

## 4. HTTP Headers and Error Responses

Clients must receive enough information to self-regulate. At minimum, return these headers on every response:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 342
X-RateLimit-Reset: 1698765432
```

- `X-RateLimit-Limit`: maximum requests per window (e.g., per minute).
- `X-RateLimit-Remaining`: remaining requests in current window.
- `X-RateLimit-Reset`: Unix timestamp when the window resets (or when tokens will be fully replenished for token bucket).

**On 429 Too Many Requests**:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 45
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1698765432
Content-Type: application/problem+json

{
  "type": "https://api.example.com/errors/rate-limit",
  "title": "Rate limit exceeded",
  "detail": "You have exceeded the per-client rate limit of 1000 requests per minute. Please reduce request frequency or contact support to increase your limit.",
  "instance": "client-id:abc123, endpoint:POST /orders",
  "scope": "client-id"
}
```

Including `scope` tells the client exactly whose limit was hit. This prevents the tenant admin from mistakenly thinking the whole tenant is blocked.

## 5. Observability: Metrics, Logs, and Alerts

Rate limiting is not a set-and-forget configuration. You must measure whether limits are protecting reliability without blocking legitimate traffic.

### Key Metrics (monitored per tenant, per client-id, per endpoint)

- **`rate_limit.exceeded`** (counter): 429 responses returned. Track by tenant tier (enterprise vs. small team) and by client-id.
- **`rate_limit.remaining`** (gauge): current remaining tokens or window count. Low values signal approaching thresholds.
- **`rate_limit.dropped_requests_percent`** (derived): percentage of requests from a tenant that result in 429. If >5%, investigate tenant integration.
- **`request_latency.p99`** before and after rate limiting: unexpected latency increases under throttling indicate implementation issues.
- **`active_buckets`** (gauge): number of tenants or client-ids currently tracked. This helps estimate memory consumption.

### Logging

- Log every 429, including `client_id`, `tenant_id`, `endpoint`, and `current_limit`.
- Sample *allow* logs at low rate (e.g., 1:1000) to verify rate limit correctness without overwhelming log storage.
- For token bucket: log when bucket is empty (throttle) and when it recovers (to detect flapping).

### Alerts

- **High 429 rate for a single client-id** (>50% of its requests, sustained for 5 minutes): likely a misconfigured integration. Notify the tenant admin (via webhook) rather than paging ops.
- **High global 429 rate** (>10% of total API traffic): the system is under-provisioned or a DDoS-like pattern is occurring. Page operations.
- **Rate limit latency increase**: if rate limit checks themselves take >10ms, the algorithm or storage layer is bottlenecked—investigate before it cascades.
- **Tenant-wide throttling**: if any tenant hits its per-tenant limit, investigate whether a single client-id is leaking across tenants (e.g., shared API key).

## 6. Recommended Baseline Design

Start with this minimal, scalable architecture:

1. **Algorithms**: Token bucket for per-client-id limits (100 tokens initial burst, 50 tokens/sec refill). Sliding window counter for per-tenant limits (10,000 requests/min). Both stored in a distributed, low-latency cache (e.g., Redis Cluster or Memcached) with TTL-based eviction.
2. **Hierarchy**: Three levels: *global* → *per-tenant* → *per-client-id*. Each client-id bucket is checked first. If it passes, decrement the tenant bucket. Never overload a single key; use separate keys per scope.
3. **Headers**: Always return `X-RateLimit-Limit`, `Remaining`, `Reset`. On 429, include `Retry-After` and a JSON Problem response with `scope`.
4. **Defaults**: Small teams: 50 req/min per client-id, 500 req/min per tenant. Enterprise: configurable up to 5,000 req/min per client-id (with higher cost). All tenants can burst to 2× sustained for 10 seconds maximum.
5. **Overrides**: Allow tenant admins to set per-client-id limits via API (within enterprise plan maximums). Store overrides in the same cache with higher TTL.
6. **Observability**: Export metrics (counter, gauge) every 10 seconds. Log 429s and sample allowable requests at 1:100. Alert on per-client-id flapping >50% or global >10%.

This design prevents one misconfigured integration from silencing an entire team, gives clients clear signals to self-correct, and provides enough observability to tune limits as your customer base grows.
````
