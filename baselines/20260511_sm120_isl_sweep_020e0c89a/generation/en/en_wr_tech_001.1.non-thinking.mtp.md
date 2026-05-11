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
- Elapsed seconds: 15.606637
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2332, "completion_tokens": 2180, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2180
- Total tokens: 2332

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
# Throttling with Finesse: Designing Multi-Tenant Rate Limiting for Teams and Enterprises

Rate limiting is one of those infrastructure concerns that sounds simple—count requests, reject excess—until you try to do it fairly across a hundred tenants, each containing five or five hundred integrations. Get it wrong and you either degrade reliability for everyone or frustrate legitimate users into churning.

This article assumes you already understand HTTP and distributed systems. We’ll focus on the decisions that matter when your API serves both a three-person startup and a Fortune 500 division running automated pipelines.

---

## 1. Fundamental Distinctions: Auth, Authz, Quotas, and Rate Limits

Engineers often conflate these four concepts. They serve different purposes and should be enforced at different layers.

**Authentication** answers *who you are*. An API key or JWT proves identity. This is the outermost gate: without it, nothing else applies.

**Authorization** answers *what you’re allowed to do*. It checks resource-level permissions—tenant admin vs. read-only user, or access to a specific endpoint.

**Quotas** are *cumulative, long-term limits*. “Your team can make 100,000 requests this month.” Quotas reset on a billing cycle, not per second. They protect business models and prevent runaway usage from surprising you or the customer.

**Rate limits** are *short-term, burst-oriented controls*. “Your integration can send 10 requests per second.” They protect infrastructure from traffic spikes and misbehaving clients.

Simplified: quotas guard the contract; rate limits guard the server. Enforce rate limits in middleware after auth but before authorization. Enforce quotas at a separate, stateless service called before writing to your database.

---

## 2. Algorithm Selection: Token Bucket, Fixed Window, Sliding Window

Each algorithm makes different trade-offs between accuracy, memory, and fairness.

### Fixed Window
Divide time into discrete intervals (e.g., one second). Each window has a counter. If the counter exceeds the limit, reject until the next window.

**Practical problem**: At the boundary between windows, a burst can double the allowed rate. A client sending 10 requests at the last millisecond of window N and another 10 at the first millisecond of window N+1 effectively sends 20 requests in two milliseconds—hardly a rate limit. This is called the *boundary burst* issue.

**Good for**: Simplicity. Use only when a small burst is acceptable (e.g., non-critical endpoints).

### Sliding Window Log
Keep a timestamped log of every request within the window (e.g., last 60 seconds). Count requests by scanning the list.

**Practical problem**: Memory and time complexity. A high-throughput tenant generating 1,000 req/s requires storing 60,000 timestamps per tenant. Scan overhead kills performance.

**Good for**: Prototyping. Never use in production for multi-tenant systems.

### Sliding Window Counter
Divide the window into smaller sub-windows (e.g., 1-second buckets for a 60-second window). Count requests per bucket. To get the current count, sum the current incomplete bucket plus the appropriate fraction from the previous bucket.

**Practical trade-off**: Approximates sliding window accuracy with O(1) memory per tenant. The boundary between buckets introduces minor inaccuracy (~10–15%), but that’s generally acceptable for API rate limiting.

### Token Bucket
Refill tokens at a steady rate (e.g., 100 tokens per second) up to a burst capacity (e.g., 200). Each request consumes one token. If no tokens remain, reject.

**Why it wins for multi-tenant**: Token buckets naturally allow short bursts up to the capacity limit, then smooth out. A tenant with a spikey integration (e.g., a webhook handler that fires 50 events in one second) gets the burst, then must wait for refill. This aligns with real-world traffic patterns.

**Practical recommendation**: Use token bucket as your default. It’s memory-efficient (one counter + one timestamp per bucket), handles bursts gracefully, and is easy to reason about.

---

## 3. Protecting Tenants from Their Own Noise

A single noisy integration—a misconfigured polling loop, a buggy webhook client—can consume an entire tenant’s rate limit, starving their other integrations. The naive solution (a single bucket per tenant) punishes that tenant’s legitimate traffic.

**Strategy: hierarchical buckets.** Allocate a parent bucket at the tenant level (e.g., 500 req/s). Under that, each integration key or API token gets its own child bucket (e.g., 100 req/s). Enforce both: a request must pass the child bucket *and* the parent bucket.

When a noisy integration drains its child bucket, it gets rejected, but the tenant bucket still has capacity for other integrations. The parent bucket becomes the ceiling for aggregate traffic.

