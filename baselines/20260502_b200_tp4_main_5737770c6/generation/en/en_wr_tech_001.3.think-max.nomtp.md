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
- Variant: `nomtp`
- OK: `True`
- Status: PASS
- Check: matched expectation
- Detail: `matched expectation`
- Elapsed seconds: 15.49782
- Finish reason: `stop`
- Usage: `{"prompt_tokens": 152, "total_tokens": 2335, "completion_tokens": 2183, "prompt_tokens_details": null}`
- Prompt tokens: 152
- Completion tokens: 2183
- Total tokens: 2335

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
# Designing Rate Limiting for a Multi-Tenant API: Serving Small Teams and Enterprise Customers

## Introduction

Multi-tenant APIs present a unique challenge: your small teams might burst to 100 requests per minute during a hackathon, while your enterprise customers run steady state at 5,000 QPS across dozens of integrations. Poorly designed rate limiting can either block legitimate use or fail to protect the shared infrastructure. This article covers the core concepts, practical algorithm choices, tenant isolation strategies, client feedback mechanisms, and observability patterns for building a rate limiting system that scales across tenant sizes.

## 1. Authentication vs. Authorization vs. Quotas vs. Rate Limits

These four concepts are frequently conflated but serve distinct purposes.

**Authentication** answers "Who are you?" – verifying identity via API keys, OAuth tokens, or mTLS. It must happen before any other check.

**Authorization** answers "What are you allowed to do?" – controlling access to specific endpoints, resources, or operations (e.g., "Can this team create billing invoices?"). Authorization is often resource-specific.

**Quotas** are long-term, hard caps on resource consumption over a billing period – e.g., "10,000 API calls per month" or "50 GB of storage." Quotas enforce business agreements and are typically reset monthly or on plan upgrade.

**Rate limits** are short-term, granular controls that protect system capacity – e.g., "100 requests per second per tenant." They prevent a single tenant from degrading service for others, regardless of their quota balance.

Key distinction: A tenant can have remaining quota (allowed 10,000 calls this month) but still be rate limited (exceeded 100 req/s). Rate limits are about *burst* protection; quotas are about *cumulative* usage enforcement.

## 2. Token Bucket vs. Fixed Window vs. Sliding Window

All three algorithms can work, but their practical behaviors differ significantly.

**Fixed Window** divides time into discrete buckets (e.g., 1-minute windows). A tenant can make up to `N` requests per window. Problem: at the window boundary, two adjacent windows can each see full bursts, allowing a 2× spike in a very short interval. Example: a tenant sends 100 requests at 1:59.999 and another 100 at 2:00.000 – that's 200 requests in 200 milliseconds, defeating the purpose.

**Sliding Window** (log or counter-based) considers a rolling time frame. Each incoming request resets the window end. A common implementation uses a log of timestamps or a counter with weighted decay. This eliminates the boundary burst issue but requires more memory (full timestamp log for each tenant) or the complexity of the "sliding window counter" hybrid (track current and previous window counters with weight interpolation). Practical for most APIs but overhead scales with tenant count.

**Token Bucket** maintains a bucket of `N` tokens that refills at rate `R` per second. Each request consumes one token. Spare tokens accumulate up to bucket capacity. This naturally allows bursting (a tenant that was idle can burst up to capacity) while enforcing a sustainable average rate. The refill rate makes it smooth and predictable.

**Recommendation for multi-tenant**: Token bucket is best. It handles bursts gracefully (idle tenants can catch up quickly), prevents sustained abuse (refill enforces average rate), and has low memory footprint – a single counter per tenant plus a timestamp of last refill. Fixed window is too dangerous for shared infrastructure. Sliding window works but adds complexity without practical benefit over token bucket for most use cases.

## 3. Isolating Tenants and Noisy Integrations

The worst-case scenario: an enterprise tenant has one chatty integration that spikes to 10,000 req/s, while their other (critical) integrations operate normally. A naive per-tenant rate limit would block *all* traffic for that tenant, punishing their legitimate use.

**Solution: Sub-tenant rate limits.** Implement a two-level hierarchy:

- **Global tenant limit**: e.g., 5,000 req/s for an enterprise plan.
- **Per-API-key or per-integration limit**: e.g., 500 req/s per key within that tenant.

A single noisy integration hits its own key limit, while other keys continue working. This requires rate limiters to operate at the API key (or client credential) level, not just at the customer account level.