**Isolate by endpoint sensitivity**. Authenticated, read-heavy endpoints (GET /items) can have higher limits than write-heavy or expensive ones (POST /transactions). This prevents one slow endpoint from degrading the entire tenant’s experience.

**Queue vs. reject**: For enterprise customers with SLA guarantees, consider a short (1–5 second) in-memory queue per tenant that drains slowly. Reject only if the queue overflows. This absorbs transient bursts without rejecting a single request.

---

## 4. Headers and Error Messages That Clients Can Actually Use

Your rate limiting is only as good as the feedback you give clients. Silent drops create angry customers.

**Required response headers** (on every response, not just rejects):

- `X-RateLimit-Limit`: The maximum requests allowed per window (e.g., 100).
- `X-RateLimit-Remaining`: How many requests remain in the current window.
- `X-RateLimit-Reset`: Unix timestamp (or ISO 8601) when the current window/bucket resets.
- `Retry-After`: Seconds the client should wait before retrying. Include on 429 responses.

**Error response body** (for 429 Too Many Requests):

```json
{
  "error": "rate_limit_exceeded",
  "message": "You have exceeded the allowed request rate. Please retry after the specified time.",
  "retry_after_seconds": 15,
  "limit": 100,
  "remaining": 0,
  "reset_at": "2025-04-10T14:32:00Z"
}
```

Avoid cryptic codes like “ERR_429_01.” Use machine-readable error types so clients can parse and handle programmatically. Include the scope (tenant, integration, endpoint) in the message so the client knows what limit they hit.

**When to return 429 vs. 503**: 429 is explicit—the client triggered a rate limit. 503 means the server is overloaded, which is a different failure mode. Never conflate them.

---

## 5. Observability: Metrics That Tell the Real Story

Rate limiting creates a tension: reject too many requests and customers complain; reject too few and the database melts. Observability must reveal where you stand on that spectrum.

**Essential metrics** (per tenant, per endpoint, per integration key):

- **Requests total**: raw throughput.
- **Requests rate-limited**: count of 429 responses. Track both absolute number and as a fraction of total.
- **Bucket exhaustion rate**: how often each bucket empties. Low exhaustion means limits are generous; high means tenants are hitting ceilings.
- **Latency impact**: measure p50/p99 latency before and after rate limiting middleware. A slow rate limiter can itself become a bottleneck.
- **Burst peak**: the maximum number of requests within a 1-second window per tenant. Compare to the configured limit. If burst peaks are consistently 10x the limit, your limiter may be misconfigured or bypassed.

**Logs**: Log every rate limit action (allow + deny) with tenant ID, integration key, endpoint, and the bucket state (tokens available, limit). Sampling at 1:10 is acceptable for high-traffic endpoints, but never sample denials—every rejected request is a potential support ticket.

**Alerts**: Set three tiers of alerting.

1. **Warning**: Any tenant exceeds 80% of their rate limit for a sustained five-minute window. This suggests they may need an upgrade or are misconfiguring their client.
2. **Critical**: Rate-limited requests exceed 5% of total traffic for any tenant for more than 10 minutes. Something is broken—either a noisy integration or our limits are too tight.
3. **Pager**: Global rate-limited requests exceed 20% of total traffic. This indicates a systemic problem: a DDoS attack, a global misconfiguration, or an upstream service failing.

**Push to prometheus-compatible storage** (counters for requests, histograms for latency). Pull into dashboards that show, per tenant, the relationship between their throughput, their limit, and how many requests we reject.

---

## Recommended Baseline Design

For a new multi-tenant API supporting small teams and enterprises:

1. **Algorithm**: Token bucket with hierarchical structure. Each tenant gets a parent bucket (burst = 2x sustained). Each integration key gets a child bucket (burst = 1.5x sustained). Enforce child first, then parent.

2. **Granularity**: Tenant-level limits derived from their plan. Integration-level limits set to 20% of the tenant limit, ensuring no single integration can monopolize the tenant’s capacity.

3. **Headers**: Include `X-RateLimit-*` on every response. Use `Retry-After` on 429s. Return JSON error bodies with `error` type and `retry_after_seconds`.

4. **Observability**: Log every deny, sample allows at 1:10. Track requests total, rate-limited count, and bucket exhaustion rate per tenant and integration. Alert when denials exceed 5% of tenant traffic.

5. **Queue for enterprises**: For tenants on premium plans, insert a short (2-second) in-memory queue after the rate limiter. If the queue overflows, reject with 429. This absorbs bursts while keeping latency predictable.

Start with this baseline, then iterate based on real traffic patterns. The goal isn’t perfection on day one—it’s a system that lets you detect and fix unfairness before your customers do.
````