**Isolation design pattern**:
- Each API key has a dedicated token bucket.
- A parent bucket (tenant-level) acts as a circuit breaker: if the tenant's aggregate exceeds, say, 8,000 req/s (a generous buffer above the global limit), the parent bucket starts rejecting *new* requests from any key, but only briefly. The child buckets try first; if denied, the parent check is skipped for that request to avoid double accounting.
- Introduce a "latency injection" tier: when a key approaches 80% of its limit, add 50ms delay to responses. This slows down noisy integrations naturally, often fixing burst problems before hard blocking is needed.

This approach ensures that one misconfigured CI/CD pipeline or a rogue script doesn't bring down an entire enterprise customer's operations.

## 4. Client Feedback: Headers and Error Messages

Transparency is critical. Clients must understand *why* they are being limited and *when* they can retry. Standard practice uses these HTTP response headers on every API response (success or error):

- `X-RateLimit-Limit`: The maximum requests allowed per window (e.g., 100).
- `X-RateLimit-Remaining`: The number of requests remaining in the current window (e.g., 42).
- `X-RateLimit-Reset`: Unix timestamp (seconds since epoch) when the limit resets (for token bucket, when the bucket will be full again if idle).

For multi-key setups, include:
- `X-RateLimit-Scope`: Indicates if this limit applies to `api-key`, `tenant`, or `global`. Helps debugging.

**Error codes**:
- Use HTTP 429 Too Many Requests.
- Return a JSON body with:
  - `error.type`: `"rate_limit_exceeded"`
  - `error.detail`: `"API key limit exceeded. Retry after the time specified in Retry-After header."`
  - `error.scope`: `"api_key"`
- Include `Retry-After` header with integer seconds to wait.

Never return 401 or 403 for rate limiting – those imply authentication or authorization issues.

## 5. Observability: Metrics, Logs, and Alerts

You need to know if rate limiting is working as intended, not just that it is firing.

**Metrics to collect per tenant and per endpoint**:
- **Requests allowed vs. blocked** – basic health indicator.
- **Rate limit hit ratio** (blocked / total). Spikes indicate noisy tenants.
- **Token bucket fill level** (as percentile across tenants). If many tenants hover near empty, your limits may be too tight.
- **Latency distribution** – compare p50, p99 latency for requests that pass vs. requests that get delayed. If passing requests show latency spikes, rate limiting might be causing thundering herds.
- **Time-to-reset** distribution – how long are throttled clients waiting? Most should wait <1 second; many waiting 30+ seconds suggests limits too restrictive.

**Logs** (structured, high-cardinality):
- Log every 429 response with: `tenant_id`, `api_key_id`, `endpoint`, `limit_name`, `reset_at`, `retry_after`.
- Log every throttling event (delayed request) with similar context.

**Alerts**:
- **P0**: Rate limit hit ratio > 5% overall for more than 5 minutes. This indicates a systemic issue – maybe your limits are too low for legitimate traffic.
- **P1**: A single tenant's hit ratio exceeds 20% – possible misconfigured integration or abuse.
- **P2**: Token bucket fill level for >5% of tenants stays below 10% for 1 hour – your limit may be too tight for normal usage patterns.
- **P3**: Rate limit error count > 100/min from a single API key – likely a noisy integration; alert the tenant's support contact.

Monitor *false positives*: if rate limit hits spike but system load is low, your algorithm is too aggressive. Correlate limit hits with downstream database/API latency – if blocking a request coincides with a high db latency, the limiter is doing its job; if blocking happens while db is idle, adjust.

## 6. Recommended Baseline Design

For a new multi-tenant API serving both small teams and enterprise customers:

**Algorithm**: Token bucket per API key (child bucket) + token bucket per tenant (parent bucket with 1.5× the key limit). Use a sliding window cache (e.g., Redis sorted sets or a simple in-memory map) for bucket state, with TTL equal to the bucket refill period.

**Limits per plan**:
- Small team: 500 req/min per key, 2 keys per tenant → 1,000 req/min tenant aggregate.
- Enterprise: 5,000 req/s per key (with burst up to 10,000 for 5 seconds), unlimited keys, tenant aggregate at 15,000 req/s.

**Throttling strategy**: At 80% of key limit, add 100ms latency per request. At 100%, return 429 with a 1-second retry-after. The parent circuit breaker kicks in at 90% of tenant aggregate, returning 429 with a 5-second retry and including `scope: tenant` in the error.

**Headers**: Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `X-RateLimit-Scope` on every response.

**Observability**: Log all 429s. Emit the metrics described – specifically hit ratio and bucket fill level. Alert when overall hit ratio exceeds 3% or when any single tenant exceeds 15%. Review limits monthly using p99 latency graphs and bucket fill percentile charts.

This design gives small teams room to burst during coding sessions, protects enterprise customers from their own noisy integrations, and keeps your infrastructure safe from abuse – all without vendor lock-in or overcomplicated code.
```
